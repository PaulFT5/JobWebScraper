<script lang="ts">
    import { cv } from '$lib/cv.svelte';
    import type { Job } from '$lib/types';
    import type { CoverageResult } from '$lib/api/fetchCoverage';
    import CoverageCard from './CoverageCard.svelte';
    import SkillsHistogram from './SkillsHistogram.svelte';
    import PreviewSection from './PreviewSection.svelte';

    let { jobs, coverage }: { jobs: Job[]; coverage: CoverageResult | null } = $props();
    import {
        methodShare, latency, llmTiming, llmHistogram, topUnresolved, sampleCv, cvTiming,
        METHODS, METHOD_LABELS, METHOD_COLORS
    } from '$lib/analyzerMock';

    const methodTotal = METHODS.reduce((sum, m) => sum + methodShare[m], 0);
    const pct = (m: (typeof METHODS)[number]) => (methodShare[m] / methodTotal) * 100;
    const histMax = Math.max(...llmHistogram.map((b) => b.value));
    const unresolvedMax = topUnresolved[0].count;
    const fmtMs = (ms: number) => (ms < 1 ? ms.toFixed(2) : ms.toFixed(ms < 10 ? 1 : 0)) + ' ms';
</script>

<div class="mb-2 flex flex-wrap items-baseline gap-2">
    <h2 class="text-sm font-semibold tracking-wide text-slate-700 uppercase">Verified counts</h2>
    <span class="text-xs text-slate-500">Live from the database</span>
</div>
<div class="flex flex-col gap-4">
    <CoverageCard {coverage} />
    <SkillsHistogram {jobs} />
</div>

<PreviewSection title="Pending grounding statistics & timings (preview only)" note="Mock data. Fills in after the batch grounding run and once timings are stored (AN2).">

<div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">How skills were grounded</h3>
        <p class="mb-3 text-xs text-slate-500">{methodTotal.toLocaleString()} distinct job skills by grounding step</p>
        <div class="flex h-5 gap-0.5 overflow-hidden rounded">
            {#each METHODS as m (m)}
                <span
                    class="h-full first:rounded-l last:rounded-r"
                    style="width: {pct(m)}%; background: {METHOD_COLORS[m]}"
                    title="{METHOD_LABELS[m]}: {methodShare[m].toLocaleString()} ({pct(m).toFixed(1)}%)"
                ></span>
            {/each}
        </div>
        <ul class="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
            {#each METHODS as m (m)}
                <li class="flex items-center gap-2">
                    <span class="size-2.5 shrink-0 rounded-sm" style="background: {METHOD_COLORS[m]}"></span>
                    <span class="text-slate-600">{METHOD_LABELS[m]}</span>
                    <span class="ml-auto font-mono text-slate-800">{pct(m).toFixed(1)}%</span>
                </li>
            {/each}
        </ul>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">Grounding time per skill</h3>
        <p class="mb-3 text-xs text-slate-500">First lookup only; cache hits are not timed</p>
        <table class="w-full text-xs">
            <thead class="text-left text-slate-500">
                <tr><th class="pb-1.5 font-medium">Step</th><th class="pb-1.5 text-right font-medium">Median</th><th class="pb-1.5 text-right font-medium">Slowest 5%</th></tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {#each latency as row (row.method)}
                    <tr>
                        <td class="py-1.5">
                            <span class="mr-2 inline-block size-2.5 rounded-sm align-middle" style="background: {METHOD_COLORS[row.method]}"></span>{METHOD_LABELS[row.method]}
                        </td>
                        <td class="py-1.5 text-right font-mono">{fmtMs(row.median)}</td>
                        <td class="py-1.5 text-right font-mono">{fmtMs(row.p95)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
        <div class="mt-4 grid grid-cols-3 gap-2 text-center">
            <div class="rounded-lg bg-slate-50 p-2">
                <div class="font-mono text-lg font-semibold text-slate-900">{Math.round(llmTiming.cacheHitRate * 100)}%</div>
                <div class="text-[11px] text-slate-500">cache hit rate</div>
            </div>
            <div class="rounded-lg bg-slate-50 p-2">
                <div class="font-mono text-lg font-semibold text-slate-900">{llmTiming.skillsPerJob}</div>
                <div class="text-[11px] text-slate-500">skills per job</div>
            </div>
            <div class="rounded-lg bg-slate-50 p-2">
                <div class="font-mono text-lg font-semibold text-slate-900">{llmTiming.medianSec} s</div>
                <div class="text-[11px] text-slate-500">LLM time per job (median)</div>
            </div>
        </div>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">LLM extraction time per job</h3>
        <p class="mb-3 text-xs text-slate-500">Groq call duration · slowest 5% above {llmTiming.p95Sec} s</p>
        <div class="flex h-36 items-end gap-2">
            {#each llmHistogram as bin (bin.label)}
                <div class="flex h-full flex-1 flex-col items-center justify-end gap-1" title="{bin.label}: {bin.value.toLocaleString()} jobs">
                    <span class="font-mono text-[10px] text-slate-500">{bin.value}</span>
                    <span class="w-full rounded-t bg-teal-600" style="height: {(bin.value / histMax) * 80}%"></span>
                    <span class="text-[10px] whitespace-nowrap text-slate-500">{bin.label}</span>
                </div>
            {/each}
        </div>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <h3 class="text-sm font-semibold text-slate-900">Most frequent unresolved skills</h3>
        <p class="mb-3 text-xs text-slate-500">Candidates for overrides or the acronym list</p>
        <ul class="space-y-1.5">
            {#each topUnresolved as row (row.skill)}
                <li class="grid grid-cols-[9rem_1fr_3rem] items-center gap-3 text-xs" title="{row.skill}: {row.count} jobs">
                    <span class="truncate text-slate-700">{row.skill}</span>
                    <span class="h-2.5 rounded-r bg-slate-100">
                        <span class="block h-2.5 rounded-r bg-slate-400" style="width: {(row.count / unresolvedMax) * 100}%"></span>
                    </span>
                    <span class="text-right font-mono text-slate-800">{row.count}</span>
                </li>
            {/each}
        </ul>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
        <div class="flex items-baseline justify-between gap-2">
            <h3 class="text-sm font-semibold text-slate-900">Your CV</h3>
            <span class="text-[11px] text-slate-500">this session only, never stored</span>
        </div>
        <p class="mb-3 text-xs text-slate-500">
            {cv.fileName ? `"${cv.fileName}"` : 'Sample CV (no CV uploaded)'} · parsed in {cvTiming.parseSec} s · grounded in {cvTiming.groundingMs} ms
        </p>
        <table class="w-full text-xs">
            <thead class="text-left text-slate-500">
                <tr><th class="pb-1.5 font-medium">Skill</th><th class="pb-1.5 font-medium">Tier</th><th class="pb-1.5 font-medium">Step</th><th class="pb-1.5 text-right font-medium">Time</th></tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {#each sampleCv as row (row.skill)}
                    <tr>
                        <td class="py-1.5 text-slate-800">{row.skill}</td>
                        <td class="py-1.5 text-slate-600">{row.tier}</td>
                        <td class="py-1.5">
                            <span class="mr-1.5 inline-block size-2.5 rounded-sm align-middle" style="background: {METHOD_COLORS[row.method]}"></span>{METHOD_LABELS[row.method]}
                        </td>
                        <td class="py-1.5 text-right font-mono">{fmtMs(row.ms)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </section>
</div>
</PreviewSection>
