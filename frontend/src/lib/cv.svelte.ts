import type { CvSkill } from '$lib/types';

// The uploaded CV and its match results. Lives in the page only (the API keeps the grounded CV in memory).
// status: idle = no CV, analyzing = upload in progress, ready = scores available, error = upload failed
export const cv = $state({
    fileName: null as string | null,
    status: 'idle' as 'idle' | 'analyzing' | 'ready' | 'error',
    error: null as string | null,
    sessionId: null as string | null,
    skills: [] as CvSkill[],
    // job key ("source/slug") -> Chamfer score 0-100
    scores: {} as Record<string, number>
});

export function clearCv() {
    cv.fileName = null;
    cv.status = 'idle';
    cv.error = null;
    cv.sessionId = null;
    cv.skills = [];
    cv.scores = {};
}
