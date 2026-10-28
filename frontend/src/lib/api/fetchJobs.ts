import { API } from './config';
import type { Job } from '$lib/types';

export async function fetchJobs(filters: {
    domains: (string | number)[];
    work_types: (string | number)[];
    cities: (string | number)[];
}): Promise<Job[]> {
    const params = new URLSearchParams();
    filters.domains.forEach((d) => params.append('domains', String(d)));
    filters.work_types.forEach((w) => params.append('work_types', String(w)));
    filters.cities.forEach((c) => params.append('cities', String(c)));

    const res = await fetch(`${API}/jobs?${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
}