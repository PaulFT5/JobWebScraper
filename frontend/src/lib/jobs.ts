import type { Job } from '$lib/types';

export const jobKey = (job: Job) => job.source + '/' + job.slug;

export function parseSkills(raw: string | null): string[] {
    if (!raw) return [];
    try {
        const list = JSON.parse(raw);
        return Array.isArray(list) ? list.filter((s) => s !== '__EXTRACTION_FAILED__') : [];
    } catch {
        return [];
    }
}

export function companyInitials(company: string | null): string {
    return (company || '?')
        .split(/\s+/)
        .slice(0, 2)
        .map((w) => w[0])
        .join('')
        .toUpperCase();
}

// listed salary wins; the estimate is only used when there is none
export function salaryInfo(job: Job): { value: string; estimated: boolean } | null {
    if (job.salary) return { value: job.salary, estimated: false };
    if (job.estimated_salary) return { value: job.estimated_salary, estimated: true };
    return null;
}

export type SalaryKind = 'listed' | 'estimated' | 'none';

// same rule as salaryInfo: a listed salary wins over the estimate
export function salaryKind(job: Job): SalaryKind {
    const info = salaryInfo(job);
    return !info ? 'none' : info.estimated ? 'estimated' : 'listed';
}

// DB value → display label; jobs without a level use 'none'
export const EXPERIENCE_LABELS: Record<string, string> = {
    none: 'Not specified',
    Fără: 'No experience',
    Entry: 'Entry',
    Middle: 'Mid-level',
    Senior: 'Senior',
    Executive: 'Executive'
};

export const experienceKind = (job: Job): string => job.experience_level ?? 'none';

// null when the job has no level, so cards can hide it
export function experienceLabel(job: Job): string | null {
    if (!job.experience_level) return null;
    return EXPERIENCE_LABELS[job.experience_level] ?? job.experience_level;
}

// lower bound of "1220 - 1350" style values, for sorting
export function salaryFloor(job: Job): number | null {
    const info = salaryInfo(job);
    const match = info?.value.match(/\d[\d.,]*/);
    return match ? Number(match[0].replace(/[.,]/g, '')) : null;
}
