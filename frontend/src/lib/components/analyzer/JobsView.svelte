<script lang="ts">
    import {
        weeklySkills, periodShare, slopeData, specificity, topSkills, CATEGORIES, PERIODS, SERIES_COLORS,
        FIRST_SCRAPE, weekLabel
    } from '$lib/analyzerMock';
    import { EXPERIENCE_LABELS } from '$lib/jobs';
    import TopSkillsBars from './TopSkillsBars.svelte';
    import SlopeChart from './SlopeChart.svelte';
    import SpecificityScatter from './SpecificityScatter.svelte';
    import CoOccurrence from './CoOccurrence.svelte';
    import CategoryTreemap from './CategoryTreemap.svelte';
    import ExperienceLadder from './ExperienceLadder.svelte';
    import DomainCityCards from './DomainCityCards.svelte';
    import PreviewSection from './PreviewSection.svelte';
    import type { Job } from '$lib/types';
    import type { CoverageResult } from '$lib/api/fetchCoverage';

    let {
        domains,
        cities,
        jobs,
        jobsStatus,
        coverage
    }: {
        domains: string[];
        cities: string[];
        jobs: Job[];
        jobsStatus: 'loading' | 'ready' | 'error';
        coverage: CoverageResult | null;
    } = $props();

    let domain = $state('All domains');
    let level = $state('all');
    let city = $state('All cities');
    let period = $state<string>(PERIODS[0]);

    // view 1: most required skills
    const top = $derived(topSkills({ domain, level, city, period }));
    const levelLabel = $derived(level === 'all' ? 'All levels' : EXPERIENCE_LABELS[level]);

    // the views below are still to be redesigned one by one; they keep their current behaviour
    const trend = $derived(weeklySkills(domain, PERIODS[0]));
    const weekly = $derived(weeklySkills(domain, period));
    const candidates = $derived(trend.skills.slice(0, SERIES_COLORS.length).map((s) => s.concept));
    const colorOf = (concept: string) => {
        const i = candidates.indexOf(concept);
        return i < 0 ? null : SERIES_COLORS[i];
    };
    const pickedSet = $derived(new Set(candidates.slice(0, 6)));
    const slope = $derived(slopeData(domain));
    const scatter = $derived(specificity(domains));
    const shareOf = $derived(new Map(weekly.skills.map((s) => [s.concept, periodShare(s, weekly.totals)])));
    const treemap = $derived(
        CATEGORIES.map((c) => ({ name: c.name, skills: c.concepts.map((k) => ({ concept: k, share: shareOf.get(k) ?? 0 })) }))
    );

    const selectClass = 'rounded-md border-slate-300 py-1 pr-8 text-sm focus:border-teal-500 focus:ring-teal-500';
</script>

<h2 class="mb-1 text-sm font-semibold tracking-wide text-slate-700 uppercase">General details</h2>

{#if jobsStatus === 'loading'}
    <p class="text-sm text-slate-500">Loading ads…</p>
{:else if jobsStatus === 'error'}
    <p class="text-sm text-red-700">The ads could not be loaded. Is the API running?</p>
{:else}
    <p class="mb-3 text-xs text-slate-600">{jobs.length.toLocaleString()} extracted jobs</p>
    <div class="flex flex-col gap-4">
        <ExperienceLadder {jobs} />
        <DomainCityCards {jobs} {domains} {coverage} />
    </div>
{/if}

<PreviewSection>

<div class="mb-4 flex flex-wrap items-center gap-3">
    <select aria-label="Domain" class={selectClass} bind:value={domain}>
        <option>All domains</option>
        {#each domains as d (d)}<option>{d}</option>{/each}
    </select>
    <select aria-label="Experience level" class={selectClass} bind:value={level}>
        <option value="all">All levels</option>
        {#each Object.entries(EXPERIENCE_LABELS) as [value, label] (value)}<option {value}>{label}</option>{/each}
    </select>
    <select aria-label="City" class={selectClass} bind:value={city}>
        <option>All cities</option>
        {#each cities as c (c)}<option>{c}</option>{/each}
    </select>
    <select aria-label="Period" class={selectClass} bind:value={period}>
        {#each PERIODS as p (p)}<option>{p}</option>{/each}
    </select>
    <span class="text-[11px] text-slate-500">Dated ads since the first scrape ({weekLabel(FIRST_SCRAPE)} 2026); older ads have no date</span>
</div>

<section class="mb-4 rounded-xl border border-slate-200 bg-white p-4">
    <h3 class="text-sm font-semibold text-slate-900">Most required skills</h3>
    <p class="mb-3 text-xs text-slate-500">
        Top 10 by % of the {top.postings.toLocaleString()} postings with extracted skills · each skill counted once per job, by ESCO concept ·
        {domain} · {levelLabel} · {city} · {period}
    </p>
    <TopSkillsBars skills={top.skills} postings={top.postings} />
</section>

<div class="mb-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">Rising and fading skills — rank change</h3>
        <p class="mb-3 text-xs text-slate-500">
            First two dated weeks vs the last two (data since {weekLabel(FIRST_SCRAPE)} 2026), independent of the period filter · lines only for skills that moved · highlighted skills are colored
        </p>
        <SlopeChart startLabel={slope.startLabel} endLabel={slope.endLabel} rows={slope.rows} highlighted={pickedSet} {colorOf} />
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">Specificity — common vs specialised</h3>
        <p class="mb-3 text-xs text-slate-500">
            Across all domains · up: most of the skill's postings fall in one domain · right: asked for in many postings · lines split at the median
        </p>
        <SpecificityScatter points={scatter} highlighted={pickedSet} {colorOf} />
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">Skill bundles — asked for together</h3>
        <p class="mb-3 text-xs text-slate-500">Share of the selected skill's jobs that also require each other skill</p>
        <CoOccurrence concepts={candidates} />
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <div class="flex flex-wrap items-baseline justify-between gap-2">
            <h3 class="text-sm font-semibold text-slate-900">Skill areas — category → skill</h3>
            <span class="rounded border border-amber-300 bg-amber-50 px-1.5 py-0.5 text-[10px] font-semibold text-amber-800">groups need esco/graph.py</span>
        </div>
        <p class="mb-3 text-xs text-slate-500">Area = share of postings · {period} · mock groups (ESCO's own hierarchy is coarse for IT)</p>
        <CategoryTreemap groups={treemap} />
    </section>

</div>
</PreviewSection>
