import { EXPERIENCE_LABELS } from '$lib/jobs';

export type Option = { id: string | number; name: string };

type FilterState = {
    cities: (string | number)[];
    work_types: (string | number)[];
    domains: (string | number)[];
    // applied in the frontend, not sent to the API
    experience_levels: (string | number)[];
    salary_kinds: (string | number)[];
};

export const experienceOptions: Option[] = Object.entries(EXPERIENCE_LABELS).map(([id, name]) => ({ id, name }));

export const salaryOptions: Option[] = [
    { id: 'listed', name: 'Listed salary' },
    { id: 'estimated', name: 'Estimated salary' },
    { id: 'none', name: 'No salary' }
];

const empty = (): FilterState => ({ cities: [], work_types: [], domains: [], experience_levels: [], salary_kinds: [] });

export const selected = $state<FilterState>(empty());
export const applied = $state<FilterState>(empty());

const keys = ['cities', 'work_types', 'domains', 'experience_levels', 'salary_kinds'] as const;

const sameSet = (a: (string | number)[], b: (string | number)[]) =>
    a.length === b.length && a.every((v) => b.includes(v));

// true when the checked boxes differ from what the list currently shows
export function isDirty() {
    return keys.some((key) => !sameSet(selected[key], applied[key]));
}

export function appliedCount() {
    return keys.reduce((sum, key) => sum + applied[key].length, 0);
}

export function applyFilters() {
    // only touch changed groups, so a salary-only change doesn't refetch from the API
    for (const key of keys) {
        if (!sameSet(selected[key], applied[key])) applied[key] = [...selected[key]];
    }
}

export function resetFilters() {
    for (const key of keys) {
        selected[key] = [];
        applied[key] = [];
    }
}
