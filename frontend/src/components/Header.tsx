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
        {
            href: '/dashboard',
            label: 'Dashboard',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
            )
        },
        {
            href: '/jobs',
            label: 'My Jobs',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
            )
        },
        {
            href: '/cover-letters',
            label: 'Cover Letters',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            )
        },
        {
            href: '/discrepancies',
            label: 'Discrepancy',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            )
        },
    ];

    return (
        <header className="sticky top-0 z-50 border-b border-[var(--border-color)] bg-[var(--bg-secondary)] backdrop-blur-md supports-[backdrop-filter]:bg-[var(--bg-secondary)]/80">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-8">
                    {/* Logo */}
                    <button
                        className="flex items-center gap-2 group cursor-pointer"
                        onClick={() => router.push('/dashboard')}
                    >
                        <img
                            src="/logo.jpg"
                            alt="Wand"
                            className="w-9 h-9 rounded-lg shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-105"
                        />
                    </button>

                    {/* Navigation */}
                    <nav className="flex items-center gap-1">
                        {navLinks.map((link) => {
                            const isActive = pathname === link.href;
                            return (
                                <button
                                    key={link.href}
                                    onClick={() => router.push(link.href)}
                                    className={`relative flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${isActive
                                        ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 shadow-sm'
                                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
                                        }`}
                                >
                                    {link.icon}
                                    <span>{link.label}</span>
                                </button>
                            );
                        })}
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-colors cursor-pointer"
                        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                    >
                        {theme === 'dark' ? (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        ) : (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </svg>
                        )}
                    </button>

                    {/* Profile Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setShowProfileMenu(!showProfileMenu)}
                            className="flex items-center gap-2 pl-2 pr-1 py-1 rounded-full border border-[var(--border-color)] bg-[var(--card-bg)] hover:border-indigo-500/50 transition-colors cursor-pointer"
                        >
                            <span className="text-sm font-medium text-[var(--text-primary)] px-2">{user?.name}</span>
                            {user?.profile_picture ? (
                                <img src={user.profile_picture} alt="" className="w-8 h-8 rounded-full bg-gray-200" />
                            ) : (
                                <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold text-xs">
                                    {user?.name?.charAt(0) || 'U'}
                                </div>
                            )}
                        </button>

                        {showProfileMenu && (
                            <div className="absolute right-0 mt-2 w-56 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl shadow-xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                                <div className="px-4 py-3 border-b border-[var(--border-color)] bg-[var(--card-bg)]">
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{user?.name}</p>
                                    <p className="text-xs text-[var(--text-muted)] truncate">{user?.email}</p>
                                </div>
                                <div className="p-1">
                                    <button
                                        onClick={() => { setShowProfileMenu(false); router.push('/settings'); }}
                                        className="w-full px-3 py-2 text-left text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded-lg transition-colors flex items-center gap-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                        Account Settings
                                    </button>
                                    <button
                                        onClick={() => { setShowProfileMenu(false); router.push('/profile'); }}
                                        className="w-full px-3 py-2 text-left text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded-lg transition-colors flex items-center gap-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                        </svg>
                                        My Files
                                    </button>
                                    <button
                                        onClick={() => setShowLogoutConfirm(true)}
                                        className="w-full px-3 py-2 text-left text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-lg transition-colors flex items-center gap-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                        </svg>
                                        Sign out
                                    </button>
                                </div>
                            </div>
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
