<script lang="ts">
    import { selection } from '$lib/selection.svelte';
    import { cv } from '$lib/cv.svelte';
    import { parseSkills } from '$lib/jobs';
    import { scoreTheme, scoreLabel } from '$lib/score';
    import PreviewSection from './PreviewSection.svelte';
    import {
        sampleCv, mockSimilarity, mockMethod, METRICS, METRIC_OFFSETS, METHOD_LABELS, METHOD_COLORS
    } from '$lib/analyzerMock';

    let noise = $state(0.35);
    let gapThreshold = $state(0.5);

    const job = $derived(selection.job);
    const requirements = $derived(job ? parseSkills(job.required_skills).slice(0, 12) : []);
    const cvSkills = sampleCv.map((s) => s.skill);

    // rows = job requirements, columns = CV skills; values below the noise threshold become 0
    const matrix = $derived(
        requirements.map((r) => cvSkills.map((c) => {
            const v = mockSimilarity(r, c);
            return v < noise ? 0 : v;
        }))
    );

    // directed Chamfer: best CV value per requirement, then the mean
    const best = $derived(
        matrix.map((row) => {
            let col = 0;
            row.forEach((v, i) => { if (v > row[col]) col = i; });
            return { col, value: row[col] ?? 0 };
        })
    );
    const chamfer = $derived(best.length ? Math.round((best.reduce((s, b) => s + b.value, 0) / best.length) * 100) : 0);
    const missing = $derived(requirements.filter((_, i) => best[i].value < gapThreshold));
    const matchedCols = $derived(new Set(best.filter((b) => b.value >= gapThreshold).map((b) => b.col)));
    const extra = $derived(cvSkills.filter((_, i) => !matchedCols.has(i)));
    const theme = $derived(scoreTheme(chamfer));

    // one teal hue, light → dark, for magnitude; empty cells stay on the surface color
    function cellStyle(v: number): string {
        if (v === 0) return 'background: #f8fafc';
        const alpha = 0.15 + v * 0.85;
        return `background: rgba(13, 148, 136, ${alpha.toFixed(2)}); color: ${v > 0.6 ? '#fff' : '#0f172a'}`;
    }
</script>

<PreviewSection
    spaced={false}
    title="Matching (preview only)"
    note="Sample CV and mock similarities. Real scores arrive with the CV parser, the similarity matrix and Chamfer (minimal slice)."
>

{#if !job}
    <div class="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
        <h3 class="text-sm font-semibold text-slate-900">No job selected</h3>
        <p class="max-w-sm text-xs text-slate-500">
            The matching metrics are computed for one CV against one job. Pick a job from the available positions and come back here.
        </p>
        <a href="/" class="mt-1 rounded-lg bg-teal-500 px-3 py-1.5 text-sm font-semibold text-slate-900 hover:bg-teal-400 focus-visible:outline-2 focus-visible:outline-teal-500">
            Choose a job
        </a>
    </div>
{:else}
    <div class="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_20rem]">
        <section class="rounded-xl border border-slate-200 bg-white p-4">
            <div class="mb-3 flex flex-wrap items-baseline justify-between gap-2">
                <div class="min-w-0">
                    <h3 class="truncate text-sm font-semibold text-slate-900">{job.title}</h3>
                    <p class="text-xs text-slate-500">
                        {job.company ?? 'Unknown company'} · {requirements.length} requirements × {cvSkills.length} CV skills
                        · {cv.fileName ? `"${cv.fileName}"` : 'sample CV'}
                    </p>
                </div>
                <span class="text-[11px] text-slate-500">cell = similarity 0–1, after the noise threshold</span>
            </div>

            {#if requirements.length === 0}
                <p class="text-sm text-slate-500">This job has no extracted skills.</p>
            {:else}
                <div class="overflow-x-auto">
                    <table class="border-separate border-spacing-0.5 text-[11px]">
                        <thead>
                            <tr>
                                <th class="sticky left-0 bg-white"></th>
                                {#each cvSkills as c (c)}
                                    <th class="h-24 w-12 align-bottom font-medium text-slate-600">
                                        <span class="inline-block w-24 origin-bottom-left translate-x-5 -rotate-45 text-left whitespace-nowrap">{c}</span>
                                    </th>
                                {/each}
                            </tr>
                        </thead>
                        <tbody>
                            {#each requirements as r, i (r)}
                                <tr>
                                    <th class="sticky left-0 max-w-44 truncate bg-white pr-2 text-left font-normal text-slate-700" title={r}>{r}</th>
                                    {#each matrix[i] as v, j (j)}
                                        <td
                                            class="h-8 w-12 rounded text-center font-mono {best[i].col === j && v > 0 ? 'ring-2 ring-slate-900 ring-inset' : ''}"
                                            style={cellStyle(v)}
                                            title="{r} ↔ {cvSkills[j]}: {v.toFixed(2)}"
                                        >{v ? v.toFixed(2).replace(/^0/, '') : ''}</td>
                                    {/each}
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
                <p class="mt-2 text-[11px] text-slate-500">Outlined cell = best CV skill for that requirement (what Chamfer uses).</p>
            {/if}
        </section>

        <div class="flex flex-col gap-4">
            <section class="rounded-xl border border-slate-200 bg-white p-4">
                <h3 class="text-sm font-semibold text-slate-900">Score</h3>
                <div class="mt-2 flex items-baseline gap-2">
                    <span class="font-mono text-4xl font-semibold {theme.text}">{chamfer}%</span>
                    <span class="rounded border px-1.5 py-0.5 text-[11px] font-semibold {theme.badge}">{scoreLabel(chamfer)}</span>
                </div>
                <ul class="mt-4 space-y-2">
                    {#each METRICS as m (m.id)}
                        {@const value = Math.max(0, Math.min(100, chamfer + METRIC_OFFSETS[m.id]))}
                        <li title={m.note}>
                            <div class="flex items-center justify-between text-xs">
                                <span class="text-slate-700">{m.name}</span>
                                <span class="font-mono {m.ready ? 'text-slate-900' : 'text-slate-400'}">{m.ready ? `${value}%` : `${value}% · planned`}</span>
                            </div>
                            <div class="mt-1 h-1.5 rounded bg-slate-100">
                                <div class="h-1.5 rounded {m.ready ? 'bg-teal-600' : 'bg-slate-300'}" style="width: {value}%"></div>
                            </div>
                        </li>
                    {/each}
                </ul>
            </section>

            <section class="rounded-xl border border-slate-200 bg-white p-4">
                <h3 class="mb-2 text-sm font-semibold text-slate-900">Thresholds</h3>
                <label class="block text-xs text-slate-600">
                    Noise threshold <span class="float-right font-mono">{noise.toFixed(2)}</span>
                    <input type="range" min="0" max="0.8" step="0.05" bind:value={noise} class="mt-1 w-full accent-teal-600" />
                </label>
                <label class="mt-3 block text-xs text-slate-600">
                    Missing below <span class="float-right font-mono">{gapThreshold.toFixed(2)}</span>
                    <input type="range" min="0.2" max="0.9" step="0.05" bind:value={gapThreshold} class="mt-1 w-full accent-teal-600" />
                </label>
            </section>
        </div>

        <section class="rounded-xl border border-slate-200 bg-white p-4 xl:col-span-2">
            <h3 class="mb-3 text-sm font-semibold text-slate-900">What matches what</h3>
            <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
                <div class="lg:col-span-2">
                    <table class="w-full text-xs">
                        <thead class="text-left text-slate-500">
                            <tr>
                                <th class="pb-1.5 font-medium">Requirement</th>
                                <th class="pb-1.5 font-medium">Found by</th>
                                <th class="pb-1.5 font-medium">Best CV skill</th>
                                <th class="pb-1.5 text-right font-medium">Score</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            {#each requirements as r, i (r)}
                                {@const method = mockMethod(r)}
                                {@const ok = best[i].value >= gapThreshold}
                                <tr>
                                    <td class="py-1.5 text-slate-800">{r}</td>
                                    <td class="py-1.5 text-slate-600">
                                        <span class="mr-1.5 inline-block size-2.5 rounded-sm align-middle" style="background: {METHOD_COLORS[method]}"></span>{METHOD_LABELS[method]}
                                    </td>
                                    <td class="py-1.5 {ok ? 'text-slate-800' : 'text-slate-400'}">{ok ? cvSkills[best[i].col] : '— missing'}</td>
                                    <td class="py-1.5 text-right font-mono">{best[i].value.toFixed(2)}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
                <div class="space-y-4 text-xs">
                    <div>
                        <h4 class="mb-1.5 font-semibold text-slate-700">Missing ({missing.length})</h4>
                        <div class="flex flex-wrap gap-1.5">
                            {#each missing as m (m)}<span class="rounded border border-red-200 bg-red-50 px-1.5 py-0.5 text-red-700">{m}</span>{:else}<span class="text-slate-400">None</span>{/each}
                        </div>
                    </div>
                    <div>
                        <h4 class="mb-1.5 font-semibold text-slate-700">Extra CV skills ({extra.length})</h4>
                        <div class="flex flex-wrap gap-1.5">
                            {#each extra as e (e)}<span class="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-slate-600">{e}</span>{:else}<span class="text-slate-400">None</span>{/each}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
{/if}
</PreviewSection>
