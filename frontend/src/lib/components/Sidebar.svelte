<script lang="ts">
    import { page } from '$app/state';
    import { cv } from '$lib/cv.svelte';
    import { selected, applyFilters, resetFilters, isDirty, appliedCount, salaryOptions, experienceOptions, type Option } from '$lib/filters.svelte';
    import FilterGroup from './FilterGroup.svelte';

    let { filters }: {
        filters: { cities: Option[]; work_types: Option[]; domains: Option[] };
    } = $props();

    let fileInput = $state<HTMLInputElement>();
    let cvError = $state<string | null>(null);

    const dirty = $derived(isDirty());
    const activeCount = $derived(appliedCount());
    const hasSelection = $derived(dirty || activeCount > 0);

    function onFileChange(e: Event) {
        const input = e.currentTarget as HTMLInputElement;
        const file = input.files?.[0];
        if (!file) return;
        if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
            cvError = 'Only PDF files are supported.';
            input.value = '';
            return;
        }
        cvError = null;
        cv.fileName = file.name;
    }

    function removeCv() {
        cv.fileName = null;
        cvError = null;
        if (fileInput) fileInput.value = '';
    }

    const navClass = (active: boolean, activeStyle: string) =>
        `flex flex-1 items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold
         focus-visible:outline-2 focus-visible:outline-teal-400
         ${active ? activeStyle : 'border-transparent text-slate-500 hover:text-slate-300'}`;
</script>

<aside class="flex h-screen w-64 shrink-0 flex-col bg-[#1e2433] text-slate-200">
    <header class="border-b border-slate-700 p-4">
        <h1 class="text-xl font-bold">CV<span class="text-teal-400">Match</span></h1>
        <p class="text-xs text-slate-400">Job compatibility engine</p>
    </header>

    <section class="border-b border-slate-700 p-4">
        <h2 class="mb-2 text-xs font-semibold tracking-wider text-slate-400">YOUR CV</h2>
        <!-- clicking the box picks a (new) file; the X sits on top of it and only removes -->
        <div class="relative">
            <label
                class="flex cursor-pointer items-center justify-center rounded-lg border border-dashed border-slate-600 bg-slate-800 p-2 hover:bg-slate-700
                       has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-teal-400
                       {cv.fileName ? 'pr-8' : ''}"
                title={cv.fileName ? 'Click to replace' : undefined}
            >
                <span class="truncate">{cv.fileName ?? 'Upload CV (PDF)'}</span>
                <input bind:this={fileInput} type="file" accept=".pdf,application/pdf" class="sr-only" onchange={onFileChange} />
            </label>
            {#if cv.fileName}
                <button
                    type="button"
                    aria-label="Remove CV"
                    class="absolute inset-y-0 right-1.5 my-auto flex size-6 cursor-pointer items-center justify-center rounded text-slate-400
                           hover:bg-slate-600 hover:text-white focus-visible:outline-2 focus-visible:outline-teal-400"
                    onclick={removeCv}
                >
                    <svg class="size-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M18 6 6 18" /><path d="m6 6 12 12" />
                    </svg>
                </button>
            {/if}
        </div>
        {#if cvError}
            <p class="mt-1.5 text-xs text-red-300" role="alert">{cvError}</p>
        {/if}
    </section>

    <div class="border-b border-slate-700 p-4">
        <div class="flex gap-2">
            <button
                type="button"
                class="flex-1 cursor-pointer rounded-lg bg-teal-500 px-3 py-1.5 text-sm font-semibold text-slate-900 hover:bg-teal-400
                       focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-400
                       disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-teal-500"
                disabled={!dirty}
                onclick={applyFilters}
            >
                Apply
            </button>
            <button
                type="button"
                class="flex-1 cursor-pointer rounded-lg border border-slate-600 px-3 py-1.5 text-sm hover:bg-slate-700
                       focus-visible:outline-2 focus-visible:outline-teal-400
                       disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
                disabled={!hasSelection}
                onclick={resetFilters}
            >
                Reset
            </button>
        </div>
    </div>

    <div class="scrollbar-none flex-1 overflow-y-auto">
        <FilterGroup title="Job domain" options={filters.domains} bind:selected={selected.domains} searchable={false} />
        <FilterGroup title="Location" options={filters.cities} bind:selected={selected.cities} />
        <FilterGroup title="Work type" options={filters.work_types} bind:selected={selected.work_types} />
        <FilterGroup title="Experience" options={experienceOptions} bind:selected={selected.experience_levels} />
        <FilterGroup title="Salary info" options={salaryOptions} bind:selected={selected.salary_kinds} />
    </div>

    <nav class="flex gap-1 border-t border-slate-700 p-2">
        <a href="/" class={navClass(page.url.pathname === '/', 'border-transparent bg-slate-800 text-white')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect width="7" height="7" x="3" y="3" rx="1" />
                <rect width="7" height="7" x="14" y="3" rx="1" />
                <rect width="7" height="7" x="14" y="14" rx="1" />
                <rect width="7" height="7" x="3" y="14" rx="1" />
            </svg>
            Jobs
        </a>
        <a href="/analyzer" class={navClass(page.url.pathname === '/analyzer', 'border-teal-500/40 bg-teal-500/15 text-teal-300')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <line x1="18" x2="18" y1="20" y2="10" />
                <line x1="12" x2="12" y1="20" y2="4" />
                <line x1="6" x2="6" y1="20" y2="14" />
            </svg>
            Analyzer
        </a>
    </nav>
</aside>
