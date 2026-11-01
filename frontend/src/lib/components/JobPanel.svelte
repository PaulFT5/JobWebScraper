<script lang="ts">
    import { applied } from '$lib/filters.svelte';
    import { fetchJobs } from '$lib/api/fetchJobs';
    import { selection, selectJob, showDetails } from '$lib/selection.svelte';
    import { cv } from '$lib/cv.svelte';
    import { mockScore } from '$lib/mockScore.svelte';
    import { jobKey, salaryFloor, salaryKind, experienceKind, parseSkills } from '$lib/jobs';
    import type { Job } from '$lib/types';
    import JobCard from './JobCard.svelte';
    import SearchBar, { type SortKey, type SearchFields } from './SearchBar.svelte';

    const PAGE_SIZE = 30;

    let jobs = $state<Job[]>([]);
    let status = $state<'loading' | 'ready' | 'error'>('loading');
    let loadedOnce = $state(false);
    let reloadKey = $state(0);
    let search = $state('');
    let sort = $state<SortKey>('default');
    let fields = $state<SearchFields>({ title: true, company: true, skills: false });
    let visible = $state(PAGE_SIZE);

    // only the newest request may write results
    let latestRequest = 0;

    $effect(() => {
        void reloadKey; // Retry bumps this to re-run the fetch
        const request = ++latestRequest;
        status = 'loading';
        fetchJobs(applied)
            .then((result) => {
                if (request !== latestRequest) return;
                jobs = result;
                status = 'ready';
                loadedOnce = true;
                visible = PAGE_SIZE;
            })
            .catch(() => {
                if (request !== latestRequest) return;
                status = 'error';
            });
    });

    // search only in the fields ticked under "Search in"
    function matches(j: Job, term: string): boolean {
        return (
            (fields.title && j.title.toLowerCase().includes(term)) ||
            (fields.company && (j.company ?? '').toLowerCase().includes(term)) ||
            (fields.skills && parseSkills(j.required_skills).some((s) => s.toLowerCase().includes(term)))
        );
    }

    const shown = $derived.by(() => {
        const term = search.trim().toLowerCase();
        const kinds = applied.salary_kinds;
        const levels = applied.experience_levels;
        const list = jobs.filter(
            (j) =>
                (kinds.length === 0 || kinds.includes(salaryKind(j))) &&
                (levels.length === 0 || levels.includes(experienceKind(j))) &&
                (!term || matches(j, term))
        );

        if (sort === 'title') list.sort((a, b) => a.title.localeCompare(b.title));
        if (sort === 'salary-desc' || sort === 'salary-asc') {
            const dir = sort === 'salary-desc' ? -1 : 1;
            // jobs without a salary always go last
            list.sort((a, b) => {
                const sa = salaryFloor(a);
                const sb = salaryFloor(b);
                if (sa === null) return sb === null ? 0 : 1;
                if (sb === null) return -1;
                return (sa - sb) * dir;
            });
        }
        return list;
    });

    // salary and experience filters work on the loaded list, so start paging over when they change
    $effect(() => {
        void applied.salary_kinds;
        void applied.experience_levels;
        visible = PAGE_SIZE;
    });

    const page = $derived(shown.slice(0, visible));
    // the compared job is only highlighted once there is a CV to compare with
    const selectedKey = $derived(cv.fileName && selection.job ? jobKey(selection.job) : null);

    let listEl = $state<HTMLDivElement>();

    // bring the compared card into view once the details popup closes
    $effect(() => {
        if (selection.details || !selectedKey || !listEl) return;
        listEl
            .querySelector(`[data-job-key="${CSS.escape(selectedKey)}"]`)
            ?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });

    function resetPaging() {
        visible = PAGE_SIZE;
    }
</script>

<section class="flex min-h-0 flex-1 flex-col">
    <!-- same columns as the job grid below, so the search bar is exactly one job card wide (the middle one on wide screens) -->
    <header class="grid shrink-0 grid-cols-1 items-end gap-3 pb-3 md:grid-cols-2 xl:grid-cols-3">
        <div>
            <h2 class="text-base font-semibold">Available Positions</h2>
            <p class="text-xs text-slate-500" aria-live="polite">
                {#if status === 'error'}
                    Could not load jobs
                {:else if status === 'loading' && !loadedOnce}
                    Loading…
                {:else}
                    {shown.length} {shown.length === 1 ? 'result' : 'results'}{status === 'loading' ? ' · updating…' : ''}
                {/if}
            </p>
        </div>

        <SearchBar bind:search bind:sort bind:fields onchange={resetPaging} />

        <div class="hidden xl:block" aria-hidden="true"></div>
    </header>

    <!-- inner padding keeps the selected ring and focus outline from being clipped by the scroll box -->
    <div bind:this={listEl} class="-mx-1 min-h-0 flex-1 overflow-y-auto px-1 pt-1 pb-6">
        {#if status === 'error'}
            <div class="flex items-center gap-3 text-sm text-slate-600">
                <span>The job list could not be loaded. Is the API running?</span>
                <button
                    type="button"
                    class="cursor-pointer rounded border border-slate-300 bg-white px-2 py-1 text-xs hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-teal-500"
                    onclick={() => reloadKey++}
                >
                    Retry
                </button>
            </div>
        {:else if loadedOnce && shown.length === 0}
            <p class="text-sm text-slate-500">No jobs match these filters.</p>
        {:else if loadedOnce}
            <div class="grid grid-cols-1 items-start gap-3 transition-opacity md:grid-cols-2 xl:grid-cols-3 {status === 'loading' ? 'opacity-60' : ''}">
                {#each page as job (jobKey(job))}
                    <JobCard {job} score={mockScore.value ?? undefined} selected={jobKey(job) === selectedKey} onSelect={selectJob} onDetails={showDetails} />
                {/each}
            </div>

            {#if page.length < shown.length}
                <div class="mt-4 flex justify-center">
                    <button
                        type="button"
                        class="cursor-pointer rounded-lg border border-slate-300 bg-white px-4 py-1.5 text-sm hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-teal-500"
                        onclick={() => (visible += PAGE_SIZE)}
                    >
                        Load more ({shown.length - page.length} left)
                    </button>
                </div>
            {/if}
        {/if}
    </div>
</section>
