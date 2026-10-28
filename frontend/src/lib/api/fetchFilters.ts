import type { Option } from '$lib/filters.svelte';
import { API } from './config';

export async function fetchFilters(f: typeof fetch = fetch) {
    const res = await f(`${API}/filters`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    return {
        cities: (data.cities as string[]).map((c): Option => ({ id: c, name: c })),
        work_types: data.work_types as Option[],
        domains: data.domains as Option[]
    };
}