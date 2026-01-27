'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, Discrepancy } from '@/utils/api';
import Header from '@/components/Header';
import { usePageUnloadWarning } from '@/hooks/usePageUnloadWarning';
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

    // Warn if user tries to refresh/leave while generating
    usePageUnloadWarning(generating, "Discrepancy check in progress. Leaving now will cancel the operation.");

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
            // Fetch latest profile to ensure we have unified data
            const profile = await api.getProfile();

            if (!profile.unified_profile) {
                alert('Please generate a Unified Profile first in the Profile section.');
                router.push('/profile');
                return;
            }

            const result = await api.createDiscrepancy({
                unified_profile: profile.unified_profile
            });

            setReports([result, ...reports]);
            setSelectedReport(result);
        } catch (error) {
            console.error(error);
            alert('Failed to run discrepancy check');
        } finally {
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
            <div className="min-h-screen">
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                </div>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[var(--bg-primary)]">
            <Header />

            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Discrepancy Check</h1>
                        <p className="text-[var(--text-secondary)]">Detect inconsistencies across your profile data sources.</p>
                    </div>
                    <button
                        onClick={handleRunCheck}
                        disabled={generating}
                        className={`px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-lg shadow-indigo-500/20 transition-all hover:scale-105 cursor-pointer flex items-center gap-2 ${generating ? 'opacity-50 cursor-not-allowed' : ''
                            }`}
                    >
                        {generating ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Checking...
                            </>
                        ) : (
                            <>
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Run Check
                            </>
                        )}
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                    {/* List Column */}
                    <div className="lg:col-span-1 space-y-4">
                        <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl p-4">
                            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-4">Past Reports</h3>
                            {reports.length === 0 ? (
                                <p className="text-sm text-[var(--text-muted)] text-center py-4">No reports yet.</p>
                            ) : (
                                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                                    {reports.map((report) => (
                                        <button
                                            key={report.id}
                                            onClick={() => setSelectedReport(report)}
                                            className={`w-full text-left p-3 rounded-lg border transition-all cursor-pointer group flex items-center justify-between ${selectedReport?.id === report.id
                                                ? 'bg-indigo-500/10 border-indigo-500 text-indigo-400'
                                                : 'border-[var(--border-color)] hover:border-[var(--text-muted)] text-[var(--text-primary)]'
                                                }`}
                                        >
                                            <div>
                                                <div className="text-sm font-medium">Report</div>
                                                <div className="text-xs text-[var(--text-muted)]">
                                                    {new Date(report.created_at).toLocaleString()}
                                                </div>
                                            </div>
                                            <div
                                                onClick={(e) => confirmDelete(report.id, e)}
                                                className="p-1.5 rounded-full hover:bg-red-500/20 text-[var(--text-muted)] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                                                title="Delete Report"
                                            >
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Detail Column */}
                    <div className="lg:col-span-3">
                        {selectedReport ? (
                            <motion.div
                                key={selectedReport.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl p-8"
                            >
                                <div className="flex items-center justify-between mb-6 pb-6 border-b border-[var(--border-color)]">
                                    <h2 className="text-xl font-bold text-[var(--text-primary)]">Analysis Results</h2>
                                    <span className="text-sm text-[var(--text-muted)]">
                                        {new Date(selectedReport.created_at).toLocaleString()}
                                    </span>
                                </div>



                                <div className="prose max-w-none text-[var(--text-primary)]">
                                    {selectedReport.result ? (
                                        typeof selectedReport.result === 'string' ? (
                                            // Fallback for legacy text-only reports
                                            <ReactMarkdown>{selectedReport.result}</ReactMarkdown>
                                        ) : (
                                            // New Structured View
                                            <DiscrepancyReportView data={selectedReport.result} />
                                        )
                                    ) : (
                                        <p>No discrepancies found or analysis pending.</p>
                                    )}
                                </div>
                            </motion.div>
                        ) : (
                            <div className="bg-[var(--card-bg)] border border-[var(--border-color)] border-dashed rounded-xl p-12 flex flex-col items-center justify-center text-center text-[var(--text-muted)] h-full min-h-[400px]">
                                <svg className="w-16 h-16 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <p className="text-lg font-medium">Select a report to view details</p>
                                <p className="text-sm">or click "Run Check" to start a new analysis</p>
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
