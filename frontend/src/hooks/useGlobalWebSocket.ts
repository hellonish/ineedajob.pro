import { useEffect, useRef } from 'react';
import { useStore } from '@/utils/store';

const WS_URL = 'ws://localhost:8000/ws';

// Global event emitter for discrepancy completion
type DiscrepancyHandler = (data: Record<string, unknown>) => void;
const discrepancyListeners: Set<DiscrepancyHandler> = new Set();

export function subscribeToDiscrepancy(handler: DiscrepancyHandler): () => void {
    discrepancyListeners.add(handler);
    return () => { discrepancyListeners.delete(handler); };
}

function emitDiscrepancy(data: Record<string, unknown>) {
    discrepancyListeners.forEach(fn => fn(data));
}

// Global event emitter for JobLens step updates
type JobLensEventType =
    | 'joblens_step_started'
    | 'joblens_step_complete'
    | 'joblens_step_failed'
    | 'joblens_pipeline_complete'
    | 'joblens_pipeline_failed';

type JobLensHandler = (data: Record<string, unknown>) => void;

const joblensListeners: Map<string, Set<JobLensHandler>> = new Map();

export function subscribeToJobLens(sessionId: string, handler: JobLensHandler): () => void {
    if (!joblensListeners.has(sessionId)) {
        joblensListeners.set(sessionId, new Set());
    }
    joblensListeners.get(sessionId)!.add(handler);
    return () => {
        joblensListeners.get(sessionId)?.delete(handler);
    };
}

function emitJobLens(sessionId: string, data: Record<string, unknown>) {
    joblensListeners.get(sessionId)?.forEach(fn => fn(data));
}

export function useGlobalWebSocket() {
    const { token } = useStore();
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!token) return;

        const ws = new WebSocket(`${WS_URL}/${token}`);

        ws.onopen = () => {
            console.log('[WebSocket] Connected globally');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Discrepancy events
                if (data.type === 'discrepancy_complete' || data.type === 'discrepancy_failed') {
                    emitDiscrepancy(data);
                }

                // JobLens step events — route to per-session listeners
                const joblensTypes: JobLensEventType[] = [
                    'joblens_step_started',
                    'joblens_step_complete',
                    'joblens_step_failed',
                    'joblens_pipeline_complete',
                    'joblens_pipeline_failed',
                ];
                if (joblensTypes.includes(data.type) && data.session_id) {
                    emitJobLens(data.session_id, data);
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

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [token]);

    return wsRef;
}
