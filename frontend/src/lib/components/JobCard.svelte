<script lang="ts">
    import type { Job } from '$lib/types';
    import { scoreTheme } from '$lib/score';
    import { parseSkills, companyInitials, salaryInfo, experienceLabel } from '$lib/jobs';

    let { job, score, selected = false, onSelect, onDetails }: {
        job: Job;
        score?: number;
        selected?: boolean;
        onSelect: (job: Job) => void;
        onDetails: (job: Job) => void;
    } = $props();

    function onKeydown(e: KeyboardEvent) {
        // keys pressed on the inner button belong to that button
        if (e.target !== e.currentTarget) return;
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSelect(job);
        }
    }

    const SHOWN_SKILLS = 3;

    const initials = $derived(companyInitials(job.company));
    const allSkills = $derived(parseSkills(job.required_skills));
    const skills = $derived(allSkills.slice(0, SHOWN_SKILLS));
    const hiddenSkills = $derived(allSkills.length - skills.length);
    const salary = $derived(salaryInfo(job));
    const experience = $derived(experienceLabel(job));

    const theme = $derived(score === undefined ? null : scoreTheme(score));
</script>

<div
    class="group flex scroll-my-3 cursor-pointer flex-col rounded-lg border p-3 shadow-sm transition-colors
           focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-500
           {selected ? 'border-teal-500 bg-teal-50/70 ring-2 ring-teal-500' : 'border-slate-200 bg-white hover:border-teal-300'}"
    data-job-key={job.source + '/' + job.slug}
    role="button"
    tabindex="0"
    aria-pressed={selected}
    onclick={() => onSelect(job)}
    onkeydown={onKeydown}
>
    <div class="flex items-start gap-2.5">
        <div class="flex size-8 shrink-0 items-center justify-center rounded-md bg-teal-700 text-xs font-bold text-white">
            {initials}
        </div>

        <div class="min-w-0 flex-1">
            <h3 class="truncate text-sm font-semibold text-slate-900 group-hover:text-teal-700">{job.title}</h3>
            <p class="truncate text-xs text-slate-500">{job.company}</p>
        </div>

        {#if score !== undefined && theme}
            <span class="rounded-full border px-1.5 py-0.5 font-mono text-[13px] {theme.badge}">
                {score}%
            </span>
        {/if}
    </div>

    <!-- Metadata 2×2: city, domain / work type, experience; fixed height keeps cards even -->
    <div class="mt-2.5 grid h-9 grid-cols-2 content-start gap-x-3 gap-y-1 text-xs text-slate-500">
        {#if job.city}
            <span class="flex min-w-0 items-center gap-1 capitalize">
                <svg class="size-3 shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" /><circle cx="12" cy="10" r="3" />
                </svg>
                <span class="truncate">{job.city}</span>
            </span>
        {/if}
        {#if job.domain}
            <span class="flex min-w-0 items-center gap-1">
                <svg class="size-3 shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" /><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" /><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2" /><path d="M10 6h4" /><path d="M10 10h4" /><path d="M10 14h4" /><path d="M10 18h4" />
                </svg>
                <span class="truncate">{job.domain}</span>
            </span>
        {/if}
        {#if job.work_type}
            <span class="flex min-w-0 items-center gap-1">
                <svg class="size-3 shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                </svg>
                <span class="truncate">{job.work_type}</span>
            </span>
        {/if}
        {#if experience}
            <span class="flex min-w-0 items-center gap-1">
                <svg class="size-3 shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z" /><path d="M22 10v6" /><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5" />
                </svg>
                <span class="truncate">{experience}</span>
            </span>
        {/if}
    </div>

    <!-- Skills: first few, the rest as a count -->
    <div class="mt-2.5 flex h-5 flex-wrap gap-1 overflow-hidden">
        {#each skills as skill (skill)}
            <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-600">{skill}</span>
        {/each}
        {#if hiddenSkills > 0}
            <span class="px-1 py-0.5 text-[10px] text-slate-400">+{hiddenSkills} more</span>
        {/if}
    </div>

    <p class="mt-2.5 h-4 text-xs">
        {#if salary}
            <span class="text-slate-500">Salary:</span>
            <span class="font-mono font-bold">{salary.value} € / month</span>
            {#if salary.estimated}
                <span class="text-slate-400">(estimated)</span>
            {/if}
        {/if}
    </p>

    <div class="mt-3 flex items-center gap-3">
        {#if score !== undefined && theme}
            <div class="h-1 flex-1 rounded-full bg-slate-100">
                <div
                    class="h-full rounded-full transition-all duration-300 {theme.bar}"
                    style="width: {Math.min(Math.max(score, 0), 100)}%"
                ></div>
            </div>
        {/if}

        <button
            type="button"
            class="ml-auto flex cursor-pointer items-center gap-1 rounded border border-teal-300 bg-teal-50 px-2 py-1 text-xs text-teal-700 hover:bg-teal-100 focus-visible:outline-2 focus-visible:outline-teal-500"
            onclick={(e) => {
                e.stopPropagation(); // details only, not a selection
                onDetails(job);
            }}
        >
            View details
        </button>
    </div>
</div>
