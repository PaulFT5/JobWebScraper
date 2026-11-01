<script lang="ts">
    // TEMPORARY: sets a mock match score so the score colors can be previewed with each palette
    import { mockScore } from '$lib/mockScore.svelte';

    const OPTIONS: { value: number | null; label: string }[] = [
        { value: null, label: 'Off' },
        { value: 25, label: 'Weak 25' },
        { value: 55, label: 'Partial 55' },
        { value: 85, label: 'Strong 85' }
    ];
</script>

<div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-white/90 p-0.5 shadow-sm backdrop-blur" role="radiogroup" aria-label="Mock match score (temporary)">
    <span class="px-1.5 text-[10px] font-semibold tracking-wide text-slate-400 uppercase">Mock score</span>
    {#each OPTIONS as o (o.label)}
        <button
            type="button"
            role="radio"
            aria-checked={mockScore.value === o.value}
            class="cursor-pointer rounded-md px-2 py-1 text-xs font-semibold focus-visible:outline-2 focus-visible:outline-teal-500
                   {mockScore.value === o.value ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'}"
            onclick={() => (mockScore.value = o.value)}
        >
            {o.label}
        </button>
    {/each}
</div>
