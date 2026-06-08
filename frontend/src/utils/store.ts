import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api, type User, type ProfileFileType } from './api';
import { uploadFileXHR } from './uploadUtils';

// ─── Upload queue ──────────────────────────────────────────────────────────────

export interface UploadQueueItem {
    id: string;
    filename: string;
    fileSize: number;
    type: ProfileFileType;
    status: 'uploading' | 'parsing' | 'done' | 'error';
    progress: number; // 0–100
    error?: string;
}

interface UploadInput {
    file: File;
    type: ProfileFileType;
    additionalContext: string;
}

interface AppState {
    // Current user (fetched from API on mount; null until first fetch)
    user: User | null;

    // Theme
    theme: 'dark' | 'light';

    // Jobs Filter
    jobsFilter: string;

    // Actions
    fetchUser: () => Promise<void>;
    toggleTheme: () => void;
    setJobsFilter: (filter: string) => void;

    // Upload queue
    uploadQueue: UploadQueueItem[];
    uploadCompletedAt: number | null;
    enqueueUploads: (items: UploadInput[]) => void;
    clearCompletedUploads: () => void;
}

export const useStore = create<AppState>()(
    persist(
        (set) => ({
            user: null,
            theme: 'light',
            jobsFilter: 'all',
            uploadQueue: [],
            uploadCompletedAt: null,

            fetchUser: async () => {
                try {
                    const user = await api.getMe();
                    set({ user });
                } catch {
                    // dev backend not running yet — leave user null
                }
            },

            toggleTheme: () => {
                set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' }));
            },

            setJobsFilter: (filter: string) => {
                set({ jobsFilter: filter });
            },

            enqueueUploads: (items: UploadInput[]) => {
                const queueItems: UploadQueueItem[] = items.map(item => ({
                    id: Math.random().toString(36).slice(2, 10),
                    filename: item.file.name,
                    fileSize: item.file.size,
                    type: item.type,
                    status: 'uploading' as const,
                    progress: 0,
                }));

                set(state => ({ uploadQueue: [...state.uploadQueue, ...queueItems] }));

                const updateItem = (id: string, updates: Partial<UploadQueueItem>) => {
                    set(state => ({
                        uploadQueue: state.uploadQueue.map(q =>
                            q.id === id ? { ...q, ...updates } : q
                        ),
                    }));
                };

                const promises = items.map((item, i) => {
                    const id = queueItems[i].id;
                    return uploadFileXHR(
                        item.file,
                        item.type,
                        item.additionalContext || undefined,
                        (pct) => updateItem(id, { progress: pct }),
                        () => updateItem(id, { status: 'parsing', progress: 100 }),
                    ).then(() => {
                        updateItem(id, { status: 'done', progress: 100 });
                    }).catch((err: unknown) => {
                        const msg = err instanceof Error ? err.message : 'Upload failed';
                        updateItem(id, { status: 'error', error: msg });
                    });
                });

                Promise.allSettled(promises).then(() => {
                    set({ uploadCompletedAt: Date.now() });
                });
            },

            clearCompletedUploads: () => {
                set(state => ({
                    uploadQueue: state.uploadQueue.filter(
                        q => q.status !== 'done' && q.status !== 'error'
                    ),
                }));
            },
        }),
        {
            name: 'wand-storage',
            partialize: (state) => ({ theme: state.theme, jobsFilter: state.jobsFilter }),
        }
    )
);
