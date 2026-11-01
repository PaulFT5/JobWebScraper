import { API } from './config';

export type ProblemAd = { slug: string; title: string; company: string | null; domain: string | null; ad_link: string | null };

// GET /api/analyzer/coverage — spec in docs/MATCHING_ROADMAP.md (Analyzer page → coverage endpoint)
export type Coverage = {
    available: number;
    with_description: number;
    extracted: number;
    waiting: number;
    no_description: number;
    empty: number;
    failed: number;
    no_description_processed: number;
    queued_by_domain: { domain: string; queued: number }[];
    problem_ads: { empty: ProblemAd[]; failed: ProblemAd[]; no_description_processed: ProblemAd[] };
};

// 'missing' = the endpoint isn't implemented yet (404), so the UI can say so instead of failing
export type CoverageResult = { status: 'ready'; data: Coverage } | { status: 'missing' } | { status: 'error' };

export async function fetchCoverage(): Promise<CoverageResult> {
    try {
        const res = await fetch(`${API}/analyzer/coverage`);
        if (res.status === 404) return { status: 'missing' };
        if (!res.ok) return { status: 'error' };
        return { status: 'ready', data: await res.json() };
    } catch {
        return { status: 'error' };
    }
}
