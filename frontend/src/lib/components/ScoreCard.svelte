<script lang="ts">
    import { cv } from '$lib/cv.svelte';
    import { selection, showDetails } from '$lib/selection.svelte';
    import { scoreTheme, scoreLabel } from '$lib/score';
    import { jobKey } from '$lib/jobs';
    import { fetchMatchDetail } from '$lib/api/match';
    import type { MatchReport } from '$lib/types';

    const job = $derived(selection.job);
    const ready = $derived(cv.status === 'ready');
    // real Chamfer score of the compared job, from the CV upload
    const score = $derived(ready && job ? (cv.scores[jobKey(job)] ?? null) : null);
    const theme = $derived(score === null ? null : scoreTheme(score));
    const cvName = $derived(cv.fileName?.replace(/\.[^.]+$/, '') ?? null);

    // per-requirement detail of the compared job (matched / missing)
    let report = $state<MatchReport | null>(null);
    let reportStatus = $state<'idle' | 'loading' | 'ready' | 'error'>('idle');
    let latestRequest = 0;

    $effect(() => {
        const request = ++latestRequest;
        report = null;
        if (!ready || !job || !cv.sessionId) {
            reportStatus = 'idle';
            return;
        }
        reportStatus = 'loading';
        fetchMatchDetail(cv.sessionId, job)
            .then((result) => {
                if (request !== latestRequest) return;
                report = result;
                reportStatus = 'ready';
            })
            .catch(() => {
                if (request !== latestRequest) return;
                reportStatus = 'error';
            });
    });

    const matched = $derived(report ? report.requirements.filter((r) => r.value > 0) : []);
    const total = $derived(report ? report.requirements.length : 0);

    const heading = $derived(
        !cvName ? 'Upload your CV to begin' : !job ? 'Select a job to score' : job.title
    );
    const hint = $derived.by(() => {
        if (!cvName) return 'Upload a CV to extract your skills and compare them against live job listings.';
        if (cv.status === 'analyzing') return `Reading "${cvName}" and scoring every job…`;
        if (cv.status === 'error') return 'The CV could not be analyzed. Upload it again from the sidebar.';
        if (!job) return `CV "${cvName}" scored against every job. Click a job to see what matches.`;
        if (score === null) return `${job.company ?? 'Unknown company'} · this job has no grounded skills yet, so it has no score.`;
        return `${job.company ?? 'Unknown company'} · your CV covers ${matched.length} of ${total} required skills.`;
    });
    const ringCaption = $derived(
        score !== null ? scoreLabel(score) : cv.status === 'analyzing' ? 'Scoring…' : job && ready ? 'No score' : 'No job selected'
    );

    const size = 128;
    const stroke = 10;
    const r = (size - stroke) / 2;
    const circumference = 2 * Math.PI * r;
    const offset = $derived(circumference - ((score ?? 0) / 100) * circumference);
</script>

<section class="flex shrink-0 items-center gap-8 border-b border-slate-200 bg-white px-6 py-4">
    <div class="flex min-w-0 flex-1 flex-col gap-2">
        <h2 class="truncate text-lg font-semibold text-slate-900">{heading}</h2>
        <p class="max-w-md text-xs text-slate-500">{hint}</p>

        {#if score !== null && reportStatus === 'ready' && report}
            <dl class="flex max-w-xl flex-col gap-1.5 text-xs">
                {#if matched.length > 0}
                    <div class="flex items-baseline gap-2">
                        <dt class="w-14 shrink-0 text-[10px] font-semibold tracking-wide text-slate-500 uppercase">Matched</dt>
                        <dd class="flex flex-wrap gap-1">
                            {#each matched as m (m.requirement)}
                                <span
                                    class="rounded border border-teal-200 bg-teal-50 px-1.5 py-0.5 font-mono text-[11px] text-teal-800"
                                    title={m.best_cv_skill && m.best_cv_skill !== m.requirement ? `Your CV: ${m.best_cv_skill}` : undefined}
                                >
                                    {m.requirement}
                                </span>
                            {/each}
                        </dd>
                    </div>
                {/if}
                {#if report.missing.length > 0}
                    <div class="flex items-baseline gap-2">
                        <dt class="w-14 shrink-0 text-[10px] font-semibold tracking-wide text-slate-500 uppercase">Missing</dt>
                        <dd class="flex flex-wrap gap-1">
                            {#each report.missing as name (name)}
                                <span class="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-mono text-[11px] text-slate-600">{name}</span>
                            {/each}
                        </dd>
                    </div>
                {/if}
            </dl>
        {:else if score !== null && reportStatus === 'loading'}
            <p class="text-xs text-slate-400">Loading matched skills…</p>
        {:else if score !== null && reportStatus === 'error'}
            <p class="text-xs text-slate-500">Matched skills unavailable. Upload the CV again if the API was restarted.</p>
        {/if}

        {#if job && !selection.details}
            <button
                type="button"
                class="w-fit cursor-pointer text-xs font-semibold text-(--accent-text) hover:underline focus-visible:outline-2 focus-visible:outline-teal-500"
                onclick={() => showDetails(job)}
            >
                Show job details
            </button>
        {/if}
    </div>

    <div class="relative shrink-0" style="width: {size}px; height: {size}px">
        <svg width={size} height={size} class="-rotate-90" aria-hidden="true">
            <circle cx={size / 2} cy={size / 2} {r} fill="none" class="stroke-slate-200" stroke-width={stroke} />
            {#if theme}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    {r}
                    fill="none"
                    class="transition-all duration-500 {theme.ring}"
                    stroke-width={stroke}
                    stroke-linecap="round"
                    stroke-dasharray={circumference}
                    stroke-dashoffset={offset}
                />
            {/if}
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span class="font-mono text-2xl leading-none font-semibold {theme ? theme.text : 'text-slate-400'}">
                {score !== null ? `${score}%` : '—'}
            </span>
            <span class="mt-1 px-3 text-[11px] leading-tight text-slate-500">{ringCaption}</span>
        </div>
    </div>

    <!-- balances the text column so the ring sits in the middle -->
    <div class="flex-1"></div>
</section>
