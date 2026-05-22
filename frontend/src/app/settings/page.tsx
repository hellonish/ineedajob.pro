'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, AvailableProviders } from '@/utils/api';
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

    const [providers, setProviders] = useState<AvailableProviders | null>(null);
    const [selectedProvider, setSelectedProvider] = useState('');
    const [selectedModel, setSelectedModel] = useState('');
    const [modelsLoading, setModelsLoading] = useState(true);

    const [focusedInput, setFocusedInput] = useState<string | null>(null);
    const [hoveredProvider, setHoveredProvider] = useState<string | null>(null);
    const [hoveredModel, setHoveredModel] = useState<string | null>(null);
    const [deleteHovered, setDeleteHovered] = useState(false);

    useEffect(() => {
        if (_hasHydrated && !isAuthenticated) {
            router.push('/');
        }
        if (user) {
            setName(user.name);
            setSelectedProvider(user.llm_provider || 'grok');
            setSelectedModel(user.llm_model || '');
        }
    }, [user, isAuthenticated, _hasHydrated, router]);

    useEffect(() => {
        loadProviders();
    }, []);

    const loadProviders = async () => {
        try {
            const result = await api.getLLMProviders();
            setProviders(result);
        } catch {
            setProviders({
                providers: {
                    grok: { default_model: 'grok-3', models: ['grok-3', 'grok-3-mini'] },
                    gemini: { default_model: 'gemini-2.5-pro', models: ['gemini-2.5-pro', 'gemini-2.5-flash'] },
                    deepseek: { default_model: 'deepseek-chat', models: ['deepseek-chat', 'deepseek-reasoner'] },
                }
            });
        } finally {
            setModelsLoading(false);
        }
    };

    const handleSaveProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setSaveMessage('');

        try {
            await api.updateUser({ name, llm_provider: selectedProvider, llm_model: selectedModel || undefined });
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

    const availableModels = providers?.providers?.[selectedProvider]?.models || [];
    const defaultModel = providers?.providers?.[selectedProvider]?.default_model || '';

    useEffect(() => {
        if (defaultModel && !selectedModel) {
            setSelectedModel(defaultModel);
        }
    }, [selectedProvider, defaultModel]);

    const hasChanges = name !== user?.name || selectedProvider !== (user?.llm_provider || 'grok') || selectedModel !== (user?.llm_model || '');

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

                    {/* AI Model Section */}
                    <div
                        className="border-b pb-8 mb-8"
                        style={{ borderColor: 'var(--border)' }}
                    >
                        <p
                            className="text-xs uppercase tracking-widest mb-4"
                            style={{ color: 'var(--text-3)' }}
                        >
                            AI Model
                        </p>

                        {modelsLoading ? (
                            <p className="text-sm" style={{ color: 'var(--text-3)' }}>
                                Loading providers...
                            </p>
                        ) : (
                            <>
                                {/* Provider selector */}
                                <div className="mb-5">
                                    <label
                                        className="text-xs block mb-1.5"
                                        style={{ color: 'var(--text-2)' }}
                                    >
                                        Provider
                                    </label>
                                    <div className="grid grid-cols-3 gap-2">
                                        {providers && Object.entries(providers.providers).map(([key]) => {
                                            const isSelected = selectedProvider === key;
                                            const isHovered = hoveredProvider === key && !isSelected;
                                            return (
                                                <button
                                                    key={key}
                                                    type="button"
                                                    onClick={() => setSelectedProvider(key)}
                                                    onMouseEnter={() => setHoveredProvider(key)}
                                                    onMouseLeave={() => setHoveredProvider(null)}
                                                    className="capitalize text-sm py-2 rounded-md"
                                                    style={{
                                                        border: isSelected
                                                            ? '1px solid var(--accent-border)'
                                                            : isHovered
                                                                ? '1px solid var(--border-strong)'
                                                                : '1px solid var(--border)',
                                                        background: isSelected ? 'var(--accent-dim)' : 'var(--card)',
                                                        color: isSelected
                                                            ? 'var(--accent)'
                                                            : isHovered
                                                                ? 'var(--text-1)'
                                                                : 'var(--text-2)',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.15s',
                                                    }}
                                                >
                                                    {key}
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>

                                {/* Model selector */}
                                <div>
                                    <label
                                        className="text-xs block mb-1.5"
                                        style={{ color: 'var(--text-2)' }}
                                    >
                                        Model
                                    </label>
                                    <div>
                                        {availableModels.map((model, idx) => {
                                            const isSelected = selectedModel === model;
                                            const isHovered = hoveredModel === model && !isSelected;
                                            const isLast = idx === availableModels.length - 1;
                                            return (
                                                <div
                                                    key={model}
                                                    onClick={() => setSelectedModel(model)}
                                                    onMouseEnter={() => setHoveredModel(model)}
                                                    onMouseLeave={() => setHoveredModel(null)}
                                                    className="flex items-center gap-2 py-3 px-0 text-sm"
                                                    style={{
                                                        borderBottom: isLast ? 'none' : '1px solid var(--border)',
                                                        color: isSelected
                                                            ? 'var(--accent)'
                                                            : isHovered
                                                                ? 'var(--text-1)'
                                                                : 'var(--text-2)',
                                                        cursor: 'pointer',
                                                        transition: 'color 0.15s',
                                                    }}
                                                >
                                                    {/* Selection indicator */}
                                                    <span
                                                        style={{
                                                            width: '6px',
                                                            height: '6px',
                                                            borderRadius: '50%',
                                                            background: isSelected ? 'var(--accent)' : 'transparent',
                                                            flexShrink: 0,
                                                            transition: 'background 0.15s',
                                                        }}
                                                    />
                                                    <span>{model}</span>
                                                    {model === defaultModel && (
                                                        <span
                                                            className="text-xs px-1.5 py-0.5 rounded"
                                                            style={{
                                                                border: '1px solid var(--border)',
                                                                color: 'var(--text-3)',
                                                            }}
                                                        >
                                                            default
                                                        </span>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </>
                        )}
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
