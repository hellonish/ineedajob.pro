'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, UserProfile } from '@/utils/api';
import Header from '@/components/Header';
import { usePageUnloadWarning } from '@/hooks/usePageUnloadWarning';
import { motion, AnimatePresence } from 'framer-motion';
import ConfirmationModal from '@/components/ConfirmationModal';
import DataViewerModal from '@/components/DataViewerModal';
import UnifiedProfileView from '@/components/UnifiedProfileView';

function FileCard({
    title, type, profile, onUpload, onDelete, onPreview, onViewData, isUploading
}: {
    title: string;
    type: 'resume' | 'linkedin' | 'portfolio';
    profile: UserProfile | null;
    onUpload: (file: File, type: 'resume' | 'linkedin' | 'portfolio') => void;
    onDelete: (type: 'resume' | 'linkedin' | 'portfolio') => void;
    onPreview: (type: string) => void;
    onViewData: (title: string, data: unknown) => void;
    isUploading: boolean;
}) {
    const [isDragging, setIsDragging] = useState(false);
    const typeKey = `${type}_path` as keyof UserProfile;
    const hasFile = profile && profile[typeKey];
    const dataKey = `${type}_data` as keyof UserProfile;
    const hasData = profile && profile[dataKey];
    const status = hasData ? 'parsed' : hasFile ? 'uploaded' : 'empty';

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files?.[0]) onUpload(e.dataTransfer.files[0], type);
    };

    return (
        <div
            className="rounded-lg p-4"
            style={{ border: '1px solid var(--border)', background: 'var(--card)' }}
        >
            <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{title}</span>
                <span
                    className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded"
                    style={{
                        background: status === 'parsed' ? 'rgba(34,197,94,0.1)' : status === 'uploaded' ? 'rgba(251,191,36,0.1)' : 'var(--surface)',
                        color: status === 'parsed' ? '#22c55e' : status === 'uploaded' ? '#fbbf24' : 'var(--text-3)',
                    }}
                >
                    {status === 'parsed' ? 'Ready' : status === 'uploaded' ? 'Uploaded' : 'Missing'}
                </span>
            </div>

            {hasFile ? (
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => onPreview(type)}
                        className="flex-1 text-xs py-1.5 rounded-md cursor-pointer transition-colors"
                        style={{ border: '1px solid var(--border)', color: 'var(--text-2)', background: 'transparent' }}
                        onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-1)'; }}
                        onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-2)'; }}
                    >
                        Preview
                    </button>
                    {hasData && (
                        <button
                            onClick={() => onViewData(title, profile[dataKey])}
                            className="flex-1 text-xs py-1.5 rounded-md cursor-pointer transition-colors"
                            style={{ border: '1px solid var(--border)', color: 'var(--text-2)', background: 'transparent' }}
                            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-1)'; }}
                            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-2)'; }}
                        >
                            View Data
                        </button>
                    )}
                    <button
                        onClick={() => onDelete(type)}
                        className="px-2.5 py-1.5 text-xs rounded-md cursor-pointer transition-colors"
                        style={{ border: '1px solid transparent', color: '#f87171', background: 'rgba(239,68,68,0.08)' }}
                        onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(239,68,68,0.15)'; }}
                        onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(239,68,68,0.08)'; }}
                    >
                        Remove
                    </button>
                </div>
            ) : (
                <div
                    onDragOver={e => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                    className="rounded-md p-4 text-center transition-colors"
                    style={{
                        border: `1.5px dashed ${isDragging ? 'var(--accent)' : 'var(--border)'}`,
                        background: isDragging ? 'var(--accent-dim)' : 'var(--surface)',
                    }}
                >
                    <input
                        type="file"
                        id={`file-${type}`}
                        className="hidden"
                        accept={type === 'portfolio' ? '.html,.htm' : '.pdf'}
                        onChange={e => { if (e.target.files?.[0]) onUpload(e.target.files[0], type); }}
                    />
                    <label htmlFor={`file-${type}`} className="cursor-pointer">
                        {isUploading ? (
                            <p className="text-xs" style={{ color: 'var(--text-3)' }}>Uploading...</p>
                        ) : (
                            <>
                                <p className="text-xs font-medium" style={{ color: 'var(--text-2)' }}>Click to upload</p>
                                <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
                                    {type === 'portfolio' ? 'HTML file' : 'PDF file'}
                                </p>
                            </>
                        )}
                    </label>
                </div>
            )}
        </div>
    );
}

export default function ProfilePage() {
    const router = useRouter();
    const { token, isAuthenticated, _hasHydrated } = useStore();
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState<string | null>(null);
    const [unifying, setUnifying] = useState(false);
    const [additionalContext, setAdditionalContext] = useState('');
    const [savingContext, setSavingContext] = useState(false);
    const [contextSaved, setContextSaved] = useState(false);
    const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; type: 'resume' | 'linkedin' | 'portfolio' | null }>({
        isOpen: false, type: null
    });
    const [dataModal, setDataModal] = useState<{ isOpen: boolean; title: string; data: unknown }>({
        isOpen: false, title: '', data: null
    });

    usePageUnloadWarning(!!uploading || unifying, 'Upload in progress. Leaving will cancel the operation.');

    useEffect(() => {
        if (!_hasHydrated) return;
        if (!token) { router.push('/'); return; }
        loadProfile();
    }, [token, _hasHydrated]);

    const loadProfile = async () => {
        try {
            const data = await api.getProfile();
            setProfile(data);
            setAdditionalContext(data.additional_context || '');
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (file: File, type: 'resume' | 'linkedin' | 'portfolio') => {
        setUploading(type);
        try {
            await api.uploadProfileFile(file, type);
            await loadProfile();
        } catch {
            alert('Upload failed');
        } finally {
            setUploading(null);
        }
    };

    const confirmDelete = async () => {
        if (!deleteModal.type) return;
        try {
            await api.deleteProfileFile(deleteModal.type);
            await loadProfile();
        } catch {
            alert('Failed to delete file');
        } finally {
            setDeleteModal({ isOpen: false, type: null });
        }
    };

    const handlePreview = async (type: string) => {
        try {
            const blob = await api.getProfileFileBlob(type);
            window.open(URL.createObjectURL(blob), '_blank');
        } catch {
            alert('Failed to preview file.');
        }
    };

    const handleUnify = async () => {
        setUnifying(true);
        try {
            await api.createUnifiedProfile();
            await loadProfile();
        } catch {
            alert('Failed to create Unified Profile');
        } finally {
            setUnifying(false);
        }
    };

    const handleSaveContext = async () => {
        setSavingContext(true);
        try {
            await api.updateAdditionalContext(additionalContext);
            setContextSaved(true);
            setTimeout(() => setContextSaved(false), 2000);
        } catch {
            alert('Failed to save');
        } finally {
            setSavingContext(false);
        }
    };

    if (!_hasHydrated || !isAuthenticated || loading) {
        return (
            <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div className="w-6 h-6 rounded-full animate-spin" style={{ border: '2px solid var(--border-strong)', borderTopColor: 'var(--accent)' }} />
                </div>
            </div>
        );
    }

    const hasAnyData = profile?.resume_data || profile?.linkedin_data || profile?.portfolio_data;

    return (
        <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
            <Header />

            <div className="max-w-screen-lg mx-auto px-8 py-6">
                {/* Page header */}
                <div className="mb-6">
                    <h1 className="text-lg font-semibold" style={{ color: 'var(--text-1)' }}>Profile</h1>
                    <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
                        Manage your career documents — they power the JobLens analysis pipeline.
                    </p>
                </div>

                {/* Upload grid */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <FileCard title="Resume" type="resume" profile={profile} onUpload={handleUpload}
                        onDelete={t => setDeleteModal({ isOpen: true, type: t })}
                        onPreview={handlePreview} onViewData={(t, d) => setDataModal({ isOpen: true, title: t, data: d })}
                        isUploading={uploading === 'resume'} />
                    <FileCard title="LinkedIn PDF" type="linkedin" profile={profile} onUpload={handleUpload}
                        onDelete={t => setDeleteModal({ isOpen: true, type: t })}
                        onPreview={handlePreview} onViewData={(t, d) => setDataModal({ isOpen: true, title: t, data: d })}
                        isUploading={uploading === 'linkedin'} />
                    <FileCard title="Portfolio" type="portfolio" profile={profile} onUpload={handleUpload}
                        onDelete={t => setDeleteModal({ isOpen: true, type: t })}
                        onPreview={handlePreview} onViewData={(t, d) => setDataModal({ isOpen: true, title: t, data: d })}
                        isUploading={uploading === 'portfolio'} />
                </div>

                {/* Additional context */}
                <div className="mb-6 rounded-lg p-4" style={{ border: '1px solid var(--border)', background: 'var(--card)' }}>
                    <div className="flex items-start justify-between mb-2">
                        <div>
                            <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>Additional Context</p>
                            <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
                                Links, certifications, side projects, or anything not in your resume
                            </p>
                        </div>
                        <button
                            onClick={handleSaveContext}
                            disabled={savingContext}
                            className="text-xs px-3 py-1.5 rounded-md cursor-pointer transition-colors flex-shrink-0 ml-4"
                            style={{
                                border: '1px solid var(--border)',
                                color: contextSaved ? '#22c55e' : 'var(--text-2)',
                                background: 'transparent',
                            }}
                            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-1)'; }}
                            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = contextSaved ? '#22c55e' : 'var(--text-2)'; }}
                        >
                            {contextSaved ? 'Saved' : savingContext ? 'Saving...' : 'Save'}
                        </button>
                    </div>
                    <textarea
                        value={additionalContext}
                        onChange={e => setAdditionalContext(e.target.value)}
                        placeholder="GitHub: github.com/you&#10;Personal site: yoursite.com&#10;Open source work: ...&#10;Certifications: AWS Solutions Architect, ..."
                        rows={5}
                        className="w-full rounded-md px-3 py-2 text-sm resize-none focus:outline-none transition-colors"
                        style={{
                            background: 'var(--surface)',
                            border: '1px solid var(--border)',
                            color: 'var(--text-1)',
                        }}
                        onFocus={e => { (e.target as HTMLTextAreaElement).style.borderColor = 'var(--border-strong)'; }}
                        onBlur={e => { (e.target as HTMLTextAreaElement).style.borderColor = 'var(--border)'; }}
                    />
                </div>

                {/* Unify action */}
                <div className="flex items-center justify-between py-4 mb-6" style={{ borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
                    <div>
                        <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>
                            {profile?.unified_profile ? 'Update Unified Profile' : 'Create Unified Profile'}
                        </p>
                        <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
                            Merges all your documents into one profile + auto-extracts structured data for JobLens
                        </p>
                    </div>
                    <button
                        onClick={handleUnify}
                        disabled={!hasAnyData || unifying}
                        className="px-4 py-2 text-sm rounded-md cursor-pointer transition-colors flex-shrink-0 ml-4"
                        style={{
                            background: hasAnyData && !unifying ? 'var(--accent)' : 'var(--surface)',
                            color: hasAnyData && !unifying ? '#fff' : 'var(--text-3)',
                            border: '1px solid transparent',
                            cursor: hasAnyData && !unifying ? 'pointer' : 'not-allowed',
                        }}
                    >
                        {unifying ? 'Processing...' : profile?.unified_profile ? 'Re-generate' : 'Generate'}
                    </button>
                </div>

                {/* Extracted profile preview */}
                {profile?.extracted_profile && (
                    <div className="mb-6 rounded-lg p-4" style={{ border: '1px solid var(--border)', background: 'var(--card)' }}>
                        <div className="flex items-center justify-between mb-3">
                            <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>Extracted Profile</p>
                            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded" style={{ background: 'var(--accent-dim)', color: 'var(--accent)' }}>
                                JobLens Ready
                            </span>
                        </div>
                        {(() => {
                            const ep = profile.extracted_profile as Record<string, unknown>;
                            const str = (v: unknown, fb = '—') => v != null ? String(v) : fb;
                            return (
                                <div className="flex flex-wrap gap-4 text-sm">
                                    {[
                                        ['Title', ep.current_title],
                                        ['Experience', ep.years_of_experience != null ? str(ep.years_of_experience) + 'y' : null],
                                        ['Role Type', ep.primary_role_type],
                                    ].filter(([, v]) => v != null).map(([label, val]) => (
                                        <div key={str(label)}>
                                            <p className="text-xs" style={{ color: 'var(--text-3)' }}>{str(label)}</p>
                                            <p style={{ color: 'var(--text-1)' }}>{str(val)}</p>
                                        </div>
                                    ))}
                                    {ep.professional_summary != null && (
                                        <div className="w-full mt-1">
                                            <p className="text-xs mb-1" style={{ color: 'var(--text-3)' }}>AI Summary</p>
                                            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)' }}>
                                                {String(ep.professional_summary)}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            );
                        })()}
                    </div>
                )}

                {/* Unified profile view */}
                {profile?.unified_profile && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <UnifiedProfileView profile={profile.unified_profile} />
                    </motion.div>
                )}
            </div>

            <ConfirmationModal
                isOpen={deleteModal.isOpen}
                onClose={() => setDeleteModal({ isOpen: false, type: null })}
                onConfirm={confirmDelete}
                title="Remove File"
                message={`Remove your ${deleteModal.type}? This will prevent it from being used in future analyses.`}
                confirmLabel="Remove"
                isDestructive={true}
            />

            <DataViewerModal
                isOpen={dataModal.isOpen}
                onClose={() => setDataModal({ ...dataModal, isOpen: false })}
                title={dataModal.title}
                data={dataModal.data}
            />
        </main>
    );
}
