<script lang="ts">
    import { coOccurrence, displayName } from '$lib/analyzerMock';

    let { concepts }: { concepts: string[] } = $props();

    let choice = $state('');
    // fall back to the first skill when the list changes (e.g. another domain) and the choice is gone
    const selected = $derived(concepts.includes(choice) ? choice : (concepts[0] ?? ''));
    const rows = $derived(selected ? coOccurrence(selected) : []);
</script>

<label class="mb-3 flex items-center gap-2 text-xs text-slate-600">
    Jobs asking for
    <select class="rounded-md border-slate-300 py-1 pr-8 text-sm focus:border-teal-500 focus:ring-teal-500" value={selected} onchange={(e) => (choice = e.currentTarget.value)}>
        {#each concepts as c (c)}<option value={c}>{displayName(c)}</option>{/each}
    </select>
    also ask for:
</label>

<ul class="space-y-1.5">
    {#each rows as r (r.concept)}
        <li class="grid grid-cols-[9rem_1fr_2.5rem] items-center gap-2 text-xs" title="{r.pct}% of jobs with {displayName(selected)} also ask for {displayName(r.concept)}">
            <span class="truncate text-slate-700">{displayName(r.concept)}</span>
            <span class="h-2.5 rounded-r bg-slate-100"><span class="block h-2.5 rounded-r bg-teal-600" style="width: {r.pct}%"></span></span>
            <span class="text-right font-mono text-slate-900">{r.pct}%</span>
        </li>
    {/each}
</ul>
