import { API } from './config';
import type { Job, MatchReport, MatchResponse } from '$lib/types';

async function errorMessage(res: Response): Promise<string> {
    try {
        const body = await res.json();
        if (typeof body?.detail === 'string') return body.detail;
    } catch {
        // not JSON
    }
    return `HTTP ${res.status}`;
}

// The PDF goes as the raw request body; the API parses, grounds and scores it against every available job.
export async function uploadCv(file: File): Promise<MatchResponse> {
    const res = await fetch(`${API}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/pdf' },
        body: file
    });
    if (!res.ok) throw new Error(await errorMessage(res));
    return await res.json();
}

export async function fetchMatchDetail(sessionId: string, job: Job): Promise<MatchReport> {
    const path = [sessionId, job.source, job.slug].map(encodeURIComponent).join('/');
    const res = await fetch(`${API}/match/${path}`);
    if (!res.ok) throw new Error(await errorMessage(res));
    return await res.json();
}
