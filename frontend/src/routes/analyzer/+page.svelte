<script lang="ts">
    import { selection } from '$lib/selection.svelte';
    import ExtractionView from '$lib/components/analyzer/ExtractionView.svelte';
    import MatchingView from '$lib/components/analyzer/MatchingView.svelte';
    import JobsView from '$lib/components/analyzer/JobsView.svelte';
    import { fetchJobs } from '$lib/api/fetchJobs';
    import { fetchCoverage, type CoverageResult } from '$lib/api/fetchCoverage';
    import type { Job } from '$lib/types';

    let { data } = $props();

    type Tab = 'extraction' | 'matching' | 'jobs';

    const TABS: { id: Tab; label: string; hint: string }[] = [
        { id: 'jobs', label: 'Jobs', hint: 'Market overview by skill and domain' },
        { id: 'matching', label: 'Matching', hint: 'Your CV against the selected job' },
        { id: 'extraction', label: 'Extraction', hint: 'How skills are extracted and grounded' }
    ];

    // open on Matching when a job was picked on the Jobs page
    let tab = $state<Tab>(selection.job ? 'matching' : 'jobs');

    const domains = $derived(data.domains.map((d: { name: string }) => d.name));
    const cities = $derived(data.cities.map((c: { name: string }) => c.name));

    // real data for the verified views: every available ad with extracted skills, plus the coverage counts
    let jobs = $state<Job[]>([]);
    let jobsStatus = $state<'loading' | 'ready' | 'error'>('loading');
    let coverage = $state<CoverageResult | null>(null);

    $effect(() => {
        fetchJobs({ domains: [], work_types: [], cities: [] })
            .then((list) => {
                jobs = list;
                jobsStatus = 'ready';
            })
            .catch(() => (jobsStatus = 'error'));
        fetchCoverage().then((result) => (coverage = result));
    });
</script>

<div class="flex h-screen flex-col bg-slate-50">
    <header class="shrink-0 border-b border-slate-200 bg-white px-6 pt-4">
        <div class="flex flex-wrap items-baseline gap-3">
            <h1 class="text-lg font-semibold text-slate-900">Analyzer</h1>
            <span class="text-[11px] text-slate-500">Verified counts on top · grayed sections are previews with mock data</span>
            <span class="text-xs text-slate-500">{TABS.find((t) => t.id === tab)?.hint}</span>
        </div>
        <div role="tablist" aria-label="Analyzer sections" class="mt-3 flex gap-1">
            {#each TABS as t (t.id)}
                <button
                    type="button"
                    role="tab"
                    aria-selected={tab === t.id}
                    class="cursor-pointer border-b-2 px-3 py-2 text-sm font-semibold focus-visible:outline-2 focus-visible:outline-teal-500
                           {tab === t.id ? 'border-teal-600 text-teal-700' : 'border-transparent text-slate-500 hover:text-slate-800'}"
                    onclick={() => (tab = t.id)}
                >
                    {t.label}
                    {#if t.id === 'matching' && selection.job}<span class="ml-1 inline-block size-1.5 rounded-full bg-teal-500 align-middle"></span>{/if}
                </button>
            {/each}
        </div>
    </header>

    <div class="min-h-0 flex-1 overflow-y-auto px-6 py-5" role="tabpanel">
        {#if tab === 'extraction'}
            <ExtractionView {jobs} {coverage} />
        {:else if tab === 'matching'}
            <MatchingView />
        {:else}
            <JobsView {domains} {cities} {jobs} {jobsStatus} {coverage} />
        {/if}
    </div>
</div>
