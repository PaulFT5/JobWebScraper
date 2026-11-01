<script lang="ts">
    import { displayName, type TopSkill } from '$lib/analyzerMock';

    let { skills, postings }: { skills: TopSkill[]; postings: number } = $props();

    // round the scale up so the longest bar leaves room for its label
    const max = $derived(Math.max(10, Math.ceil(Math.max(...skills.map((s) => s.share)) / 10) * 10));
    const ticks = $derived(Array.from({ length: max / 10 + 1 }, (_, i) => i * 10).filter((t, _, all) => all.length <= 6 || t % 20 === 0));
</script>

<div class="grid grid-cols-[minmax(8rem,14rem)_1fr] gap-x-3">
    <!-- axis -->
    <div></div>
    <div class="relative mb-1 h-4 text-[10px] text-slate-500" aria-hidden="true">
        {#each ticks as t (t)}
            <span class="absolute -translate-x-1/2" style="left: {(t / max) * 100}%">{t}%</span>
        {/each}
    </div>

    <ol class="contents" aria-label="Top {skills.length} skills by share of postings">
        {#each skills as s, i (s.concept)}
            <li class="contents">
                <div class="flex min-w-0 items-center justify-end gap-1.5 py-1 text-right text-xs">
                    <span class="truncate text-slate-800" title={s.concept}>{displayName(s.concept)}</span>
                    {#if !s.inEsco}
                        <span class="shrink-0 rounded border border-slate-300 px-1 text-[9px] font-medium tracking-wide text-slate-500 uppercase" title="Not mapped to an ESCO concept; counted by its cleaned name">not in ESCO</span>
                    {/if}
                </div>
                <div
                    class="relative flex items-center py-1"
                    title="#{i + 1} {s.concept}: {s.share.toFixed(1)}% of {postings.toLocaleString()} postings ({s.jobs} jobs){s.inEsco ? '' : ' · not in ESCO'}"
                >
                    {#each ticks as t (t)}
                        <span class="absolute inset-y-0 border-l border-slate-100" style="left: {(t / max) * 100}%" aria-hidden="true"></span>
                    {/each}
                    <span
                        class="relative h-4 rounded-r-[4px] {s.inEsco ? 'bg-teal-600' : 'border border-teal-600 bg-teal-100'}"
                        style="width: {(s.share / max) * 100}%; {s.inEsco ? '' : 'background-image: repeating-linear-gradient(45deg, transparent 0 4px, rgb(13 148 136 / 0.35) 4px 6px)'}"
                    ></span>
                    <span class="relative ml-2 font-mono text-[11px] whitespace-nowrap text-slate-700">
                        {s.share.toFixed(1)}% <span class="text-slate-400">·</span> {s.jobs.toLocaleString()} jobs
                    </span>
                </div>
            </li>
        {/each}
    </ol>
</div>
