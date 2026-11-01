<script lang="ts">
    import type { CoverageResult, ProblemAd } from '$lib/api/fetchCoverage';

    let { coverage }: { coverage: CoverageResult | null } = $props();

    type ListKey = 'empty' | 'failed' | 'no_description_processed';
    let open = $state<ListKey | null>(null);

    const data = $derived(coverage?.status === 'ready' ? coverage.data : null);
    const pct = (n: number, of: number) => (of ? ((n / of) * 100).toFixed(1) : '0.0') + '%';

    // segment order = pipeline order; status colors only where they mean a state (done / problem)
    const segments = $derived(
        data
            ? [
                  { key: 'extracted', label: 'Extracted', n: data.extracted, style: 'background: #059669', list: null },
                  { key: 'waiting', label: 'Waiting (has description)', n: data.waiting, style: 'background: repeating-linear-gradient(45deg, #94a3b8 0 4px, #cbd5e1 4px 8px)', list: null },
                  { key: 'none', label: 'No description (can’t be extracted)', n: data.no_description, style: 'background: #e2e8f0', list: null },
                  { key: 'empty', label: 'Empty list', n: data.empty, style: 'background: #f59e0b', list: 'empty' as ListKey },
                  { key: 'failed', label: 'Failed', n: data.failed, style: 'background: #dc2626', list: 'failed' as ListKey }
              ]
            : []
    );

    const LIST_TITLES: Record<ListKey, string> = {
        empty: 'Ads with an empty skill list',
        failed: 'Ads where extraction failed',
        no_description_processed: 'Ads processed although their description is empty'
    };
    const openList = $derived<ProblemAd[]>(open && data ? data.problem_ads[open] : []);

    function toggle(key: ListKey) {
        open = open === key ? null : key;
    }
</script>

<section class="rounded-xl border border-slate-200 bg-white p-4">
    <h3 class="text-sm font-semibold text-slate-900">Extraction coverage</h3>
    <p class="mb-3 text-xs text-slate-500">Available ads by extraction state · live from the database</p>

    {#if coverage === null}
        <p class="text-xs text-slate-500">Loading…</p>
    {:else if coverage.status === 'missing'}
        <div class="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-xs text-slate-600">
            <p class="font-semibold text-slate-800">Waiting for the backend endpoint</p>
            <p class="mt-1">
                This card needs <code class="rounded bg-white px-1 font-mono">GET /api/analyzer/coverage</code>, which doesn't exist yet.
                Its spec is in <code class="font-mono">docs/MATCHING_ROADMAP.md</code> → Analyzer page. No numbers are shown until it does.
            </p>
        </div>
    {:else if coverage.status === 'error'}
        <p class="text-xs text-red-700">Could not load coverage. Is the API running?</p>
    {:else if data}
        <div class="mb-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
            <div class="rounded-lg bg-slate-50 p-3">
                <div class="font-mono text-xl font-semibold text-slate-900">{data.available.toLocaleString()}</div>
                <div class="text-[11px] text-slate-500">available ads</div>
            </div>
            <div class="rounded-lg bg-slate-50 p-3">
                <div class="font-mono text-xl font-semibold text-slate-900">{data.with_description.toLocaleString()}</div>
                <div class="text-[11px] text-slate-500">with description · {pct(data.with_description, data.available)} of available</div>
            </div>
            <div class="rounded-lg bg-slate-50 p-3">
                <div class="font-mono text-xl font-semibold text-slate-900">{data.extracted.toLocaleString()}</div>
                <div class="text-[11px] text-slate-500">extracted · {pct(data.extracted, data.with_description)} of ads with a description</div>
            </div>
        </div>

        <div class="flex h-6 gap-0.5 overflow-hidden rounded" role="img" aria-label="Available ads by extraction state">
            {#each segments as s (s.key)}
                {#if s.n > 0}
                    <span
                        class="h-full min-w-1 first:rounded-l last:rounded-r"
                        style="width: {(s.n / data.available) * 100}%; {s.style}"
                        title="{s.label}: {s.n.toLocaleString()} ({pct(s.n, data.available)})"
                    ></span>
                {/if}
            {/each}
        </div>

        <ul class="mt-3 grid grid-cols-1 gap-x-4 gap-y-1.5 text-xs sm:grid-cols-2 lg:grid-cols-3">
            {#each segments as s (s.key)}
                <li class="flex items-center gap-2">
                    <span class="size-2.5 shrink-0 rounded-sm" style={s.style}></span>
                    {#if s.list}
                        <button
                            type="button"
                            class="cursor-pointer text-left text-slate-700 underline decoration-dotted underline-offset-2 hover:text-slate-900 focus-visible:outline-2 focus-visible:outline-teal-500"
                            aria-expanded={open === s.list}
                            onclick={() => toggle(s.list!)}
                        >{s.label}</button>
                    {:else}
                        <span class="text-slate-700">{s.label}</span>
                    {/if}
                    <span class="ml-auto font-mono text-slate-900">{s.n.toLocaleString()}</span>
                    <span class="w-12 text-right font-mono text-slate-500">{pct(s.n, data.available)}</span>
                </li>
            {/each}
        </ul>

        {#if data.no_description_processed > 0}
            <div class="mt-3 flex flex-wrap items-center gap-2 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-900" role="status">
                <span aria-hidden="true">⚠</span>
                <span>
                    <strong>{data.no_description_processed}</strong> ads were processed although their description is empty; their skills may be
                    invented by the LLM (ASSIST_LOG T7).
                </span>
                <button
                    type="button"
                    class="ml-auto cursor-pointer font-semibold underline underline-offset-2 focus-visible:outline-2 focus-visible:outline-amber-600"
                    aria-expanded={open === 'no_description_processed'}
                    onclick={() => toggle('no_description_processed')}
                >Inspect ads</button>
            </div>
        {/if}

        {#if open}
            <div class="mt-3 rounded-lg border border-slate-200">
                <div class="flex items-center justify-between border-b border-slate-200 px-3 py-2">
                    <h4 class="text-xs font-semibold text-slate-800">{LIST_TITLES[open]} ({openList.length})</h4>
                    <button type="button" class="cursor-pointer text-xs text-slate-500 hover:text-slate-900 focus-visible:outline-2 focus-visible:outline-teal-500" onclick={() => (open = null)}>Close</button>
                </div>
                <ul class="max-h-64 divide-y divide-slate-100 overflow-y-auto text-xs">
                    {#each openList as ad (ad.slug)}
                        <li class="flex items-center gap-2 px-3 py-1.5">
                            <span class="min-w-0 flex-1 truncate text-slate-800" title={ad.title}>{ad.title}</span>
                            <span class="hidden truncate text-slate-500 sm:block">{ad.company ?? ''}{ad.domain ? ` · ${ad.domain}` : ''}</span>
                            {#if ad.ad_link}
                                <a href={ad.ad_link} target="_blank" rel="noopener noreferrer" class="shrink-0 font-semibold text-teal-700 hover:underline">View ad ↗</a>
                            {/if}
                        </li>
                    {:else}
                        <li class="px-3 py-2 text-slate-500">None.</li>
                    {/each}
                </ul>
            </div>
        {/if}
    {/if}
</section>
