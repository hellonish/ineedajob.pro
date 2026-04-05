'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, Discrepancy } from '@/utils/api';
import Header from '@/components/Header';
import { subscribeToDiscrepancy } from '@/hooks/useGlobalWebSocket';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import ConfirmationModal from '@/components/ConfirmationModal';
import DiscrepancyReportView from '@/components/DiscrepancyReportView';

export default function DiscrepanciesPage() {
    const router = useRouter();
    const { token, isAuthenticated, _hasHydrated } = useStore();

    const [reports, setReports] = useState<Discrepancy[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [selectedReport, setSelectedReport] = useState<Discrepancy | null>(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [reportToDelete, setReportToDelete] = useState<string | null>(null);
    const [hoveredReport, setHoveredReport] = useState<string | null>(null);
    const [runBtnHovered, setRunBtnHovered] = useState(false);

    // Subscribe to WebSocket discrepancy events
    useEffect(() => {
        const unsub = subscribeToDiscrepancy((data) => {
            if (data.type === 'discrepancy_complete') {
                const id = data.discrepancy_id as string;
                const result = data.result as Record<string, unknown>;
                setReports(prev => prev.map(r =>
                    r.id === id ? { ...r, result } : r
                ));
                setSelectedReport(prev =>
                    prev?.id === id ? { ...prev, result } : prev
                );
                setGenerating(false);
            } else if (data.type === 'discrepancy_failed') {
                setGenerating(false);
            }
        });
        return unsub;
    }, []);

    useEffect(() => {
        if (!_hasHydrated) return;
        if (!token) {
            router.push('/');
            return;
        }
        loadData();
    }, [token, _hasHydrated]);

    const loadData = async () => {
        try {
            const data = await api.getDiscrepancies().catch(() => []);
            setReports(data);
            if (data.length > 0 && !selectedReport) {
                setSelectedReport(data[0]);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleRunCheck = async () => {
        if (generating) return;
        setGenerating(true);
        try {
            const profile = await api.getProfile();
            if (!profile.unified_profile) {
                alert('Please generate a Unified Profile first in the Profile section.');
                router.push('/profile');
                setGenerating(false);
                return;
            }

            // Returns immediately with result=null — WS event will deliver the result
            const pending = await api.createDiscrepancy({ unified_profile: profile.unified_profile });
            setReports(prev => [pending, ...prev]);
            setSelectedReport(pending);
            // generating stays true until WS discrepancy_complete/failed fires
        } catch (error) {
            console.error(error);
            alert('Failed to start discrepancy check');
            setGenerating(false);
        }
    };

    const confirmDelete = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setReportToDelete(id);
        setShowDeleteModal(true);
    };

    const handleDelete = async () => {
        if (!reportToDelete) return;
        try {
            await api.deleteDiscrepancy(reportToDelete);
            const updatedReports = reports.filter(r => r.id !== reportToDelete);
            setReports(updatedReports);
            if (selectedReport?.id === reportToDelete) {
                setSelectedReport(updatedReports[0] || null);
            }
        } catch (error) {
            console.error('Failed to delete report:', error);
            alert('Failed to delete report');
        } finally {
            setShowDeleteModal(false);
            setReportToDelete(null);
        }
    };

    if (!_hasHydrated || !isAuthenticated || loading) {
        return (
            <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div
                        className="w-6 h-6 rounded-full border-2 animate-spin"
                        style={{
                            borderColor: 'var(--border-strong)',
                            borderTopColor: 'var(--accent)',
                        }}
                    />
                </div>
            </div>
        );
    }

    return (
        <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
            <Header />

            <div className="max-w-screen-xl mx-auto px-8 py-6">
                {/* Page header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1
                            className="text-lg font-semibold"
                            style={{ color: 'var(--text-1)' }}
                        >
                            Discrepancy Check
                        </h1>
                        <p
                            className="text-sm mt-0.5"
                            style={{ color: 'var(--text-3)' }}
                        >
                            Detect inconsistencies across your profile sources
                        </p>
                    </div>

                    <button
                        onClick={handleRunCheck}
                        disabled={generating}
                        onMouseEnter={() => setRunBtnHovered(true)}
                        onMouseLeave={() => setRunBtnHovered(false)}
                        className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md border cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        style={{
                            borderColor: runBtnHovered && !generating ? 'var(--accent-border)' : 'var(--border-strong)',
                            color: runBtnHovered && !generating ? 'var(--text-1)' : 'var(--text-2)',
                            background: 'transparent',
                        }}
                    >
                        {generating ? (
                            <>
                                <div
                                    className="w-3.5 h-3.5 rounded-full border-2 animate-spin"
                                    style={{
                                        borderColor: 'var(--border-strong)',
                                        borderTopColor: 'var(--accent)',
                                    }}
                                />
                                Checking…
                            </>
                        ) : (
                            <>
                                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Run Check
                            </>
                        )}
                    </button>
                </div>

                {/* Main grid */}
                <div className="grid gap-6" style={{ gridTemplateColumns: '260px 1fr' }}>

                    {/* Left panel — reports list */}
                    <div
                        className="rounded-lg overflow-hidden"
                        style={{
                            border: '1px solid var(--border)',
                            height: 'fit-content',
                        }}
                    >
                        {/* Panel header */}
                        <div
                            className="px-4 py-3 text-xs uppercase tracking-widest"
                            style={{
                                color: 'var(--text-3)',
                                background: 'var(--surface)',
                                borderBottom: '1px solid var(--border)',
                                letterSpacing: '0.08em',
                            }}
                        >
                            Reports
                        </div>

                        {reports.length === 0 ? (
                            <div
                                className="px-4 py-8 text-sm text-center"
                                style={{ color: 'var(--text-3)' }}
                            >
                                No reports yet.
                            </div>
                        ) : (
                            <div>
                                {reports.map((report) => {
                                    const isSelected = selectedReport?.id === report.id;
                                    const isHovered = hoveredReport === report.id;
                                    return (
                                        <div
                                            key={report.id}
                                            onClick={() => setSelectedReport(report)}
                                            onMouseEnter={() => setHoveredReport(report.id)}
                                            onMouseLeave={() => setHoveredReport(null)}
                                            className="relative flex items-center justify-between px-4 py-3 cursor-pointer group"
                                            style={{
                                                borderBottom: '1px solid var(--border)',
                                                borderLeft: isSelected ? '2px solid var(--accent)' : '2px solid transparent',
                                                background: isSelected
                                                    ? 'var(--accent-dim)'
                                                    : isHovered
                                                        ? 'var(--hover)'
                                                        : 'transparent',
                                            }}
                                        >
                                            <div>
                                                <div
                                                    className="text-sm"
                                                    style={{ color: 'var(--text-1)' }}
                                                >
                                                    Report
                                                </div>
                                                <div
                                                    className="text-xs font-mono mt-0.5"
                                                    style={{ color: 'var(--text-3)' }}
                                                >
                                                    {new Date(report.created_at).toLocaleString()}
                                                </div>
                                            </div>

                                            <DeleteIcon
                                                visible={isHovered}
                                                onClick={(e) => confirmDelete(report.id, e)}
                                            />
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Right panel — report detail */}
                    <div
                        className="rounded-lg min-h-[400px]"
                        style={{ border: '1px solid var(--border)' }}
                    >
                        {selectedReport ? (
                            <motion.div
                                key={selectedReport.id}
                                initial={{ opacity: 0, y: 6 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-6 h-full"
                            >
                                <div
                                    className="text-xs font-mono mb-5 pb-4"
                                    style={{
                                        color: 'var(--text-3)',
                                        borderBottom: '1px solid var(--border)',
                                    }}
                                >
                                    {new Date(selectedReport.created_at).toLocaleString()}
                                </div>

                                <div className="prose max-w-none" style={{ color: 'var(--text-1)' }}>
                                    {selectedReport.result ? (
                                        typeof selectedReport.result === 'string' ? (
                                            <ReactMarkdown>{selectedReport.result}</ReactMarkdown>
                                        ) : (
                                            <DiscrepancyReportView data={selectedReport.result} />
                                        )
                                    ) : (
                                        <div className="flex flex-col items-center justify-center py-16 gap-3">
                                            <div
                                                className="w-5 h-5 rounded-full border-2 animate-spin"
                                                style={{ borderColor: 'var(--border-strong)', borderTopColor: 'var(--accent)' }}
                                            />
                                            <p className="text-sm" style={{ color: 'var(--text-3)' }}>
                                                Analysis running — you can navigate away freely.
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ) : (
                            <div
                                className="flex items-center justify-center h-full min-h-[400px] text-sm"
                                style={{ color: 'var(--text-3)' }}
                            >
                                Select a report or run a new check.
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <ConfirmationModal
                isOpen={showDeleteModal}
                title="Delete Report"
                message="Are you sure you want to delete this discrepancy report? This action cannot be undone."
                confirmLabel="Delete Report"
                cancelLabel="Cancel"
                onConfirm={handleDelete}
                onClose={() => setShowDeleteModal(false)}
                isDestructive={true}
            />
        </main>
    );
}

function DeleteIcon({
    visible,
    onClick,
}: {
    visible: boolean;
    onClick: (e: React.MouseEvent) => void;
}) {
    const [hovered, setHovered] = useState(false);

    return (
        <div
            onClick={onClick}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            className="p-1 rounded transition-opacity"
            style={{
                opacity: visible ? 1 : 0,
                color: hovered ? '#f87171' : 'var(--text-3)',
                pointerEvents: visible ? 'auto' : 'none',
            }}
            title="Delete Report"
        >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
        </div>
    );
}
