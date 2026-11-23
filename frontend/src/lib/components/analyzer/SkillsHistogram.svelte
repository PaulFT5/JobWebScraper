<script lang="ts">
    import { parseSkills } from '$lib/jobs';
    import type { Job } from '$lib/types';

    let { jobs }: { jobs: Job[] } = $props();

    // one point per exact skill count; the long tail from CAP upwards is grouped into one last point
    const CAP = 25;

    const sorted = $derived(jobs.map((j) => parseSkills(j.required_skills).length).filter((n) => n > 0).sort((a, b) => a - b));
    const total = $derived(sorted.length);

    const median = $derived(total ? (sorted[Math.floor((total - 1) / 2)] + sorted[Math.ceil((total - 1) / 2)]) / 2 : 0);

    const points = $derived.by(() => {
        const max = sorted[total - 1] ?? 0;
        const last = Math.min(max, CAP - 1);
        const out: { label: string; count: number }[] = [];
        for (let k = 1; k <= last; k++) out.push({ label: String(k), count: sorted.filter((n) => n === k).length });
        if (max >= CAP) out.push({ label: `${CAP}+`, count: sorted.filter((n) => n >= CAP).length });
        return out;
    });
    const peak = $derived(Math.max(1, ...points.map((p) => p.count)));

    const plotH = 180;
    const topPad = 22;
    const xOf = (i: number) => ((i + 0.5) / points.length) * 100;
    const yOf = (count: number) => plotH - (count / peak) * (plotH - topPad);
    const line = $derived(points.map((p, i) => `${xOf(i)},${yOf(p.count)}`).join(' '));
    const pctOf = (count: number) => ((count / total) * 100).toFixed(1);

    // median sits on the axis at its exact value (between two points when it is a .5)
    const medianPos = $derived(points.length ? xOf(Math.min(median, CAP) - 1) : null);
</script>

<section class="rounded-xl border border-slate-200 bg-white p-4">
    <header class="-mx-4 -mt-4 mb-3 rounded-t-xl border-b border-(--card-head-border) bg-(--card-head-bg) px-4 py-3">
        <h3 class="text-sm font-semibold text-(--card-head-fg)">Skills per job: {total.toLocaleString()} extracted ads</h3>
    </header>
    {#if total === 0}
        <p class="mt-4 text-xs text-slate-500">No extracted ads loaded.</p>
    {:else}
        <div class="relative mt-4" style="height: {plotH}px">
            <svg class="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 100 {plotH}" preserveAspectRatio="none" aria-hidden="true">
                <polyline
                    points={line}
                    fill="none"
                    stroke="var(--bar-skills)"
                    stroke-width="2"
                    stroke-linejoin="round"
                    stroke-linecap="round"
                    vector-effect="non-scaling-stroke"
                />
            </svg>
            <ul class="absolute inset-0" aria-label="Number of ads per skill count">
                {#each points as p, i (p.label)}
                    <li
                        class="absolute -translate-x-1/2"
                        style="left: {xOf(i)}%; top: {yOf(p.count)}px"
                        title="{p.label} skills: {p.count.toLocaleString()} ads ({pctOf(p.count)}%)"
                    >
                        <span class="absolute top-0 left-1/2 w-[3px] -translate-x-1/2 rounded-t-[2px] bg-(--bar-skills) opacity-35" style="height: {plotH - yOf(p.count)}px"></span>
                        <span class="absolute bottom-3 left-1/2 z-1 -translate-x-1/2 rounded border border-slate-200 bg-white px-1 py-0.5 font-mono text-[11px] leading-none font-semibold whitespace-nowrap text-slate-700">{p.count}</span>
                        <span class="relative block size-[9px] -translate-y-1/2 rounded-full bg-(--bar-skills) ring-2 ring-white"></span>
                    </li>
                {/each}
            </ul>
            {#if medianPos !== null}
                <div class="pointer-events-none absolute inset-y-0 border-l-2 border-dashed border-slate-900" style="left: {medianPos}%" aria-hidden="true">
                    <span class="absolute -top-1 left-1 rounded bg-white px-1 text-[10px] font-semibold whitespace-nowrap text-slate-900">median {median}</span>
                </div>
            {/if}
        </div>
        <div class="mt-1.5 flex border-t-2 border-slate-300">
            {#each points as p (p.label)}
                <span class="relative min-w-0 flex-1 pt-2 text-center font-mono leading-tight before:absolute before:top-0 before:left-1/2 before:h-[5px] before:w-px before:bg-slate-400 before:content-['']"
                    ><span class="block text-xs font-semibold text-slate-900">{p.label}</span><span class="block text-[10px] text-slate-500">{pctOf(p.count)}%</span></span
                >
            {/each}
        </div>
    {/if}
</section>
