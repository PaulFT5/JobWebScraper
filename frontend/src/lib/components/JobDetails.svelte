<script lang="ts">
    import { selection, closeDetails } from '$lib/selection.svelte';
    import { parseSkills, companyInitials, salaryInfo, experienceLabel } from '$lib/jobs';

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
            <div class="flex size-10 shrink-0 items-center justify-center rounded-md bg-teal-700 text-sm font-bold text-white">
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
            <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
                <dt class="text-slate-500">Location</dt>
                <dd class="capitalize">{job.city ?? '—'}</dd>
                <dt class="text-slate-500">Domain</dt>
                <dd>{job.domain ?? '—'}</dd>
                <dt class="text-slate-500">Work type</dt>
                <dd>{job.work_type ?? '—'}</dd>
                <dt class="text-slate-500">Experience</dt>
                <dd>{experienceLabel(job) ?? 'Not specified'}</dd>
                <dt class="text-slate-500">Salary</dt>
                <dd>
                    {#if salary}
                        <span class="font-mono font-bold">{salary.value} € / month</span>
                        {#if salary.estimated}<span class="text-slate-400">(estimated)</span>{/if}
                    {:else}
                        Not listed
                    {/if}
                </dd>
            </dl>

            <section>
                <h3 class="mb-2 text-xs font-semibold tracking-wider text-slate-500 uppercase">
                    Required skills ({skills.length})
                </h3>
                <div class="flex flex-wrap gap-1.5">
                    {#each skills as skill (skill)}
                        <span class="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-700">{skill}</span>
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
                    class="block rounded-lg bg-teal-500 px-3 py-2 text-center text-sm font-semibold text-slate-900 hover:bg-teal-400 focus-visible:outline-2 focus-visible:outline-teal-700"
                >
                    Open original ad
                </a>
            </footer>
        {/if}
    </div>
{/if}
