<script lang="ts">
    import { parseSkills } from '$lib/jobs';
    import type { Job } from '$lib/types';

    let { jobs }: { jobs: Job[] } = $props();

    const BINS: { label: string; from: number; to: number }[] = [
        { label: '1–3', from: 1, to: 3 },
        { label: '4–6', from: 4, to: 6 },
        { label: '7–9', from: 7, to: 9 },
        { label: '10–12', from: 10, to: 12 },
        { label: '13–15', from: 13, to: 15 },
        { label: '16–20', from: 16, to: 20 },
        { label: '21+', from: 21, to: Infinity }
    ];

    const counted = $derived(jobs.map((j) => ({ job: j, n: parseSkills(j.required_skills).length })).filter((c) => c.n > 0));
    const sorted = $derived(counted.map((c) => c.n).sort((a, b) => a - b));
    const total = $derived(sorted.length);

    const median = $derived(total ? (sorted[Math.floor((total - 1) / 2)] + sorted[Math.ceil((total - 1) / 2)]) / 2 : 0);
    const mean = $derived(total ? sorted.reduce((a, b) => a + b, 0) / total : 0);
    const upTo15 = $derived(total ? (sorted.filter((n) => n <= 15).length / total) * 100 : 0);
    const outlier = $derived(counted.reduce<(typeof counted)[number] | null>((best, c) => (!best || c.n > best.n ? c : best), null));

    const bins = $derived(BINS.map((b) => ({ ...b, count: sorted.filter((n) => n >= b.from && n <= b.to).length })));
    const peak = $derived(Math.max(1, ...bins.map((b) => b.count)));

    // the median line sits inside its bin, at the median's position within the bin's range
    const medianPos = $derived.by(() => {
        const i = BINS.findIndex((b) => median >= b.from && median <= b.to);
        if (i < 0) return null;
        const b = BINS[i];
        const width = (b.to === Infinity ? b.from + 3 : b.to) - b.from + 1;
        return ((i + (median - b.from + 0.5) / width) / BINS.length) * 100;
    });

    const plotH = 180;
</script>

<section class="rounded-xl border border-slate-200 bg-white p-4">
    <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
            <h3 class="text-sm font-semibold text-slate-900">Skills per job</h3>
            <p class="text-xs text-slate-500">
                {total.toLocaleString()} extracted ads · median <strong class="text-slate-700">{median}</strong> · mean
                <strong class="text-slate-700">{mean.toFixed(1)}</strong> · range {sorted[0] ?? 0}–{sorted[total - 1] ?? 0} ·
                {upTo15.toFixed(1)}% have ≤ 15 skills
            </p>
        </div>
        {#if outlier}
            <div class="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1.5 text-[11px] text-slate-600">
                Max: <strong class="text-slate-800">{outlier.n} skills</strong> — {outlier.job.title}{outlier.job.domain ? ` (${outlier.job.domain})` : ''}
                {#if outlier.job.ad_link}
                    <a href={outlier.job.ad_link} target="_blank" rel="noopener noreferrer" class="ml-1 font-semibold text-teal-700 hover:underline">View ad ↗</a>
                {/if}
            </div>
        {/if}
    </div>

    {#if total === 0}
        <p class="mt-4 text-xs text-slate-500">No extracted ads loaded.</p>
    {:else}
        <div class="relative mt-4" style="height: {plotH}px">
            <ul class="absolute inset-0 flex items-end gap-2" aria-label="Number of ads per skill-count range">
                {#each bins as b (b.label)}
                    <li
                        class="flex h-full min-w-0 flex-1 flex-col items-center justify-end"
                        title="{b.label} skills: {b.count.toLocaleString()} ads ({((b.count / total) * 100).toFixed(1)}%)"
                    >
                        <span class="mb-1 font-mono text-[10px] text-slate-600">{b.count}</span>
                        <span class="w-full rounded-t-[4px] bg-(--bar-skills)" style="height: {(b.count / peak) * (plotH - 18)}px"></span>
                    </li>
                {/each}
            </ul>
            {#if medianPos !== null}
                <div class="pointer-events-none absolute inset-y-0 border-l-2 border-dashed border-slate-900" style="left: {medianPos}%" aria-hidden="true">
                    <span class="absolute -top-1 left-1 rounded bg-white px-1 text-[10px] font-semibold text-slate-900">median {median}</span>
                </div>
            {/if}
        </div>
        <div class="mt-1.5 flex gap-2 border-t border-slate-200 pt-1">
            {#each bins as b (b.label)}
                <span class="flex-1 text-center text-[10px] text-slate-500">{b.label}<br /><span class="text-slate-400">{((b.count / total) * 100).toFixed(1)}%</span></span>
            {/each}
        </div>
        <p class="mt-1 text-center text-[10px] text-slate-500">skills per ad</p>
    {/if}
</section>
