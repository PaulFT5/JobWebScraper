<script lang="ts">
    import { selection, closeDetails } from '$lib/selection.svelte';
    import { parseSkills, companyInitials, avatarColors, salaryInfo, experienceLabel } from '$lib/jobs';

    const job = $derived(selection.details);
    const skills = $derived(job ? parseSkills(job.required_skills) : []);
    const salary = $derived(job ? salaryInfo(job) : null);

    let closeButton = $state<HTMLButtonElement>();

    $effect(() => {
        if (job) closeButton?.focus();
    });

    function onKeydown(e: KeyboardEvent) {
        if (job && e.key === 'Escape') closeDetails();
    }
</script>

<svelte:window onkeydown={onKeydown} />

{#if job}
    <!-- backdrop: click outside the panel closes it -->
    <div class="fixed inset-0 z-40 bg-slate-900/30" role="presentation" onclick={closeDetails}></div>

    <div
        class="fixed top-1/2 left-1/2 z-50 flex max-h-[85vh] w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-xl bg-white shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="job-details-title"
    >
        <header class="flex items-start gap-3 border-b border-slate-200 p-5">
            <div
                class="flex size-10 shrink-0 items-center justify-center rounded-md text-sm font-bold"
                style="background: {avatarColors(job.company).bg}; color: {avatarColors(job.company).fg}"
            >
                {companyInitials(job.company)}
            </div>
            <div class="min-w-0 flex-1">
                <h2 id="job-details-title" class="text-base font-semibold text-slate-900">{job.title}</h2>
                <p class="text-sm text-slate-500">{job.company ?? 'Unknown company'}</p>
            </div>
            <button
                bind:this={closeButton}
                type="button"
                aria-label="Close details"
                class="cursor-pointer rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-2 focus-visible:outline-teal-500"
                onclick={closeDetails}
            >
                <svg class="size-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6 6 18" /><path d="m6 6 12 12" />
                </svg>
            </button>
        </header>

        <div class="flex-1 space-y-5 overflow-y-auto p-5 text-sm">
            <dl class="fact-band">
                <dt class="band-label">Location</dt>
                <dd class="band-value capitalize">{job.city ?? '—'}</dd>
                <dt class="band-label">Domain</dt>
                <dd class="band-value">{job.domain ?? '—'}</dd>
                <dt class="band-label">Work type</dt>
                <dd class="band-value">{job.work_type ?? '—'}</dd>
                <dt class="band-label">Experience</dt>
                <dd class="band-value">{experienceLabel(job) ?? 'Not specified'}</dd>
                <dt class="band-label band-salary-label">Salary</dt>
                <dd class="band-value band-salary">
                    {#if salary}
                        <span class="band-amount">{salary.value} € / month</span>
                        {#if salary.estimated}<span class="band-note">(estimated)</span>{/if}
                    {:else}
                        <span class="band-missing">Not listed</span>
                    {/if}
                </dd>
            </dl>

            <section>
                <h3 class="skills-title mb-2 text-xs font-semibold tracking-wider uppercase">
                    Required skills ({skills.length})
                </h3>
                <div class="flex flex-wrap gap-2">
                    {#each skills as skill (skill)}
                        <span class="skill-chip">{skill}</span>
                    {/each}
                </div>
            </section>
        </div>

        {#if job.ad_link}
            <footer class="border-t border-slate-200 p-4">
                <a
                    href={job.ad_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="block rounded-lg bg-(--accent-btn) px-3 py-2 text-center text-sm font-semibold text-(--accent-btn-fg) hover:bg-(--accent-btn-hover) focus-visible:outline-2 focus-visible:outline-teal-700"
                >
                    Open original ad
                </a>
            </footer>
        {/if}
    </div>
{/if}

<style>
  .fact-band {
    display: grid;
    grid-template-columns: auto 1fr;
    column-gap: 1.25rem;
    row-gap: 0.5rem;
    margin: 0;
    padding: 0.875rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    background: #f8fafc;
  }
  .band-label {
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    align-self: baseline;
  }
  .band-value {
    margin: 0;
    font-weight: 600;
    color: #0f172a;
  }
  .band-salary-label, .band-salary {
    margin-top: 0.25rem;
    padding-top: 0.625rem;
    border-top: 1px solid #e2e8f0;
  }
  .band-amount {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 1.25rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    color: #0f766e;
  }
  .band-note {
    margin-left: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 400;
    color: #64748b;
  }
  .band-missing {
    font-weight: 500;
    color: #64748b;
  }
  .skills-title { color: #0f766e; }
  .skill-chip {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.8125rem;
    font-weight: 500;
    color: #0f766e;
    background: #f0fdfa;
    border: 1px solid #5eead4;
    border-radius: 0.375rem;
    padding: 0.25rem 0.625rem;
  }
</style>
