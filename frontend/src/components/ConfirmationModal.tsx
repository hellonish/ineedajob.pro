'use client';

import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';

interface ConfirmationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    isDestructive?: boolean;
}

export default function ConfirmationModal({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    isDestructive = false
}: ConfirmationModalProps) {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setMounted(true);
        return () => setMounted(false);
    }, []);

    if (!mounted) return null;

    return createPortal(
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999]"
                    />

                    {/* Modal */}
                    <div className="fixed inset-0 flex items-center justify-center z-[10000] pointer-events-none p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 10 }}
                            className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl shadow-2xl w-full max-w-sm pointer-events-auto overflow-hidden bg-[#111118]"
                        >
                            <div className="p-6">
                                <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">
                                    {title}
                                </h3>
                                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                                    {message}
                                </p>
                            </div>

                            <div className="bg-[var(--bg-secondary)/50] px-6 py-4 flex gap-3 justify-end border-t border-[var(--border-color)]">
                                <button
                                    onClick={onClose}
                                    className="px-4 py-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded-lg transition-colors cursor-pointer"
                                >
                                    {cancelLabel}
                                </button>
                                <button
                                    onClick={() => {
                                        onConfirm();
                                        onClose();
                                    }}
                                    className={`px-4 py-2 text-sm font-medium text-white rounded-lg shadow-lg transition-all transform hover:scale-105 cursor-pointer ${isDestructive
                                        ? 'bg-red-600 hover:bg-red-700 shadow-red-500/20'
                                        : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-500/20'
                                        }`}
                                >
                                    {confirmLabel}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>,
        document.body
    );
}
