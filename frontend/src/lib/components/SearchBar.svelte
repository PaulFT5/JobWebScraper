<script lang="ts">
    import { SlidersHorizontal, Search } from '@lucide/svelte';

    export type SortKey = 'default' | 'salary-desc' | 'salary-asc' | 'title';
    export type SearchFields = { title: boolean; company: boolean; skills: boolean };

    let {
        search = $bindable(''),
        sort = $bindable<SortKey>('default'),
        fields = $bindable<SearchFields>({ title: true, company: true, skills: false }),
        onchange
    }: { search?: string; sort?: SortKey; fields?: SearchFields; onchange?: () => void } = $props();

    const SORTS: { value: SortKey; label: string }[] = [
        { value: 'default', label: 'Default order' },
        { value: 'salary-desc', label: 'Salary: high → low' },
        { value: 'salary-asc', label: 'Salary: low → high' },
        { value: 'title', label: 'Title A–Z' }
    ];
    const FIELDS: { key: keyof SearchFields; label: string }[] = [
        { key: 'title', label: 'Title' },
        { key: 'company', label: 'Company' },
        { key: 'skills', label: 'Skills' }
    ];

    let open = $state(false);
    let root = $state<HTMLDivElement>();

    const searchedIn = $derived(FIELDS.filter((f) => fields[f.key]).map((f) => f.label.toLowerCase()));
    const changedFromDefault = $derived(sort !== 'default' || !fields.title || !fields.company || fields.skills);

    // at least one field stays on (the last one is disabled), otherwise the search would match nothing
    const onlyOne = $derived([fields.title, fields.company, fields.skills].filter(Boolean).length === 1);

    function toggleField(key: keyof SearchFields) {
        fields = { ...fields, [key]: !fields[key] };
        onchange?.();
    }

    // close the panel on a click outside or on Escape
    function onWindowClick(e: MouseEvent) {
        if (open && root && !root.contains(e.target as Node)) open = false;
    }
    function onKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') open = false;
    }
</script>

<svelte:window onclick={onWindowClick} onkeydown={onKeydown} />

<div class="relative w-full" bind:this={root}>
    <div class="flex h-9 items-stretch overflow-hidden rounded-full border border-[#757575] bg-white">
        <label class="flex min-w-0 flex-1 items-center gap-2 pr-3 pl-3.5 focus-within:bg-slate-50/60">
            <Search size={16} strokeWidth={1.5} class="shrink-0 text-[#757575]" aria-hidden="true" />
            <input
                type="search"
                placeholder="Search..."
                aria-label="Search jobs by {searchedIn.join(', ')}"
                class="min-w-0 flex-1 border-0 bg-transparent p-0 text-sm text-slate-900 placeholder:text-slate-400 focus:ring-0"
                bind:value={search}
                oninput={() => onchange?.()}
            />
        </label>
        <button
            type="button"
            class="relative flex w-12 shrink-0 cursor-pointer items-center justify-center border-l border-[#9e9e9e] text-[#757575] hover:bg-slate-50 hover:text-slate-900
                   focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-teal-500"
            aria-label="Sort and search options"
            aria-expanded={open}
            aria-haspopup="dialog"
            onclick={() => (open = !open)}
        >
            <SlidersHorizontal size={16} strokeWidth={1.75} />
            {#if changedFromDefault}
                <span class="absolute top-1.5 right-2.5 size-1.5 rounded-full bg-teal-600" aria-hidden="true"></span>
            {/if}
        </button>
    </div>

    {#if open}
        <div
            class="absolute top-full right-0 z-30 mt-2 w-64 rounded-xl border border-slate-200 bg-white p-3 text-sm shadow-lg"
            role="dialog"
            aria-label="Sort and search options"
        >
            <fieldset>
                <legend class="mb-1.5 text-[11px] font-semibold tracking-wide text-slate-500 uppercase">Sort by</legend>
                {#each SORTS as s (s.value)}
                    <label class="flex cursor-pointer items-center gap-2 rounded px-1 py-1 hover:bg-slate-50">
                        <input
                            type="radio"
                            name="job-sort"
                            value={s.value}
                            checked={sort === s.value}
                            class="text-teal-600 focus:ring-teal-500"
                            onchange={() => {
                                sort = s.value;
                                onchange?.();
                            }}
                        />
                        {s.label}
                    </label>
                {/each}
            </fieldset>
            <fieldset class="mt-3 border-t border-slate-100 pt-3">
                <legend class="mb-1.5 text-[11px] font-semibold tracking-wide text-slate-500 uppercase">Search in</legend>
                {#each FIELDS as f (f.key)}
                    <label class="flex cursor-pointer items-center gap-2 rounded px-1 py-1 hover:bg-slate-50">
                        <input
                            type="checkbox"
                            checked={fields[f.key]}
                            disabled={onlyOne && fields[f.key]}
                            class="rounded text-teal-600 focus:ring-teal-500 disabled:opacity-50"
                            onchange={() => toggleField(f.key)}
                        />
                        {f.label}
                    </label>
                {/each}
            </fieldset>
        </div>
    {/if}
</div>
