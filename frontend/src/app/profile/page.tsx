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
    title,
    type,
    profile,
    onUpload,
    onDelete,
    onPreview,
    onViewData,
    isUploading
}: {
    title: string;
    type: 'resume' | 'linkedin' | 'portfolio';
    profile: UserProfile | null;
    onUpload: (file: File, type: any) => void;
    onDelete: (type: any) => void;
    onPreview: (type: any) => void;
    onViewData: (title: string, data: any) => void;
    isUploading: boolean;
}) {
    const [isDragging, setIsDragging] = useState(false);

    // Check if file exists in profile
    const typeKey = `${type}_path` as keyof UserProfile;
    const hasFile = profile && profile[typeKey];
    const dataKey = `${type}_data` as keyof UserProfile;
    const hasData = profile && profile[dataKey];

    // Status
    const status = hasData ? 'parsed' : hasFile ? 'uploaded' : 'missing';

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files?.[0]) {
            onUpload(e.dataTransfer.files[0], type);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            onUpload(e.target.files[0], type);
        }
    };

    return (
        <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl p-6 relative overflow-hidden group">
            {/* Status indicator */}
            <div className={`absolute top-4 right-4 text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider ${status === 'parsed' ? 'bg-green-500/10 text-green-500' :
                status === 'uploaded' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-red-500/10 text-red-500'
                }`}>
                {status}
            </div>

            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={type === 'portfolio' ? "M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" : "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"} />
                    </svg>
                </div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h3>
            </div>

            {hasFile ? (
                <div className="space-y-4">
                    <p className="text-sm text-[var(--text-secondary)]">
                        File uploaded securely.
                        {hasData ? " Successfully parsed and ready for analysis." : " Waiting for processing."}
                    </p>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onPreview(type)}
                            className="flex-1 px-3 py-2 text-sm text-[var(--text-primary)] bg-[var(--bg-secondary)] hover:bg-[var(--bg-hover)] border border-[var(--border-color)] rounded-lg transition-colors flex items-center justify-center gap-1"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            Preview
                        </button>
                        {hasData && (
                            <button
                                onClick={() => onViewData(title, profile[dataKey])}
                                className="flex-1 px-3 py-2 text-sm text-[var(--text-secondary)] bg-[var(--bg-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] border border-[var(--border-color)] rounded-lg transition-colors flex items-center justify-center gap-1"
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                </svg>
                                View Data
                            </button>
                        )}
                        <button
                            onClick={() => onDelete(type)}
                            className="px-3 py-2 text-sm text-red-500 bg-red-500/10 hover:bg-red-500/20 rounded-lg transition-colors"
                            title="Delete File"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            ) : (
                <div
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${isDragging ? 'border-indigo-500 bg-indigo-500/5' : 'border-[var(--border-color)] hover:border-indigo-500/50'
                        }`}
                >
                    <input
                        type="file"
                        id={`file-${type}`}
                        className="hidden"
                        accept={type === 'portfolio' ? '.html,.htm' : '.pdf'}
                        onChange={handleChange}
                    />
                    <label htmlFor={`file-${type}`} className="cursor-pointer">
                        {isUploading ? (
                            <div className="animate-pulse text-sm text-[var(--text-muted)]">Uploading...</div>
                        ) : (
                            <>
                                <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Click to upload</p>
                                <p className="text-xs text-[var(--text-muted)]">or drag and drop {type === 'portfolio' ? 'HTML' : 'PDF'}</p>
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
    const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; type: 'resume' | 'linkedin' | 'portfolio' | null }>({
        isOpen: false,
        type: null
    });
    const [dataModal, setDataModal] = useState<{ isOpen: boolean; title: string; data: any }>({
        isOpen: false,
        title: '',
        data: null
    });
    const [unifying, setUnifying] = useState(false);

    // Warn if user tries to refresh/leave while uploading
    usePageUnloadWarning(!!uploading || unifying, "Upload/Creation in progress. Leaving now will cancel the operation.");

    useEffect(() => {
        if (!_hasHydrated) return;
        if (!token) {
            router.push('/');
            return;
        }
        loadProfile();
    }, [token, _hasHydrated]);

    const loadProfile = async () => {
        try {
            const data = await api.getProfile();
            setProfile(data);
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
            // Reload profile to get Updated Paths and Data
            await loadProfile();
        } catch (error) {
            console.error(error);
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
        } catch (error) {
            console.error(error);
            alert('Failed to delete file');
        } finally {
            setDeleteModal({ isOpen: false, type: null });
        }
    };

    const handleDelete = (type: 'resume' | 'linkedin' | 'portfolio') => {
        setDeleteModal({ isOpen: true, type });
    };

    const handlePreview = async (type: string) => {
        try {
            const blob = await api.getProfileFileBlob(type);
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
        } catch (error) {
            console.error(error);
            alert('Failed to preview file.');
        }
    };

    const handleViewData = (title: string, data: any) => {
        setDataModal({ isOpen: true, title, data });
    };

    const handleUnify = async () => {
        setUnifying(true);
        try {
            await api.createUnifiedProfile();
            await loadProfile();
            alert('Unified Profile Created Successfully!');
        } catch (error) {
            console.error(error);
            alert('Failed to create Unified Profile');
        } finally {
            setUnifying(false);
        }
    };

    if (!_hasHydrated || !isAuthenticated || loading) {
        return (
            <div className="min-h-screen">
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                </div>
            </div>
        );
    }

    const hasAnyData = profile?.resume_data || profile?.linkedin_data || profile?.portfolio_data;

    return (
        <main className="min-h-screen bg-[var(--bg-primary)]">
            <Header />

            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">My Files</h1>
                    <p className="text-[var(--text-secondary)]">Manage your career documents. Uploading these helps us generate accurate job analyses.</p>
                </div>

                {/* Upload Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <FileCard
                        title="Resume"
                        type="resume"
                        profile={profile}
                        onUpload={handleUpload}
                        onDelete={handleDelete}
                        onPreview={handlePreview}
                        onViewData={handleViewData}
                        isUploading={uploading === 'resume'}
                    />
                    <FileCard
                        title="LinkedIn Profile"
                        type="linkedin"
                        profile={profile}
                        onUpload={handleUpload}
                        onDelete={handleDelete}
                        onPreview={handlePreview}
                        onViewData={handleViewData}
                        isUploading={uploading === 'linkedin'}
                    />
                    <FileCard
                        title="Portfolio Website"
                        type="portfolio"
                        profile={profile}
                        onUpload={handleUpload}
                        onDelete={handleDelete}
                        onPreview={handlePreview}
                        onViewData={handleViewData}
                        isUploading={uploading === 'portfolio'}
                    />
                </div>

                {/* Unified Profile Action */}
                <div className="flex flex-col items-center justify-center py-8 border-t border-[var(--border-color)]">
                    <button
                        onClick={handleUnify}
                        disabled={!hasAnyData || unifying}
                        className={`
                            px-8 py-3 rounded-xl font-semibold text-white shadow-lg transition-all transform
                            ${!hasAnyData || unifying ? 'bg-gray-500 cursor-not-allowed opacity-50' : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:scale-105 hover:shadow-indigo-500/25'}
                        `}
                    >
                        {unifying ? 'Generating Unified Profile...' : (profile?.unified_profile ? 'Update Unified Profile' : 'Create Unified Profile')}
                    </button>
                    {!hasAnyData && (
                        <p className="text-sm text-[var(--text-muted)] mt-3">Upload at least one document to enable this feature.</p>
                    )}
                </div>

                {/* Unified Profile Preview */}
                {profile?.unified_profile && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-12"
                    >
                        <UnifiedProfileView profile={profile.unified_profile} />
                    </motion.div>
                )}
            </div>

            <ConfirmationModal
                isOpen={deleteModal.isOpen}
                onClose={() => setDeleteModal({ isOpen: false, type: null })}
                onConfirm={confirmDelete}
                title="Remove File"
                message={`Are you sure you want to remove your ${deleteModal.type}? This will prevent it from being used in future analyses.`}
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
