# Plan: Remove Payments → Move to BYOK (Bring Your Own Key)

**Audience:** engineering
**Goal:** Strip out all monetization (Stripe, plans, credits, per-plan LLM limits) and replace the LLM layer with a **Bring-Your-Own-Key** model that supports **Gemini, Grok (xAI), DeepSeek, ChatGPT (OpenAI), and Anthropic**, with per-task model selection and a one-click "Recommended setup."
**Keep:** token/usage **tracking** (the `UsageEvent` table + `UsageCollector`). We stop *charging* and *gating*, but we keep *measuring*.

Everything is in git, so removal is safe and reversible. Do this in **three independent, shippable PRs** in the order below.

---

## TL;DR sequencing

| PR | Scope | Risk | Depends on |
|----|-------|------|-----------|
| **PR-A** | Delete `/contact` + `/refunds` pages, landing pricing, footer links | trivial | — |
| **PR-B** | Add BYOK foundation: new provider clients, encrypted key storage, per-user resolver, settings UI, "Recommended setup". Keep server-key fallback so nothing breaks yet. | medium | — |
| **PR-C** | Remove Stripe + plans + credits + rate limits; flip LLM resolution to BYOK-only; gut the gateway down to usage logging | medium | PR-B |

Ship PR-B fully working (with server keys still as fallback) **before** PR-C removes the safety net.

---

## Current architecture (what we're changing)

**Backend**
- `engine/providers.py` — only two clients exist: `XAIClient`, `DeepSeekClient`. Both implement `.complete(response_model, messages, …)` and attach a `collector`.
- `api/llm.py` — `get_llm(task, collector)` resolves provider/model from server-side `api/llm_config.json` and reads API keys from **server env vars**.
- `api/billing/` — `gateway.py` (the `metered()` FastAPI dependency + `MeterContext`), `ledger.py` (credit reserve/refund/grant + `write_usage_event`), `limits.py` (multi-window rate limiter), `subscriptions.py` (free-plan lazy reset).
- `api/routers/billing.py` (782 lines) — Stripe checkout/portal/topup/webhook + plan listing + usage history.
- Billing tables in `api/models.py`: `Plan`, `Subscription`, `CreditLedger`, `UsageEvent`, `RateWindow`, `ProcessedWebhook`.
- `api/database.py` — `seed_plans()`, `backfill_subscriptions()`, `PLAN_SEED`.
- `api/main.py` — includes `billing_router`, calls `seed_plans`, `backfill_subscriptions`, `sweep_orphaned_reservations`.
- `requirements.txt` — `stripe==15.2.0`.

**How a metered task flows today (keep the shape, change the internals):**
```
endpoint depends on metered("cover_letter")
  → MeterContext{collector, credits_reserved, ...}
  → llm = get_llm("cover_letter", collector=ctx.collector)
  → work...
  → ctx.settle_success()  # writes UsageEvent
```
Background tasks (`api/routers/jobs.py`) call `get_llm(...)` + `bg_settle_success/failure` directly inside the bg function using a fresh DB session.

**Frontend touchpoints**
- `frontend/src/app/billing/page.tsx`, `frontend/src/app/contact/page.tsx`, `frontend/src/app/refunds/page.tsx`
- `frontend/src/components/landing/PricingSection.tsx`, `LandingFooter.tsx`
- `frontend/src/components/Header.tsx` (credits %/plan pill), `UpgradePrompt.tsx`
- `frontend/src/components/AddJobModal.tsx`, `profile/page.tsx`, all `cover-letters/*` pages (handle 402/429 via `UpgradePrompt`)
- `frontend/src/app/settings/page.tsx` (Account + "Billing & usage" subnav)
- `frontend/src/utils/store.ts` (`billing`, `fetchBilling`), `frontend/src/utils/api.ts` (`getBillingStatus`, `getPlans`, `createCheckout`, `createPortal`, `createTopup`, `previewPlanChange`, `getUsage`, `BillingStatus`/`Plan` types)
- `frontend/src/app/onboarding/page.tsx`

---

# PR-A — Remove contact + refunds + pricing (cosmetic)

**Delete**
- `frontend/src/app/contact/page.tsx` and the empty `contact/` dir
- `frontend/src/app/refunds/page.tsx` and the empty `refunds/` dir
- `frontend/src/components/landing/PricingSection.tsx`

**Edit**
- `frontend/src/app/page.tsx` — remove `import PricingSection` and `<PricingSection … />`.
- `frontend/src/app/landing-preview/page.tsx` — same removal.
- `frontend/src/components/landing/LandingFooter.tsx` — remove `Contact` and `Refunds` from the links array (keep `Terms`, `Privacy`).
- `frontend/src/components/LegalDoc.tsx` — remove the `Contact` and `Refund Policy` cross-links (keep Terms + Privacy).
- Grep for any remaining `/contact`, `/refunds`, `Refund`, `PricingSection` references and clean up.

**Acceptance:** landing page renders with no pricing section; footer shows only Terms · Privacy; `/contact` and `/refunds` 404; `next build` passes.

---

# PR-B — BYOK foundation

This is the core. Land it with the **server-key fallback still in place** so the app keeps working while we build.

## B1. Backend: provider clients

Add three new clients to `engine/providers.py`, each matching the existing `.complete(response_model, messages, temperature, max_tokens, max_retries, step)` contract and the `collector` pattern. Constructor must accept an explicit `api_key` (BYOK) and fall back to env only during the transition.

| Provider | New class | SDK / transport | Structured-output strategy |
|----------|-----------|-----------------|----------------------------|
| Google Gemini | `GeminiClient` | `google-genai` SDK (or OpenAI-compat endpoint) | `response_mime_type=application/json` + schema; reuse the manual-validate path like DeepSeek |
| OpenAI (ChatGPT) | `OpenAIClient` | `openai` SDK (already a dep) | `instructor` JSON mode (like `XAIClient`) — OpenAI handles it well |
| Anthropic | `AnthropicClient` | `anthropic` SDK | `instructor.from_anthropic(...)` JSON mode, or tool-use schema |

Notes:
- The engine is already provider-agnostic (services take `llm` and call `.complete()`), so **no engine service code changes** — only new client classes.
- Reuse the shared helpers (`_truncate_if_needed`, `_inject_response_schema`, `_ensure_json_word`, `_retry_call`, `_is_transient_error`) — generalize the DeepSeek manual-validate path into a small mixin so Gemini can share it.
- Each client records `Usage(input_tokens, output_tokens, provider, model)` into the collector exactly like the existing two. **Token tracking is preserved across all five providers.**
- Add SDKs to `requirements.txt`: `google-genai`, `anthropic`. (`openai` already present.) Drop `stripe` in PR-C, not here.

## B2. Backend: model registry + tasks

Create `engine/model_registry.py` (single source of truth; **devs pin to each provider's current GA model IDs at implementation time — these names drift**):

```python
# Two capability tiers per provider.
PROVIDERS = {
    "anthropic": {"reasoning": "claude-opus-<latest>",   "fast": "claude-haiku-<latest>"},
    "openai":    {"reasoning": "gpt-<flagship-latest>",   "fast": "gpt-<mini-latest>"},
    "gemini":    {"reasoning": "gemini-2.5-pro",          "fast": "gemini-2.5-flash"},
    "xai":       {"reasoning": "grok-4",                  "fast": "grok-3-mini"},
    "deepseek":  {"reasoning": "deepseek-reasoner",       "fast": "deepseek-chat"},
}

# Each app task maps to a tier (derived from today's llm_config.json task list).
TASK_TIER = {
    "default": "fast",
    "profile": "fast",            # large-context extraction
    "job_description": "fast",    # extraction
    "cover_letter_tone": "fast",  # light rewrite
    "company_intel": "reasoning",
    "job_match": "reasoning",     # scoring / judgment
    "reachout": "reasoning",
    "cover_letter": "reasoning",  # generation quality
}
```

## B3. Backend: "Recommended setup" resolution

The user asked: *recommended setup uses only providers for which a key exists; produce a mapping for each case.* Implement as **per-tier provider preference order** + first-available resolution — this gives a deterministic mapping for **every** combination of supplied keys, instead of hand-maintaining 8×5 cells.

```python
# Quality-first preference order, per tier.
PREFERENCE = {
    "reasoning": ["anthropic", "openai", "gemini", "xai", "deepseek"],
    "fast":      ["gemini", "openai", "anthropic", "deepseek", "xai"],
}

def recommended_config(available_providers: set[str]) -> dict[str, dict]:
    """For each task, pick the first preferred provider the user has a key for."""
    cfg = {}
    for task, tier in TASK_TIER.items():
        for provider in PREFERENCE[tier]:
            if provider in available_providers:
                cfg[task] = {"provider": provider, "model": PROVIDERS[provider][tier]}
                break
    return cfg  # tasks with no available provider are omitted → caller surfaces "add a key"
```

### Worked "mapping for each case" (what one click produces)

| Keys the user has | Reasoning tasks (intel/match/reachout/cover_letter) | Fast tasks (profile/job_desc/tone/default) |
|---|---|---|
| Gemini only | Gemini Pro | Gemini Flash |
| Anthropic only | Claude Opus | Claude Haiku |
| OpenAI only | GPT flagship | GPT mini |
| Grok only | Grok-4 | Grok-3-mini |
| DeepSeek only | deepseek-reasoner | deepseek-chat |
| Anthropic + Gemini | Claude Opus | Gemini Flash |
| OpenAI + DeepSeek | GPT flagship | GPT mini *(OpenAI outranks DeepSeek in both tiers)* |
| Gemini + Grok | Gemini Pro | Gemini Flash |
| **All five** | **Claude Opus** | **Gemini Flash** |
| none | — *(inference blocked; CTA to add a key)* | — |

Users can still override any individual task's provider/model in Settings (advanced); "Recommended" is just the one-click default. Preference orders live in one constant so product can re-tune later.

## B4. Backend: per-user key storage (encrypted)

Add a table (new file `api/migrations` or extend `ensure_sqlite_schema`):

```python
class UserLLMKey(Base):
    __tablename__ = "user_llm_keys"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String, nullable=False)        # anthropic|openai|gemini|xai|deepseek
    encrypted_key = Column(String, nullable=False)    # Fernet ciphertext — NEVER plaintext
    key_last4 = Column(String(4), nullable=True)      # for masked display
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)
```

Optional: `UserLLMConfig` table (or a JSON column on a `user_settings` row) to persist the per-task `{provider, model}` overrides; if absent, fall back to `recommended_config(available)` computed live.

**Encryption:** use `cryptography.Fernet` with a key from `APP_ENCRYPTION_KEY` env (32-byte urlsafe base64). Encrypt on write, decrypt only at inference time in memory. Add `cryptography` to `requirements.txt`.

## B5. Backend: resolver + threading user context

`api/llm.py` `get_llm()` currently has no user context. Change resolution to be per-user:

- New `api/llm.py::resolve_user_llm(db, user_id) -> UserLLMRuntime` that loads the user's keys + task config (or recommended fallback) and returns a small object able to build a client per task.
- `get_llm(task, collector, runtime)` builds the right client from `runtime` (decrypted key + chosen model). Keep an env-key fallback path behind a flag `BYOK_REQUIRED=false` for PR-B; flip to `true` in PR-C.
- **Thread the runtime through the gateway:** load it once in the `metered()` dependency, attach to `MeterContext` (e.g. `ctx.runtime`), so endpoints call `get_llm(task, ctx.collector, ctx.runtime)`.
- **Background tasks** (`jobs.py`): pass `user_id` (already available) into the bg function and call `resolve_user_llm` with a fresh session there, exactly like `bg_settle_*` already opens its own session.

## B6. Backend: API endpoints (new `api/routers/llm_settings.py`)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/llm/providers` | List supported providers + which the user has configured (masked: `{provider, configured, key_last4}`). Never returns plaintext keys. |
| `PUT` | `/api/llm/keys/{provider}` | Add/replace a key. Validate it with a cheap live ping (e.g. list-models / 1-token call) before saving; return `{valid: bool}`. |
| `DELETE` | `/api/llm/keys/{provider}` | Remove a key. |
| `GET` | `/api/llm/config` | Current per-task `{provider, model}` mapping (resolved or custom). |
| `PUT` | `/api/llm/config` | Save custom per-task overrides. |
| `POST` | `/api/llm/recommended` | Apply one-click recommended config from currently-available keys. Returns the resulting mapping. |

Register in `api/main.py`.

## B7. Frontend: Settings → "AI providers" tab

Replace the "Billing & usage" subnav item in `frontend/src/app/settings/page.tsx` with **"AI providers"** (and keep a read-only "Usage" view — see B8). UI:

- A card per provider (Anthropic, OpenAI, Gemini, xAI, DeepSeek): masked key input (`sk-…••••1234`), Save/Remove, live "Valid ✓ / Invalid ✕" from the validate-on-save call, and a link to where to get the key.
- A prominent **"Use recommended setup"** button → `POST /api/llm/recommended`, then shows the resulting per-task mapping ("Reasoning → Claude Opus · Fast → Gemini Flash"). Greyed-out/explanatory state when no keys are present.
- An **Advanced** disclosure: per-task provider+model dropdowns (only providers with a saved key are selectable), saved via `PUT /api/llm/config`.

New `frontend/src/utils/api.ts` methods + types mirroring B6. Remove the BYOK section's dependency on `BillingStatus`.

## B8. Frontend: keep usage UI, drop billing UI

- Keep a **Usage** view (tokens by task, recent activity) — it already exists in `billing/page.tsx`'s `UsageThisPeriod` / `UsageHistory`. Extract those into a `settings` "Usage" subtab fed by `GET /api/llm/usage` (rename of `getUsage`); drop the plan/credit/top-up cards.
- `Header.tsx`: remove the credits %/plan pill (the `billing.grant_balance` block). Optionally replace with a tiny "AI: <active provider>" indicator or nothing.

**Acceptance for PR-B:** a user can paste a Gemini key, click "Recommended setup," and run a job analysis / cover letter end-to-end **using their own key**, with `UsageEvent` rows still written. Server-key fallback still works for users who haven't added a key (because `BYOK_REQUIRED=false`).

---

# PR-C — Remove Stripe, plans, credits, limits

Now that BYOK works, delete monetization.

## C1. Backend deletions
- Delete `api/routers/billing.py`; remove its include + import from `api/main.py`.
- Delete `api/billing/ledger.py`, `limits.py`, `subscriptions.py`.
- **Gut `api/billing/gateway.py`** down to usage logging only:
  - `MeterContext` keeps `collector`, `runtime`, `user_id`, `task_type`, `ref`; drop `credits_reserved`, `charge`, `_tracker`.
  - `metered(task_type)` no longer reserves credits or enforces limits — it just builds the context (and loads the user's LLM runtime).
  - `settle_success()` / `settle_failure()` keep calling `write_usage_event` (move that fn into gateway or a small `usage_log.py`); drop `refund`/rate-window rollback.
  - `bg_settle_success/failure` simplified the same way.
  - Remove the `charge=` param at all call sites (`cover_letters.py`, `profile.py`) — it becomes a no-op; do a clean signature change.
- `api/main.py`: remove `seed_plans`, `backfill_subscriptions`, `sweep_orphaned_reservations` calls + imports.
- `api/database.py`: remove `PLAN_SEED`, `seed_plans()`, `backfill_subscriptions()`, and any `STRIPE_PRICE_*` env reads.
- `requirements.txt`: remove `stripe==15.2.0`.
- `.env.example`: remove the entire Stripe block (`STRIPE_*`, `STRIPE_PRICE_*`). Add `APP_ENCRYPTION_KEY` and set `BYOK_REQUIRED=true`.
- Flip `api/llm.py` to BYOK-only: drop the env-key fallback (or keep env only for local dev behind `BYOK_REQUIRED`). Delete `api/llm_config.json` (server-owned routing) — routing is now per-user.

## C2. Database / models
- Drop tables: `Plan`, `Subscription`, `CreditLedger`, `RateWindow`, `ProcessedWebhook`.
- **Keep `UsageEvent`** (token tracking). Its `provider`/`model` columns now reflect whichever BYOK provider ran; `credits_charged` becomes vestigial — either keep defaulted to 0 or drop the column.
- Remove the `subscription` relationship from `User`.
- Migration: since prod likely runs Supabase/Postgres, write a forward migration that drops the five tables. **Don't** delete user data. SQLite local dev: `ensure_sqlite_schema` should stop creating them.

## C3. Frontend deletions
- Delete `frontend/src/app/billing/page.tsx` and `billing/` dir (Usage view already moved to settings in B8).
- Delete `frontend/src/components/UpgradePrompt.tsx`.
- In `AddJobModal.tsx`, `profile/page.tsx`, all `cover-letters/*` pages: remove `UpgradePrompt` import/usage and the 402/429 handling. Replace with a generic **"AI provider error"** toast that triggers when a provider returns 401/403 (bad/missing key) → CTA "Check your API key in Settings."
- `store.ts`: remove `billing`, `fetchBilling`, `BillingStatus`. Add `llmProviders` state if useful.
- `api.ts`: remove `getBillingStatus`, `getPlans`, `createCheckout`, `createPortal`, `createTopup`, `previewPlanChange`, `BillingStatus`, `Plan`, `CapMap` (if unused). Keep usage types.
- `layout.tsx`: remove the `fetchBilling()` call on hydrate.
- `Header.tsx`: ensure no `billing` references remain.

## C4. Onboarding
- `onboarding/page.tsx`: replace any plan/credit step with a **"Connect an AI provider"** step — paste at least one key (or pick "Recommended" after adding keys). Make completing onboarding require ≥1 valid key (since `BYOK_REQUIRED=true`). Keep the existing Terms/Privacy consent step.

**Acceptance for PR-C:** no Stripe code, no plan/credit/limit code remains (grep clean); app runs purely on user keys; usage tracking still records every task; new-user onboarding forces adding a key.

---

## Data model: before → after

| Table | Action |
|---|---|
| `users` | keep (drop `subscription` rel) |
| `usage_events` | **keep** (token tracking) — optionally drop `credits_charged` |
| `user_llm_keys` | **new** (encrypted BYOK keys) |
| `user_llm_config` *(optional)* | **new** (per-task overrides) |
| `plans` | drop |
| `subscriptions` | drop |
| `credit_ledger` | drop |
| `rate_windows` | drop |
| `processed_webhooks` | drop |

---

## Security checklist (BYOK)
- Keys encrypted at rest (Fernet via `APP_ENCRYPTION_KEY`); never logged, never returned in plaintext (mask to last 4).
- Validate keys server-side on save with a minimal live call; reject invalid before storing.
- Provider 401/403 at inference time → clear "check your key" error, not a 500.
- Rate-limit the key-validation + key-write endpoints (reuse `slowapi`/`limiter`) to prevent abuse.
- Decrypt only in memory at request time; don't cache plaintext keys across requests.
- Document `APP_ENCRYPTION_KEY` rotation (re-encrypt on rotate).

## Testing
- Unit: `recommended_config()` for all 2^5 key combinations resolves deterministically and never picks a provider without a key.
- Unit: each new provider client returns valid structured output + records `Usage` into the collector (mock the SDK).
- Integration: with only a Gemini key, run profile build → job analysis → cover letter; assert correct models used and `UsageEvent` rows written.
- Integration: missing key → inference returns the "add a key" error, not 500.
- Regression: confirm no `stripe`, `Plan`, `CreditLedger`, `RateWindow`, `metered(... charge=...)`, `UpgradePrompt`, `billing` references remain (grep gate in CI).

## Rollback
- Each PR is a clean revert (everything in git). PR-C is the only destructive one (drops tables) — take a DB snapshot before running its migration in prod. PR-A/PR-B are non-destructive.

## Open product decisions (confirm before PR-B)
1. **Exact GA model IDs** per provider tier at implementation time (the registry names above are placeholders).
2. Preference orders in B3 — quality-first as drafted, or cost-first?
3. Keep a server-key fallback for a hosted "demo" mode, or hard BYOK for everyone (`BYOK_REQUIRED=true`)?
4. Drop `credits_charged` column or leave it defaulted for historical analytics?
