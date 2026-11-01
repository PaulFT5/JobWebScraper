<script lang="ts">
    import type { Job } from '$lib/types';

    let { jobs }: { jobs: Job[] } = $props();

    // career order, not count order; the DB value Fără means no experience required
    const STAGES: { value: string; label: string }[] = [
        { value: 'Fără', label: 'No experience (Fără)' },
        { value: 'Entry', label: 'Entry' },
        { value: 'Middle', label: 'Mid-level' },
        { value: 'Senior', label: 'Senior' },
        { value: 'Executive', label: 'Executive' }
    ];

    const counts = $derived(STAGES.map((s) => ({ ...s, n: jobs.filter((j) => j.experience_level === s.value).length })));
    const known = $derived(counts.reduce((a, c) => a + c.n, 0));
    const unspecified = $derived(jobs.length - known);
    const max = $derived(Math.max(1, ...counts.map((c) => c.n)));
</script>

<section class="rounded-xl border border-slate-200 bg-white p-4">
    <header class="-mx-4 -mt-4 mb-3 rounded-t-xl border-b border-(--card-head-border) bg-(--card-head-bg) px-4 py-3">
        <h3 class="text-sm font-semibold text-(--card-head-fg)">
            Experience level: {known.toLocaleString()} specified out of {jobs.length.toLocaleString()} jobs found
        </h3>
    </header>
    <ol class="space-y-1.5" aria-label="Ads per experience level">
        {#each counts as c (c.value)}
            <li class="grid grid-cols-[11rem_1fr] items-center gap-3 px-1 text-xs">
                <span class="text-slate-700">{c.label}</span>
                <span class="flex items-center gap-2">
                    <span class="h-4 shrink-0 rounded-r-[4px] bg-(--bar-level)" style="width: calc((100% - 6.5rem) * {c.n / max})"></span>
                    <span class="font-mono text-[11px] whitespace-nowrap text-slate-700">
                        {c.n.toLocaleString()} <span class="text-slate-400">·</span> {known ? ((c.n / known) * 100).toFixed(1) : '0.0'}%
                    </span>
                </span>
            </li>
        {/each}
    </ol>
</section>
