import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, api, setToken, clearToken } from './api';

interface AppState {
    // Auth
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    _hasHydrated: boolean;

    // Theme
    theme: 'dark' | 'light';

    // Jobs Filter
    jobsFilter: string;

    // Actions
    login: (token: string) => Promise<void>;
    logout: () => void;
    fetchUser: () => Promise<void>;
    toggleTheme: () => void;
    setHasHydrated: (state: boolean) => void;

    // Jobs Filter Actions
    setJobsFilter: (filter: string) => void;

}

export const useStore = create<AppState>()(
    persist(
        (set, get) => ({
            // Initial State
            user: null,
            token: null,
            isAuthenticated: false,
            _hasHydrated: false,
            theme: 'light',
            jobsFilter: 'all',

            setHasHydrated: (state: boolean) => {
                set({ _hasHydrated: state });
            },

            // Auth Actions
            login: async (token: string) => {
                setToken(token);
                set({ token, isAuthenticated: true });
                await get().fetchUser();
            },

            logout: () => {
                clearToken();
                set({ user: null, token: null, isAuthenticated: false });
            },

            fetchUser: async () => {
                try {
                    const user = await api.getMe();
                    set({ user, isAuthenticated: true });
                } catch {
                    get().logout();
                }
            },

            toggleTheme: () => {
                set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' }));
            },

            setJobsFilter: (filter: string) => {
                set({ jobsFilter: filter });
            },
        }),
        {
            name: 'wand-storage',
            partialize: (state) => ({ token: state.token, theme: state.theme, jobsFilter: state.jobsFilter }),
            onRehydrateStorage: () => (state) => {
                // When store hydrates from localStorage, sync token to api.ts
                if (state) {
                    // Recovery: If store has no token but localStorage does (e.g. from login redirect), use it
                    const rawToken = localStorage.getItem('token');
                    if (!state.token && rawToken) {
                        state.token = rawToken;
                        state.isAuthenticated = true; // Will be verified by fetchUser later
                    }

                    // Sync api.ts with store state
                    if (state.token) {
                        setToken(state.token);
                    } else {
                        // If store has no token, ensure api.ts matches
                        clearToken();
                    }

                    state.setHasHydrated(true);
                }
            },
        }
    )
);
