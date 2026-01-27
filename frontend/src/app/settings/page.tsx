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

    // Form State
    const [name, setName] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');

    // Modal State
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

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
            await fetchUser(); // Refresh global state
            setSaveMessage('Profile updated successfully!');
            setTimeout(() => setSaveMessage(''), 3000);
        } catch (error) {
            console.error(error);
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
        } catch (error) {
            console.error(error);
            setIsDeleting(false);
            alert('Failed to delete account. Please try again.');
        }
    };

    if (!_hasHydrated || !isAuthenticated || !user) {
        return null; // Or loader
    }

    return (
        <main className="min-h-screen bg-[var(--bg-primary)]">
            <Header />

            <div className="max-w-2xl mx-auto px-6 py-12">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                >
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Account Settings</h1>
                        <p className="text-[var(--text-secondary)] mt-2">Manage your personal information and account preferences.</p>
                    </div>

                    {/* Profile Section */}
                    <section className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-2xl p-6 md:p-8">
                        <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Profile Information</h2>

                        <form onSubmit={handleSaveProfile} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                                    Display Name
                                </label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="w-full px-4 py-2.5 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                                    placeholder="Your Name"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    value={user.email}
                                    disabled
                                    className="w-full px-4 py-2.5 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-xl text-[var(--text-muted)] cursor-not-allowed"
                                />
                                <p className="text-xs text-[var(--text-muted)] mt-2">
                                    Email address is managed via your Google account and cannot be changed here.
                                </p>
                            </div>

                            <div className="flex items-center justify-between pt-4">
                                <span className={`text-sm font-medium transition-colors ${saveMessage.includes('Failed') ? 'text-red-400' : 'text-green-400'
                                    }`}>
                                    {saveMessage}
                                </span>
                                <button
                                    type="submit"
                                    disabled={isSaving || name === user.name}
                                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600/50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition-colors shadow-lg shadow-indigo-500/20"
                                >
                                    {isSaving ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    </section>

                    {/* Danger Zone */}
                    <section className="bg-red-500/5 border border-red-500/20 rounded-2xl p-6 md:p-8">
                        <h2 className="text-xl font-semibold text-red-500 mb-2">Danger Zone</h2>
                        <p className="text-sm text-[var(--text-secondary)] mb-6">
                            Once you delete your account, there is no going back. All your data, including jobs, resumes, and analysis history will be permanently removed.
                        </p>

                        <div className="flex justify-end">
                            <button
                                onClick={() => setShowDeleteConfirm(true)}
                                className="px-6 py-2.5 bg-white dark:bg-red-500/10 hover:bg-red-50 dark:hover:bg-red-500/20 border border-red-200 dark:border-red-500/30 text-red-600 dark:text-red-400 text-sm font-semibold rounded-xl transition-all"
                            >
                                Delete Account
                            </button>
                        </div>
                    </section>
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
