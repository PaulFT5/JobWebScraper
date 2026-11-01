<script lang="ts">
    import type { Snippet } from 'svelte';

    let {
        title = 'Pending grounding & time-series backfill (preview only)',
        note = 'Mock data. These views show real numbers once grounding and dated extractions exist.',
        spaced = true,
        children
    }: { title?: string; note?: string; spaced?: boolean; children: Snippet } = $props();
</script>

<!-- previews are dimmed so they can't be mistaken for verified counts; hover brings back full colour for inspection -->
<section class={spaced ? 'mt-12 border-t border-dashed border-slate-300 pt-6' : ''} aria-label={title}>
    <div class="mb-4 flex flex-wrap items-baseline gap-2">
        <h2 class="text-sm font-semibold tracking-wide text-slate-500 uppercase">{title}</h2>
        <span class="rounded border border-slate-300 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500">PREVIEW</span>
        <span class="text-xs text-slate-500">{note}</span>
    </div>
    <div class="opacity-45 grayscale-80 transition duration-200 hover:opacity-100 hover:grayscale-0 focus-within:opacity-100 focus-within:grayscale-0">
        {@render children()}
    </div>
</section>
