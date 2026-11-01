<script lang="ts">
    import { displayName, type SpecificityPoint } from '$lib/analyzerMock';

    let {
        points,
        highlighted,
        colorOf
    }: { points: SpecificityPoint[]; highlighted: Set<string>; colorOf: (concept: string) => string | null } = $props();

    const W = 520;
    const H = 320;
    const pad = { top: 16, right: 16, bottom: 36, left: 44 };
    const innerW = W - pad.left - pad.right;
    const innerH = H - pad.top - pad.bottom;

    let hover = $state<SpecificityPoint | null>(null);

    const xMax = $derived(Math.ceil(Math.max(5, ...points.map((p) => p.share)) / 5) * 5);
    const x = (v: number) => pad.left + (v / xMax) * innerW;
    const y = (v: number) => pad.top + innerH - (v / 100) * innerH;

    // quadrant split at the medians, so the quadrants are relative to this skill set
    const median = (v: number[]) => {
        const s = [...v].sort((a, b) => a - b);
        return s.length ? (s[Math.floor((s.length - 1) / 2)] + s[Math.ceil((s.length - 1) / 2)]) / 2 : 0;
    };
    const midX = $derived(median(points.map((p) => p.share)));
    const midY = $derived(median(points.map((p) => p.concentration)));

    const fill = (c: string) => (highlighted.has(c) ? (colorOf(c) ?? '#0d9488') : '#94a3b8');
    const xTicks = $derived(Array.from({ length: xMax / 5 + 1 }, (_, i) => i * 5));
</script>

<div class="relative">
    <svg viewBox="0 0 {W} {H}" class="block w-full" role="img" aria-label="Skills by share of postings and by concentration in one domain">
        <!-- quadrant guides -->
        <line x1={x(midX)} x2={x(midX)} y1={pad.top} y2={pad.top + innerH} class="stroke-slate-300" stroke-dasharray="4 4" />
        <line x1={pad.left} x2={pad.left + innerW} y1={y(midY)} y2={y(midY)} class="stroke-slate-300" stroke-dasharray="4 4" />
        <text x={pad.left + innerW - 4} y={pad.top + 10} text-anchor="end" class="fill-slate-500 text-[10px] font-semibold">CORE ESSENTIALS</text>
        <text x={pad.left + 4} y={pad.top + 10} class="fill-slate-500 text-[10px] font-semibold">NICHE SPECIALISTS</text>
        <text x={pad.left + innerW - 4} y={pad.top + innerH - 6} text-anchor="end" class="fill-slate-500 text-[10px] font-semibold">GENERIC BASELINE</text>
        <text x={pad.left + 4} y={pad.top + innerH - 6} class="fill-slate-500 text-[10px] font-semibold">FRINGE</text>

        {#each [0, 25, 50, 75, 100] as t (t)}
            <text x={pad.left - 6} y={y(t)} dy="0.32em" text-anchor="end" class="fill-slate-500 text-[10px]">{t}%</text>
        {/each}
        {#each xTicks as t (t)}
            <text x={x(t)} y={pad.top + innerH + 14} text-anchor="middle" class="fill-slate-500 text-[10px]">{t}%</text>
        {/each}
        <line x1={pad.left} x2={pad.left + innerW} y1={pad.top + innerH} y2={pad.top + innerH} class="stroke-slate-300" />
        <text x={pad.left + innerW / 2} y={H - 4} text-anchor="middle" class="fill-slate-600 text-[10px]">Share of all postings →</text>
        <text transform="translate(10 {pad.top + innerH / 2}) rotate(-90)" text-anchor="middle" class="fill-slate-600 text-[10px]">Concentration in one domain →</text>

        {#each points as p (p.concept)}
            {@const on = highlighted.has(p.concept)}
            <!-- larger invisible target so small dots are easy to hover -->
            <circle
                cx={x(p.share)}
                cy={y(p.concentration)}
                r="10"
                fill="transparent"
                role="presentation"
                onpointerenter={() => (hover = p)}
                onpointerleave={() => (hover = null)}
            />
            <circle cx={x(p.share)} cy={y(p.concentration)} r={on ? 6 : 4.5} fill={fill(p.concept)} stroke="#fff" stroke-width="2" pointer-events="none" />
            {#if on}
                <text x={x(p.share) + 9} y={y(p.concentration)} dy="0.32em" class="fill-slate-800 text-[10px]" pointer-events="none">{displayName(p.concept)}</text>
            {/if}
        {/each}
    </svg>

    {#if hover}
        <div
            class="pointer-events-none absolute w-52 rounded-lg border border-slate-200 bg-white p-2 text-xs shadow-md"
            style="left: min(calc({(x(hover.share) / W) * 100}% + 12px), calc(100% - 13rem)); top: {(y(hover.concentration) / H) * 100}%"
        >
            <div class="font-semibold text-slate-900">{displayName(hover.concept)}</div>
            <div class="text-slate-600">{hover.share.toFixed(1)}% of postings</div>
            <div class="text-slate-600">{hover.concentration.toFixed(0)}% of them in {hover.topDomain}</div>
        </div>
    {/if}
</div>
