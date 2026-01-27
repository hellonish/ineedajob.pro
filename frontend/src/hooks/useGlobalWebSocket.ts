import { useEffect, useRef } from 'react';
import { useStore } from '@/utils/store';

const WS_URL = 'ws://localhost:8000/ws';

export function useGlobalWebSocket() {
    const { token, updateQueueItem, removeFromQueue } = useStore();
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!token) return;

        // Create WebSocket connection
        const ws = new WebSocket(`${WS_URL}/${token}`);

        ws.onopen = () => {
            console.log('[WebSocket] Connected globally');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('[WebSocket] Message:', data);

                if (data.type === 'job_update') {
                    const jobId = data.job_id;

                    // Map backend status to frontend queue status
                    let frontendStatus: 'pending' | 'analyzing' | 'complete' | 'error';
                    if (data.status === 'processing') {
                        frontendStatus = 'analyzing';
                    } else if (data.status === 'completed') {
                        frontendStatus = 'complete';
                    } else if (data.status === 'failed') {
                        frontendStatus = 'error';
                    } else {
                        frontendStatus = 'pending';
                    }

                    // Update the queue item
                    updateQueueItem(jobId, {
                        status: frontendStatus,
                        error: data.status === 'failed' ? (data.data?.message || 'Analysis failed') : undefined,
                    });

                    // Auto-remove completed/failed items after a delay
                    if (data.status === 'completed' || data.status === 'failed') {
                        setTimeout(() => {
                            removeFromQueue(jobId);
                        }, 3000); // 3 second delay to show the status
                    }
                }
            } catch (err) {
                console.error('[WebSocket] Parse error:', err);
            }
        };

        ws.onerror = (error) => {
            console.error('[WebSocket] Error:', error);
        };

        ws.onclose = () => {
            console.log('[WebSocket] Disconnected');
        };

        wsRef.current = ws;

        // Cleanup on unmount or token change
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [token, updateQueueItem, removeFromQueue]);

    return wsRef;
}
