<script lang="ts">
    import { displayName } from '$lib/analyzerMock';

    type Group = { name: string; skills: { concept: string; share: number }[] };

    let { groups }: { groups: Group[] } = $props();

    let hover = $state<string | null>(null);

    // slice-and-dice: category width ∝ its total share, skill height ∝ its share inside the category
    const total = $derived(groups.reduce((sum, g) => sum + g.skills.reduce((a, s) => a + s.share, 0), 0));
    const sized = $derived(
        groups
            .map((g) => ({ ...g, sum: g.skills.reduce((a, s) => a + s.share, 0) }))
            .filter((g) => g.sum > 0)
            .sort((a, b) => b.sum - a.sum)
    );
</script>

<div class="flex h-72 gap-1" role="list" aria-label="Skills grouped by category, area = share of postings">
    {#each sized as g (g.name)}
        <div class="flex min-w-0 flex-col gap-1" style="flex: {g.sum} 1 0" role="listitem">
            <div class="truncate text-[10px] font-semibold tracking-wide text-slate-500 uppercase" title="{g.name}: {g.sum.toFixed(1)}% of postings">
                {g.name} <span class="font-mono font-normal">{((g.sum / total) * 100).toFixed(0)}%</span>
            </div>
            {#each [...g.skills].sort((a, b) => b.share - a.share) as s (s.concept)}
                <div
                    class="flex min-h-0 items-start overflow-hidden rounded-[4px] p-1.5 text-[11px] leading-tight text-white transition-colors
                           {hover === s.concept ? 'bg-teal-800' : 'bg-teal-600'}"
                    style="flex: {s.share} 1 0"
                    title="{displayName(s.concept)}: {s.share.toFixed(1)}% of postings"
                    role="presentation"
                    onpointerenter={() => (hover = s.concept)}
                    onpointerleave={() => (hover = null)}
                >
                    <span class="truncate">{displayName(s.concept)}</span>
                </div>
            {/each}
        </div>
    {/each}
</div>
