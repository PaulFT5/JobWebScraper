<script lang="ts">
    import { displayName, SLOPE_OUTSIDE, type SlopeRow } from '$lib/analyzerMock';

    let {
        startLabel,
        endLabel,
        rows,
        highlighted,
        colorOf
    }: {
        startLabel: string;
        endLabel: string;
        rows: SlopeRow[];
        highlighted: Set<string>;
        colorOf: (concept: string) => string | null;
    } = $props();

    type Filter = 'all' | 'gainers' | 'decliners';
    let filter = $state<Filter>('all');

    const rowH = 26;
    const labelW = 190;
    const slopeW = 160;
    const width = labelW * 2 + slopeW;
    const top = 30;
    const height = top + SLOPE_OUTSIDE * rowH + 8;

    const xL = labelW;
    const xR = labelW + slopeW;
    const y = (rank: number) => top + (rank - 1) * rowH;

    // positive = places gained (rank number went down)
    const delta = (r: SlopeRow) => r.start - r.end;
    const visible = (r: SlopeRow) =>
        filter === 'all' || (filter === 'gainers' ? delta(r) > 0 : delta(r) < 0);

    const movers = $derived(rows.filter((r) => delta(r) !== 0 && visible(r)));
    const statics = $derived(filter === 'all' ? rows.filter((r) => delta(r) === 0) : []);

    // one label per rank on each side; everything outside the top 10 shares the bottom row, so stack those
    function placed(side: 'start' | 'end') {
        const shown = [...movers, ...statics];
        const outside = shown.filter((r) => r[side] === SLOPE_OUTSIDE);
        return shown.map((r) => ({
            row: r,
            y: r[side] === SLOPE_OUTSIDE ? y(SLOPE_OUTSIDE) + outside.indexOf(r) * 13 : y(r[side])
        }));
    }
    const leftLabels = $derived(placed('start'));
    const rightLabels = $derived(placed('end'));

    const stroke = (c: string) => (highlighted.has(c) ? (colorOf(c) ?? '#64748b') : '#94a3b8');
    const rankText = (r: number) => (r === SLOPE_OUTSIDE ? '>10' : `#${r}`);
    const gained = $derived(rows.filter((r) => delta(r) > 0).length);
    const lost = $derived(rows.filter((r) => delta(r) < 0).length);

    const pill = (active: boolean) =>
        `cursor-pointer rounded-full border px-2.5 py-0.5 text-xs focus-visible:outline-2 focus-visible:outline-teal-500
         ${active ? 'border-slate-800 bg-slate-800 text-white' : 'border-slate-300 bg-white text-slate-600 hover:text-slate-900'}`;
</script>

<div class="mb-3 flex flex-wrap gap-1.5" role="group" aria-label="Filter skills by rank change">
    <button type="button" class={pill(filter === 'all')} aria-pressed={filter === 'all'} onclick={() => (filter = 'all')}>All skills</button>
    <button type="button" class={pill(filter === 'gainers')} aria-pressed={filter === 'gainers'} onclick={() => (filter = 'gainers')}>Gainers only ({gained})</button>
    <button type="button" class={pill(filter === 'decliners')} aria-pressed={filter === 'decliners'} onclick={() => (filter = 'decliners')}>Decliners only ({lost})</button>
</div>

<div class="overflow-x-auto">
    <svg viewBox="0 0 {width} {height}" class="mx-auto block w-full max-w-[560px] min-w-[480px]" role="img" aria-label="Rank of each skill at the start and at the end">
        <text x={xL} y="12" text-anchor="middle" class="fill-slate-500 text-[10px] font-semibold">START</text>
        <text x={xL} y="23" text-anchor="middle" class="fill-slate-500 text-[10px]">{startLabel}</text>
        <text x={xR} y="12" text-anchor="middle" class="fill-slate-500 text-[10px] font-semibold">LATEST</text>
        <text x={xR} y="23" text-anchor="middle" class="fill-slate-500 text-[10px]">{endLabel}</text>
        <line x1={xL} x2={xL} y1={top - 4} y2={height - 6} class="stroke-slate-200" />
        <line x1={xR} x2={xR} y1={top - 4} y2={height - 6} class="stroke-slate-200" />

        <!-- unchanged skills: faded endpoint dots only -->
        {#each statics as r (r.concept)}
            <circle cx={xL} cy={y(r.start)} r="3" fill="#cbd5e1" />
            <circle cx={xR} cy={y(r.end)} r="3" fill="#cbd5e1" />
        {/each}

        {#each movers as r (r.concept)}
            {@const on = highlighted.has(r.concept)}
            <line x1={xL} y1={y(r.start)} x2={xR} y2={y(r.end)} stroke={stroke(r.concept)} stroke-width={on ? 2.5 : 1.5} stroke-linecap="round" />
            <circle cx={xL} cy={y(r.start)} r="4" fill={stroke(r.concept)} stroke="#fff" stroke-width="1.5" />
            <circle cx={xR} cy={y(r.end)} r="4" fill={stroke(r.concept)} stroke="#fff" stroke-width="1.5" />
        {/each}

        {#each leftLabels as l (l.row.concept)}
            {@const still = delta(l.row) === 0}
            <text x={xL - 10} y={l.y} dy="0.32em" text-anchor="end" class="text-[11px] {still ? 'fill-slate-400' : highlighted.has(l.row.concept) ? 'fill-slate-900' : 'fill-slate-600'}">
                {displayName(l.row.concept)} <tspan class="fill-slate-400 font-mono">{rankText(l.row.start)}</tspan>
            </text>
        {/each}

        {#each rightLabels as l (l.row.concept)}
            {@const d = delta(l.row)}
            <text x={xR + 10} y={l.y} dy="0.32em" class="text-[11px] {d === 0 ? 'fill-slate-400' : highlighted.has(l.row.concept) ? 'fill-slate-900 font-semibold' : 'fill-slate-600'}">
                <tspan class="font-mono {d === 0 ? 'fill-slate-400' : 'fill-slate-500'}">{rankText(l.row.end)}</tspan> {displayName(l.row.concept)}
                {#if d !== 0}<tspan class={d > 0 ? 'fill-emerald-700' : 'fill-red-700'}> {d > 0 ? '▲' : '▼'}{Math.abs(d)}</tspan>{/if}
            </text>
        {/each}
    </svg>
</div>
