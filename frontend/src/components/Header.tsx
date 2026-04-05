'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useStore } from '@/utils/store';
import ConfirmationModal from './ConfirmationModal';

export default function Header() {
    const router = useRouter();
    const pathname = usePathname();
    const { user, theme, toggleTheme, logout } = useStore();
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    const navLinks = [
        { href: '/dashboard',    label: 'Dashboard'     },
        { href: '/jobs',         label: 'Jobs'          },
        { href: '/cover-letters',label: 'Cover Letters' },
        { href: '/discrepancies',label: 'Discrepancy'   },
    ];

    return (
        <header
            style={{
                position: 'sticky',
                top: 0,
                zIndex: 50,
                background: 'var(--surface)',
                borderBottom: '1px solid var(--border)',
            }}
        >
            <div
                style={{
                    maxWidth: '1280px',
                    margin: '0 auto',
                    padding: '0 24px',
                    height: '52px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '32px',
                }}
            >
                {/* Left: logo + nav */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
                    {/* Logo */}
                    <button
                        onClick={() => router.push('/dashboard')}
                        style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', background: 'none', border: 'none', padding: 0 }}
                    >
                        <img
                            src="/logo.jpg"
                            alt="Wand"
                            style={{ width: '32px', height: '32px', borderRadius: '8px' }}
                        />
                    </button>

                    {/* Navigation */}
                    <nav style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                        {navLinks.map((link) => {
                            const isActive = pathname === link.href || pathname?.startsWith(link.href + '/');
                            return (
                                <button
                                    key={link.href}
                                    onClick={() => router.push(link.href)}
                                    style={{
                                        position: 'relative',
                                        padding: '4px 10px',
                                        fontSize: '13.5px',
                                        fontWeight: 500,
                                        cursor: 'pointer',
                                        background: 'none',
                                        border: 'none',
                                        borderBottom: isActive ? '2px solid var(--accent)' : '2px solid transparent',
                                        color: isActive ? 'var(--accent)' : 'var(--text-2)',
                                        transition: 'color 0.15s ease, border-color 0.15s ease',
                                        lineHeight: '24px',
                                    }}
                                    onMouseEnter={(e) => {
                                        if (!isActive) {
                                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-1)';
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        if (!isActive) {
                                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-2)';
                                        }
                                    }}
                                >
                                    {link.label}
                                </button>
                            );
                        })}
                    </nav>
                </div>

                {/* Right: theme toggle + profile */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                        style={{
                            width: '32px',
                            height: '32px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderRadius: '6px',
                            border: 'none',
                            background: 'none',
                            color: 'var(--text-2)',
                            cursor: 'pointer',
                            transition: 'color 0.15s ease, background 0.15s ease',
                        }}
                        onMouseEnter={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-1)';
                            (e.currentTarget as HTMLButtonElement).style.background = 'var(--hover)';
                        }}
                        onMouseLeave={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-2)';
                            (e.currentTarget as HTMLButtonElement).style.background = 'none';
                        }}
                    >
                        {theme === 'dark' ? (
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        ) : (
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </svg>
                        )}
                    </button>

                    {/* Profile Dropdown */}
                    <div style={{ position: 'relative' }}>
                        <button
                            onClick={() => setShowProfileMenu(!showProfileMenu)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '4px 8px',
                                border: 'none',
                                background: 'none',
                                cursor: 'pointer',
                                borderRadius: '6px',
                                transition: 'background 0.15s ease',
                            }}
                            onMouseEnter={(e) => {
                                (e.currentTarget as HTMLButtonElement).style.background = 'var(--hover)';
                            }}
                            onMouseLeave={(e) => {
                                (e.currentTarget as HTMLButtonElement).style.background = 'none';
                            }}
                        >
                            {user?.profile_picture ? (
                                <img
                                    src={user.profile_picture}
                                    alt=""
                                    style={{ width: '28px', height: '28px', borderRadius: '50%' }}
                                />
                            ) : (
                                <div
                                    style={{
                                        width: '28px',
                                        height: '28px',
                                        borderRadius: '50%',
                                        background: 'var(--accent-dim)',
                                        border: '1px solid var(--accent-border)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        color: 'var(--accent)',
                                        fontSize: '11px',
                                        fontWeight: 700,
                                        flexShrink: 0,
                                    }}
                                >
                                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                                </div>
                            )}
                            <span
                                style={{
                                    fontSize: '13.5px',
                                    fontWeight: 500,
                                    color: 'var(--text-1)',
                                    maxWidth: '120px',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                {user?.name}
                            </span>
                            <svg
                                width="12"
                                height="12"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                style={{ color: 'var(--text-3)', flexShrink: 0 }}
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>

                        {showProfileMenu && (
                            <>
                                {/* Click-away overlay */}
                                <div
                                    style={{ position: 'fixed', inset: 0, zIndex: 40 }}
                                    onClick={() => setShowProfileMenu(false)}
                                />
                                <div
                                    style={{
                                        position: 'absolute',
                                        right: 0,
                                        top: 'calc(100% + 6px)',
                                        width: '216px',
                                        background: 'var(--card)',
                                        border: '1px solid var(--border)',
                                        borderRadius: '10px',
                                        boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
                                        overflow: 'hidden',
                                        zIndex: 50,
                                    }}
                                >
                                    {/* User info */}
                                    <div
                                        style={{
                                            padding: '12px 14px',
                                            borderBottom: '1px solid var(--border)',
                                        }}
                                    >
                                        <p style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-1)', margin: 0 }}>
                                            {user?.name}
                                        </p>
                                        <p
                                            style={{
                                                fontSize: '12px',
                                                color: 'var(--text-3)',
                                                margin: '2px 0 0',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap',
                                            }}
                                        >
                                            {user?.email}
                                        </p>
                                    </div>

                                    {/* Menu items */}
                                    <div style={{ padding: '4px' }}>
                                        <DropdownItem
                                            onClick={() => { setShowProfileMenu(false); router.push('/settings'); }}
                                            icon={
                                                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                </svg>
                                            }
                                        >
                                            Account Settings
                                        </DropdownItem>
                                        <DropdownItem
                                            onClick={() => { setShowProfileMenu(false); router.push('/profile'); }}
                                            icon={
                                                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                                </svg>
                                            }
                                        >
                                            My Files
                                        </DropdownItem>
                                        <DropdownItem
                                            onClick={() => { setShowProfileMenu(false); setShowLogoutConfirm(true); }}
                                            danger
                                            icon={
                                                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                                </svg>
                                            }
                                        >
                                            Sign out
                                        </DropdownItem>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>

            <ConfirmationModal
                isOpen={showLogoutConfirm}
                onClose={() => setShowLogoutConfirm(false)}
                onConfirm={handleLogout}
                title="Sign out"
                message="Are you sure you want to sign out of your account?"
                confirmLabel="Sign out"
                isDestructive={true}
            />
        </header>
    );
}

/* ─── DropdownItem helper ───────────────────────────────────────────────────── */
function DropdownItem({
    children,
    onClick,
    icon,
    danger = false,
}: {
    children: React.ReactNode;
    onClick: () => void;
    icon?: React.ReactNode;
    danger?: boolean;
}) {
    const [hovered, setHovered] = useState(false);

    return (
        <button
            onClick={onClick}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '7px 10px',
                borderRadius: '6px',
                border: 'none',
                background: hovered
                    ? danger
                        ? 'rgba(239,68,68,0.08)'
                        : 'var(--hover)'
                    : 'none',
                color: danger
                    ? '#f87171'
                    : hovered
                    ? 'var(--text-1)'
                    : 'var(--text-2)',
                fontSize: '13px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'background 0.12s ease, color 0.12s ease',
            }}
        >
            {icon && (
                <span style={{ flexShrink: 0, opacity: 0.8 }}>{icon}</span>
            )}
            {children}
        </button>
    );
}
