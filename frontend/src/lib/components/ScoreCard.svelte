<script lang="ts">
    import { cv } from '$lib/cv.svelte';
    import { selection, showDetails } from '$lib/selection.svelte';
    import { scoreTheme, scoreLabel } from '$lib/score';

    // null until the matcher is wired to the API
    const score = null as number | null;

    const job = $derived(selection.job);
    const theme = $derived(score === null ? null : scoreTheme(score));
    const cvName = $derived(cv.fileName?.replace(/\.[^.]+$/, '') ?? null);

    const heading = $derived(
        !cvName ? 'Upload your CV to begin' : !job ? 'Select a job to score' : job.title
    );
    const hint = $derived(
        !cvName
            ? 'Upload a CV to extract your skills and compare them against live job listings.'
            : !job
              ? `CV "${cvName}" loaded. Click a job to see how well it matches.`
              : `${job.company ?? 'Unknown company'} · scoring will appear here once matching is available.`
    );
    const ringCaption = $derived(score !== null ? scoreLabel(score) : job && cvName ? 'Not available yet' : 'No job selected');

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
        {#if job && !selection.details}
            <button
                type="button"
                class="w-fit cursor-pointer text-xs font-semibold text-teal-700 hover:underline focus-visible:outline-2 focus-visible:outline-teal-500"
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
