'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api } from '@/utils/api';
import Header from '@/components/Header';
import ConfirmationModal from '@/components/ConfirmationModal';
import { motion } from 'framer-motion';

export default function SettingsPage() {
    const router = useRouter();
    const { user, isAuthenticated, _hasHydrated, fetchUser, logout } = useStore();

    const [name, setName] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');

    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const [focusedInput, setFocusedInput] = useState<string | null>(null);
    const [deleteHovered, setDeleteHovered] = useState(false);

    useEffect(() => {
        if (_hasHydrated && !isAuthenticated) {
            router.push('/');
        }
        if (user) {
            setName(user.name);
        }
    }, [user, isAuthenticated, _hasHydrated, router]);

    const handleSaveProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setSaveMessage('');

        try {
            await api.updateUser({ name });
            await fetchUser();
            setSaveMessage('Profile updated successfully!');
            setTimeout(() => setSaveMessage(''), 3000);
        } catch {
            setSaveMessage('Failed to update profile.');
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteAccount = async () => {
        setIsDeleting(true);
        try {
            await api.deleteAccount();
            logout();
            router.push('/');
        } catch {
            setIsDeleting(false);
            alert('Failed to delete account. Please try again.');
        }
    };

    const hasChanges = name !== user?.name;

    if (!_hasHydrated || !isAuthenticated || !user) {
        return null;
    }

    return (
        <main style={{ minHeight: '100vh', background: 'var(--bg)' }}>
            <Header />

            <div className="max-w-2xl mx-auto px-8 py-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    {/* Page header */}
                    <h1
                        className="text-lg font-semibold mb-8"
                        style={{ color: 'var(--text-1)' }}
                    >
                        Settings
                    </h1>

                    {/* Profile Section */}
                    <div
                        className="border-b pb-8 mb-8"
                        style={{ borderColor: 'var(--border)' }}
                    >
                        <p
                            className="text-xs uppercase tracking-widest mb-4"
                            style={{ color: 'var(--text-3)' }}
                        >
                            Profile
                        </p>

                        <form onSubmit={handleSaveProfile}>
                            <div className="mb-4">
                                <label
                                    className="text-xs block mb-1.5"
                                    style={{ color: 'var(--text-2)' }}
                                >
                                    Display Name
                                </label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    onFocus={() => setFocusedInput('name')}
                                    onBlur={() => setFocusedInput(null)}
                                    placeholder="Your Name"
                                    style={{
                                        background: 'var(--card)',
                                        border: `1px solid ${focusedInput === 'name' ? 'var(--border-strong)' : 'var(--border)'}`,
                                        color: 'var(--text-1)',
                                        borderRadius: '6px',
                                        padding: '8px 12px',
                                        fontSize: '14px',
                                        width: '100%',
                                        outline: 'none',
                                        transition: 'border-color 0.15s',
                                    }}
                                />
                            </div>

                            <div className="mb-6">
                                <label
                                    className="text-xs block mb-1.5"
                                    style={{ color: 'var(--text-2)' }}
                                >
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    value={user.email}
                                    disabled
                                    style={{
                                        background: 'var(--card)',
                                        border: '1px solid var(--border)',
                                        color: 'var(--text-3)',
                                        borderRadius: '6px',
                                        padding: '8px 12px',
                                        fontSize: '14px',
                                        width: '100%',
                                        outline: 'none',
                                        cursor: 'not-allowed',
                                    }}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <span
                                    className="text-sm"
                                    style={{
                                        color: saveMessage.includes('Failed') ? 'var(--danger)' : 'var(--success)',
                                        visibility: saveMessage ? 'visible' : 'hidden',
                                    }}
                                >
                                    {saveMessage || ' '}
                                </span>
                                <button
                                    type="submit"
                                    disabled={isSaving || !hasChanges}
                                    style={{
                                        border: hasChanges && !isSaving
                                            ? '1px solid var(--accent-border)'
                                            : '1px solid var(--border)',
                                        color: hasChanges && !isSaving
                                            ? 'var(--accent)'
                                            : 'var(--text-3)',
                                        cursor: hasChanges && !isSaving ? 'pointer' : 'not-allowed',
                                        background: 'transparent',
                                        borderRadius: '6px',
                                        padding: '7px 16px',
                                        fontSize: '13px',
                                        transition: 'all 0.15s',
                                    }}
                                >
                                    {isSaving ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Danger Zone */}
                    <div>
                        <p
                            className="text-xs uppercase tracking-widest mb-4"
                            style={{ color: 'var(--danger)' }}
                        >
                            Danger Zone
                        </p>
                        <p
                            className="text-sm mb-4"
                            style={{ color: 'var(--text-3)' }}
                        >
                            Once you delete your account, there is no going back. All your data, including jobs, resumes, and analysis history will be permanently removed.
                        </p>
                        <button
                            onClick={() => setShowDeleteConfirm(true)}
                            onMouseEnter={() => setDeleteHovered(true)}
                            onMouseLeave={() => setDeleteHovered(false)}
                            className="text-sm px-4 py-2 rounded-md"
                            style={{
                                border: deleteHovered
                                    ? '1px solid var(--danger)'
                                    : '1px solid var(--danger-border)',
                                color: 'var(--danger)',
                                background: deleteHovered ? 'var(--danger-dim)' : 'transparent',
                                cursor: 'pointer',
                                transition: 'all 0.15s',
                            }}
                        >
                            Delete Account
                        </button>
                    </div>
                </motion.div>
            </div>

            <ConfirmationModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleDeleteAccount}
                title="Delete Account"
                message="Are you absolutely sure? This action cannot be undone and will permanently delete your account and all associated data."
                confirmLabel={isDeleting ? "Deleting..." : "Delete Account"}
                isDestructive={true}
            />
        </main>
    );
}
