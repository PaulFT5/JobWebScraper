import type { Job } from '$lib/types';

// job: the one compared with the CV (picked by clicking a card)
// details: the one shown in the details popup, independent of the comparison
export const selection = $state({ job: null as Job | null, details: null as Job | null });

export function selectJob(job: Job) {
    selection.job = job;
}

export function showDetails(job: Job) {
    selection.details = job;
}

export function closeDetails() {
    selection.details = null;
}
