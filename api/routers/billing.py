"""Billing router — Stripe integration + credit/plan endpoints.

All Stripe keys are read from environment variables only. Never stored in DB or app config.

Required env vars:
  STRIPE_SECRET_KEY
  STRIPE_WEBHOOK_SECRET
  STRIPE_PRICE_STARTER
  STRIPE_PRICE_PRO
  STRIPE_PRICE_MAX
  STRIPE_PRICE_TOPUP      (one-time price for the $4.99 / 250-credit pack)

Optional:
  FRONTEND_URL            (used for Stripe success/cancel redirect URLs, default http://localhost:3000)
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

import stripe
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..billing.ledger import expire_grant, get_balance, grant, write_usage_event
from ..billing.subscriptions import get_or_create_subscription
from ..database import SessionLocal, get_db
from ..models import Plan, ProcessedWebhook, RateWindow, Subscription, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/billing", tags=["Billing"])

TOPUP_CREDITS = 250  # credits granted per top-up purchase
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _stripe_client() -> stripe.stripe_object.StripeObject:
    """Return configured stripe module. Raises 503 if key is missing."""
    key = os.getenv("STRIPE_SECRET_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="Stripe not configured on this server.")
    stripe.api_key = key
    return stripe


# ── Response models ───────────────────────────────────────────────────────────

class PlanOut(BaseModel):
    code: str
    name: str
    price_cents: int
    monthly_credits: int
    daily_caps: dict
    weekly_caps: dict | None

    class Config:
        from_attributes = True


class BillingStatusOut(BaseModel):
    plan_code: str
    plan_name: str
    status: str
    balance: int
    period_end: datetime | None
    daily_caps: dict
    weekly_caps: dict | None
    monthly_credits: int


class CheckoutRequest(BaseModel):
    plan_code: str  # starter | pro | power


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/plans")
async def list_plans(db: Session = Depends(get_db)) -> list[PlanOut]:
    """Public plan catalogue for the pricing page."""
    plans = db.query(Plan).order_by(Plan.price_cents).all()
    return [
        PlanOut(
            code=p.code,
            name=p.name,
            price_cents=p.price_cents,
            monthly_credits=p.monthly_credits,
            daily_caps=p.daily_caps,
            weekly_caps=p.weekly_caps,
        )
        for p in plans
    ]


@router.get("/me", response_model=BillingStatusOut)
async def billing_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's current plan, balance, and usage caps."""
    sub = get_or_create_subscription(db, current_user.id)
    plan = sub.plan
    balance = get_balance(db, current_user.id)
    return BillingStatusOut(
        plan_code=plan.code,
        plan_name=plan.name,
        status=sub.status,
        balance=balance,
        period_end=sub.current_period_end,
        daily_caps=plan.daily_caps,
        weekly_caps=plan.weekly_caps,
        monthly_credits=plan.monthly_credits,
    )


@router.get("/usage")
async def usage_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's last 50 UsageEvents (for the dashboard)."""
    from ..models import UsageEvent
    events = (
        db.query(UsageEvent)
        .filter(UsageEvent.user_id == current_user.id)
        .order_by(UsageEvent.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": e.id,
            "task_type": e.task_type,
            "provider": e.provider,
            "model": e.model,
            "input_tokens": e.input_tokens,
            "output_tokens": e.output_tokens,
            "raw_cost_usd": e.raw_cost_usd,
            "credits_charged": e.credits_charged,
            "failed": e.failed,
            "created_at": e.created_at,
        }
        for e in events
    ]


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a Stripe Checkout Session for a paid plan. Returns {url}."""
    _stripe = _stripe_client()

    price_env_map = {
        "starter": "STRIPE_PRICE_STARTER",
        "pro": "STRIPE_PRICE_PRO",
        "max": "STRIPE_PRICE_MAX",
    }
    env_key = price_env_map.get(body.plan_code)
    if not env_key:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {body.plan_code}")

    price_id = os.getenv(env_key)
    if not price_id:
        raise HTTPException(status_code=503, detail=f"Stripe price not configured for {body.plan_code}.")

    sub = get_or_create_subscription(db, current_user.id)

    # ── Plan SWITCH path ──────────────────────────────────────────────────────
    # If the user already has an active Stripe subscription, DO NOT create a new
    # Checkout (that would create a SECOND subscription and double-bill). Instead
    # modify the existing subscription's price in place. Stripe prorates the
    # difference and fires `customer.subscription.updated`, which the webhook
    # handler (_handle_subscription_updated) uses to update the plan + grant the
    # credit delta.
    if sub.stripe_subscription_id and sub.status in ("active", "trialing"):
        try:
            stripe_sub = _stripe.Subscription.retrieve(sub.stripe_subscription_id)
            current_item = stripe_sub["items"]["data"][0]
            # Already on this price? Nothing to do.
            if current_item["price"]["id"] == price_id:
                return {"url": f"{FRONTEND_URL}/billing"}
            _stripe.Subscription.modify(
                sub.stripe_subscription_id,
                items=[{"id": current_item["id"], "price": price_id}],
                proration_behavior="create_prorations",
                metadata={"user_id": current_user.id},
            )
            # No redirect to Stripe needed — change is applied immediately.
            return {"url": f"{FRONTEND_URL}/billing?success=1"}
        except Exception:
            # If the stored subscription is stale/invalid in Stripe, fall through
            # to a fresh Checkout below rather than failing the request.
            pass

    # ── First-time purchase path ──────────────────────────────────────────────
    # Reuse existing Stripe customer if we already have one.
    customer_id = sub.stripe_customer_id or None

    session = _stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        customer_email=current_user.email if not customer_id else None,
        line_items=[{"price": price_id, "quantity": 1}],
        metadata={"user_id": current_user.id},
        success_url=f"{FRONTEND_URL}/billing?success=1",
        cancel_url=f"{FRONTEND_URL}/billing?canceled=1",
    )
    return {"url": session.url}


@router.post("/portal")
async def create_portal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Customer Portal session so the user can manage/cancel. Returns {url}."""
    _stripe = _stripe_client()

    sub = get_or_create_subscription(db, current_user.id)
    if not sub.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="No Stripe customer found. Subscribe to a paid plan first.",
        )

    portal = _stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=f"{FRONTEND_URL}/billing",
    )
    return {"url": portal.url}


@router.post("/topup")
async def create_topup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a Stripe Checkout Session for a one-time 250-credit top-up ($5). Returns {url}."""
    _stripe = _stripe_client()

    price_id = os.getenv("STRIPE_PRICE_TOPUP")
    if not price_id:
        raise HTTPException(status_code=503, detail="Top-up price not configured.")

    sub = get_or_create_subscription(db, current_user.id)
    customer_id = sub.stripe_customer_id or None

    session = _stripe.checkout.Session.create(
        mode="payment",
        customer=customer_id,
        customer_email=current_user.email if not customer_id else None,
        line_items=[{"price": price_id, "quantity": 1}],
        metadata={"user_id": current_user.id, "topup": "1"},
        success_url=f"{FRONTEND_URL}/billing?topup=success",
        cancel_url=f"{FRONTEND_URL}/billing",
    )
    return {"url": session.url}


# ── Webhook ───────────────────────────────────────────────────────────────────

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Stripe events — the source of truth for all subscription/credit state.

    Verified with STRIPE_WEBHOOK_SECRET. Idempotent: events already in
    processed_webhooks are silently ACKed.
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured.")

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.")

    event_id = event["id"]

    # Idempotency: skip already-processed events.
    existing = db.query(ProcessedWebhook).filter(
        ProcessedWebhook.stripe_event_id == event_id
    ).first()
    if existing:
        return {"status": "already_processed"}

    # Insert first so concurrent replays don't double-process.
    db.add(ProcessedWebhook(stripe_event_id=event_id))
    try:
        db.commit()
    except Exception:
        # Unique constraint violation — another worker beat us here.
        db.rollback()
        return {"status": "already_processed"}

    event_type = event["type"]
    data = event["data"]["object"]

    try:
        if event_type == "checkout.session.completed":
            _handle_checkout_completed(db, data)
        elif event_type == "invoice.paid":
            _handle_invoice_paid(db, data)
        elif event_type == "customer.subscription.updated":
            _handle_subscription_updated(db, data)
        elif event_type == "invoice.payment_failed":
            _handle_payment_failed(db, data)
        elif event_type == "customer.subscription.deleted":
            _handle_subscription_deleted(db, data)
        # All other event types: return 200 and do nothing.
    except Exception:
        logger.exception("Error handling Stripe event %s (%s)", event_id, event_type)
        # Do NOT raise — return 200 so Stripe doesn't retry indefinitely.
        # The event_id is already marked processed; investigate via Stripe dashboard.

    return {"status": "ok"}


# ── Webhook handlers ──────────────────────────────────────────────────────────

def _find_user_by_stripe_customer(db: Session, customer_id: str) -> Subscription | None:
    return db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()


def _find_user_id_from_metadata(data: dict) -> str | None:
    return (data.get("metadata") or {}).get("user_id")


def _extract_subscription_id(data: dict) -> str | None:
    """Extract subscription ID from a Stripe object.

    Stripe API 2026-05-27.dahlia moved the subscription reference on invoices
    from the top-level `subscription` field to
    `parent.subscription_details.subscription`. We try both locations so the
    code works across API versions.
    """
    # Old location (pre-2026 API versions)
    sub_id = data.get("subscription")
    if sub_id:
        return sub_id
    # New location (2026-05-27.dahlia+)
    parent = data.get("parent") or {}
    sub_details = parent.get("subscription_details") or {}
    return sub_details.get("subscription")


def _handle_checkout_completed(db: Session, data: dict) -> None:
    user_id = _find_user_id_from_metadata(data)
    if not user_id:
        logger.warning("checkout.session.completed: no user_id in metadata — skipping")
        return

    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        logger.warning("checkout.session.completed: no subscription row for user %s", user_id)
        return

    customer_id = data.get("customer")
    if customer_id:
        sub.stripe_customer_id = customer_id

    # One-time top-up (mode=payment, topup=1 in metadata).
    if data.get("metadata", {}).get("topup") == "1":
        session_id = data.get("id", "")
        topup_ref = f"topup:{session_id}"
        grant(db, user_id, TOPUP_CREDITS, ref=topup_ref, kind="topup")
        db.commit()
        return

    # Subscription checkout — store the Stripe subscription id + customer id.
    stripe_sub_id = _extract_subscription_id(data)
    if stripe_sub_id:
        sub.stripe_subscription_id = stripe_sub_id
    sub.status = "active"
    db.commit()
    # Credits are granted on the subsequent invoice.paid event.


def _handle_invoice_paid(db: Session, data: dict) -> None:
    """Stripe fires this on every successful charge — initial and renewal."""
    from ..models import User as UserModel

    customer_id = data.get("customer")
    stripe_sub_id = _extract_subscription_id(data)

    # 1. Primary: look up by stripe_customer_id.
    sub = _find_user_by_stripe_customer(db, customer_id) if customer_id else None

    # 2. Fallback: by stripe_subscription_id.
    if not sub and stripe_sub_id:
        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()

    # 3. Fallback: by customer_email on the invoice → User.email → Subscription.
    #    This handles the race condition where neither ID has been stored yet.
    if not sub:
        customer_email = data.get("customer_email")
        if customer_email:
            user = db.query(UserModel).filter(
                UserModel.email == customer_email,
                UserModel.is_deleted == False,
            ).first()
            if user:
                sub = db.query(Subscription).filter(
                    Subscription.user_id == user.id
                ).first()

    if not sub:
        logger.warning(
            "invoice.paid: no subscription found for customer=%s sub=%s email=%s",
            customer_id, stripe_sub_id, data.get("customer_email"),
        )
        return

    # Backfill IDs for future lookups.
    if customer_id and not sub.stripe_customer_id:
        sub.stripe_customer_id = customer_id
    if stripe_sub_id and not sub.stripe_subscription_id:
        sub.stripe_subscription_id = stripe_sub_id

    invoice_id = data.get("id", "")
    user_id = sub.user_id

    # Resolve and update plan from the invoice line items.
    plan = _resolve_plan_from_invoice(db, data)
    if plan:
        sub.plan_id = plan.id

    # Expire unused grant from the previous period (top-ups are preserved).
    expire_ref = f"expire:{user_id}:{invoice_id}"
    expire_grant(db, user_id, ref=expire_ref)

    # Grant this month's credits.
    grant_ref = f"grant:{invoice_id}"
    current_plan = plan or db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if current_plan:
        grant(db, user_id, current_plan.monthly_credits, ref=grant_ref, kind="grant")

    # Update subscription period from invoice.
    period_start = data.get("period_start")
    period_end = data.get("period_end")
    if period_start:
        sub.current_period_start = datetime.utcfromtimestamp(period_start)
    if period_end:
        sub.current_period_end = datetime.utcfromtimestamp(period_end)

    sub.status = "active"
    db.commit()


def _handle_subscription_updated(db: Session, data: dict) -> None:
    stripe_sub_id = data.get("id")
    if not stripe_sub_id:
        return

    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub_id
    ).first()
    if not sub:
        return

    new_plan = _resolve_plan_from_subscription(db, data)
    if new_plan and new_plan.id != sub.plan_id:
        # Plan upgrade: grant the credit delta immediately.
        old_plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
        if old_plan:
            delta = new_plan.monthly_credits - old_plan.monthly_credits
            if delta > 0:
                upgrade_ref = f"upgrade:{stripe_sub_id}:{datetime.utcnow():%Y-%m}"
                grant(db, sub.user_id, delta, ref=upgrade_ref, kind="grant")
        sub.plan_id = new_plan.id

    new_status = data.get("status")
    if new_status:
        sub.status = new_status

    db.commit()


def _handle_payment_failed(db: Session, data: dict) -> None:
    customer_id = data.get("customer")
    if not customer_id:
        return
    sub = _find_user_by_stripe_customer(db, customer_id)
    if sub:
        sub.status = "past_due"
        db.commit()


def _handle_subscription_deleted(db: Session, data: dict) -> None:
    """Stripe fires this when a subscription is fully canceled.
    Downgrade to Free at (or after) the period end.
    """
    stripe_sub_id = data.get("id")
    if not stripe_sub_id:
        return
    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub_id
    ).first()
    if not sub:
        return

    free_plan = db.query(Plan).filter(Plan.code == "free").first()
    if free_plan:
        sub.plan_id = free_plan.id
    sub.status = "canceled"
    sub.stripe_subscription_id = None
    db.commit()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_price_id(obj: dict) -> str | None:
    """Extract a price ID from a line item or subscription item.

    Stripe API 2026-05-27.dahlia moved the price reference on line items from
    `line.price.id` to `line.pricing.price_details.price`. We try both so the
    code works across API versions.
    """
    # Old location: line.price.id
    price_id = (obj.get("price") or {}).get("id")
    if price_id:
        return price_id
    # New location: line.pricing.price_details.price
    pricing = obj.get("pricing") or {}
    price_details = pricing.get("price_details") or {}
    return price_details.get("price")


def _resolve_plan_from_invoice(db: Session, invoice_data: dict) -> Plan | None:
    """Extract the Stripe price ID from invoice line items and match to a Plan row."""
    lines = (invoice_data.get("lines") or {}).get("data") or []
    for line in lines:
        price_id = _extract_price_id(line)
        if price_id:
            plan = db.query(Plan).filter(Plan.stripe_price_id == price_id).first()
            if plan:
                return plan
    return None


def _resolve_plan_from_subscription(db: Session, sub_data: dict) -> Plan | None:
    """Extract the Stripe price ID from subscription items and match to a Plan row."""
    items = (sub_data.get("items") or {}).get("data") or []
    for item in items:
        price_id = _extract_price_id(item)
        if price_id:
            plan = db.query(Plan).filter(Plan.stripe_price_id == price_id).first()
            if plan:
                return plan
    return None
