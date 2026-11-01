<script lang="ts">
    import type { Job } from '$lib/types';
    import type { CoverageResult } from '$lib/api/fetchCoverage';

    let { jobs, domains, coverage }: { jobs: Job[]; domains: string[]; coverage: CoverageResult | null } = $props();

    // the API sends the scrape-filter slugs; show the real names
    const CITY_NAMES: Record<string, string> = { timisoara: 'Timișoara', bucuresti: 'București', brasov: 'Brașov' };
    const cityName = (c: string) => CITY_NAMES[c] ?? c.charAt(0).toUpperCase() + c.slice(1);

    // clicking a bar filters the other card; clicking it again clears
    let city = $state<string | null>(null);
    let domain = $state<string | null>(null);

    const count = (list: Job[], key: (j: Job) => string | null) => {
        const m = new Map<string, number>();
        for (const j of list) {
            const k = key(j);
            if (k) m.set(k, (m.get(k) ?? 0) + 1);
        }
        return m;
    };

    const everDomains = $derived(count(jobs, (j) => j.domain));
    const domainCounts = $derived(count(city ? jobs.filter((j) => j.city === city) : jobs, (j) => j.domain));
    const cityCounts = $derived(count(domain ? jobs.filter((j) => j.domain === domain) : jobs, (j) => j.city));

    const domainRows = $derived(
        [...domainCounts.entries()].filter(([d]) => everDomains.has(d)).sort((a, b) => b[1] - a[1])
    );
    // domains with no extracted ad at all (e.g. Management, scraped only after the 2026-10-22 ID fix)
    const queuedOnly = $derived(domains.filter((d) => !everDomains.has(d)));
    const queuedOf = (d: string) =>
        coverage?.status === 'ready' ? coverage.data.queued_by_domain.find((q) => q.domain === d)?.queued ?? null : null;

    const cityRows = $derived([...cityCounts.entries()].sort((a, b) => b[1] - a[1]));
    const domainTotal = $derived(domainRows.reduce((a, [, n]) => a + n, 0));
    const cityTotal = $derived(cityRows.reduce((a, [, n]) => a + n, 0));
    const domainMax = $derived(Math.max(1, ...domainRows.map(([, n]) => n)));
    const cityMax = $derived(Math.max(1, ...cityRows.map(([, n]) => n)));

    const pct = (n: number, of: number) => (of ? ((n / of) * 100).toFixed(1) : '0.0') + '%';

    // top domain in each city over all its ads, for the summary under the city card
    const topDomainPerCity = $derived(
        cityRows.map(([c]) => {
            const inCity = count(jobs.filter((j) => j.city === c), (j) => j.domain);
            const [d, n] = [...inCity.entries()].sort((a, b) => b[1] - a[1])[0] ?? ['—', 0];
            const total = [...inCity.values()].reduce((a, b) => a + b, 0);
            return { city: c, domain: d, n, share: pct(n, total) };
        })
    );

    const rowClass = (active: boolean, dimmed: boolean) =>
        `grid w-full cursor-pointer grid-cols-[11rem_1fr] items-center gap-3 rounded px-1 py-0.5 text-left text-xs
         focus-visible:outline-2 focus-visible:outline-teal-500 hover:bg-slate-50
         ${active ? 'bg-teal-50 ring-1 ring-teal-600' : ''} ${dimmed ? 'opacity-50' : ''}`;
</script>

<div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
    <section class="flex flex-col rounded-xl border border-slate-200 bg-white p-4">
        <header class="-mx-4 -mt-4 mb-3 rounded-t-xl border-b border-(--card-head-border) bg-(--card-head-bg) px-4 py-3">
            <h3 class="text-sm font-semibold text-(--card-head-fg)">Ads per domain</h3>
        </header>
        <ul class="space-y-0.5">
            {#each domainRows as [d, n] (d)}
                <li>
                    <button
                        type="button"
                        class={rowClass(domain === d, domain !== null && domain !== d)}
                        aria-pressed={domain === d}
                        onclick={() => (domain = domain === d ? null : d)}
                    >
                        <span class="truncate text-slate-700">{d}</span>
                        <span class="flex items-center gap-2">
                            <span class="h-3.5 shrink-0 rounded-r-[4px] bg-(--bar-domain)" style="width: calc((100% - 6.5rem) * {(n / domainMax)})"></span>
                            <span class="font-mono text-[11px] whitespace-nowrap text-slate-700">{n} <span class="text-slate-400">·</span> {pct(n, domainTotal)}</span>
                        </span>
                    </button>
                </li>
            {/each}
            {#each queuedOnly as d (d)}
                {@const q = queuedOf(d)}
                <li class="grid grid-cols-[11rem_1fr] items-center gap-3 px-1 py-0.5 text-xs">
                    <span class="truncate text-slate-500">{d}</span>
                    <span class="flex items-center gap-2">
                        <span class="h-3.5 flex-1 rounded-r-[4px] border border-dashed border-slate-300"></span>
                        <span class="rounded-full border border-slate-300 px-2 text-[10px] text-slate-500">
                            0 extracted{q !== null ? ` · ${q} queued` : ' · queued'}
                        </span>
                    </span>
                </li>
            {/each}
        </ul>
        <p class="mt-auto pt-3 text-[11px] text-slate-500">
            *click a domain to filter cities
            {#if city}
                <span class="ml-2 text-slate-600">· showing {cityName(city)} only</span>
                <button type="button" class="ml-1 cursor-pointer font-semibold text-teal-700 hover:underline" onclick={() => (city = null)}>clear ✕</button>
            {/if}
        </p>
    </section>

    <!-- never taller than the domain card: zero own height, stretched to the row, scrolls if it ever overflows -->
    <section class="flex flex-col rounded-xl border border-slate-200 bg-white p-4 lg:h-0 lg:min-h-full lg:overflow-y-auto">
        <header class="-mx-4 -mt-4 mb-3 rounded-t-xl border-b border-(--card-head-border) bg-(--card-head-bg) px-4 py-3">
            <h3 class="text-sm font-semibold text-(--card-head-fg)">Ads per city</h3>
        </header>
        <ul class="space-y-0.5">
            {#each cityRows as [c, n] (c)}
                <li>
                    <button
                        type="button"
                        class={rowClass(city === c, city !== null && city !== c)}
                        aria-pressed={city === c}
                        onclick={() => (city = city === c ? null : c)}
                    >
                        <span class="truncate text-slate-700">{cityName(c)}</span>
                        <span class="flex items-center gap-2">
                            <span class="h-3.5 shrink-0 rounded-r-[4px] bg-(--bar-city)" style="width: calc((100% - 6.5rem) * {(n / cityMax)})"></span>
                            <span class="font-mono text-[11px] whitespace-nowrap text-slate-700">{n} <span class="text-slate-400">·</span> {pct(n, cityTotal)}</span>
                        </span>
                    </button>
                </li>
            {/each}
        </ul>
        <div class="mt-3 rounded-lg bg-slate-50 p-3">
            <h4 class="mb-1.5 text-[11px] font-semibold tracking-wide text-slate-500 uppercase">Top domain per city</h4>
            <ul class="space-y-1 text-xs">
                {#each topDomainPerCity as t (t.city)}
                    <li class="grid grid-cols-[6rem_1fr_auto] gap-2">
                        <span class="text-slate-600">{cityName(t.city)}</span>
                        <span class="truncate font-medium text-slate-800">{t.domain}</span>
                        <span class="font-mono text-[11px] text-slate-600">{t.n} <span class="text-slate-400">·</span> {t.share}</span>
                    </li>
                {/each}
            </ul>
        </div>
        <p class="mt-auto pt-3 text-[11px] text-slate-500">
            *click a city to filter domains
            {#if domain}
                <span class="ml-2 text-slate-600">· showing {domain} only</span>
                <button type="button" class="ml-1 cursor-pointer font-semibold text-teal-700 hover:underline" onclick={() => (domain = null)}>clear ✕</button>
            {/if}
        </p>
    </section>
</div>
