<script lang="ts">
    import type { Option } from '$lib/filters.svelte';

    let { title, options, selected = $bindable(), searchable = true }: {
        title: string;
        options: Option[];
        selected: (string | number)[];
        searchable?: boolean;
    } = $props();

    // a search box only pays off for long lists
    const SEARCH_FROM = 8;

    let query = $state('');

    const filtered = $derived.by(() => {
        const term = query.trim().toLowerCase();
        return term ? options.filter((o) => o.name.toLowerCase().includes(term)) : options;
    });
</script>

<details open class="group border-b border-slate-700 p-4">
    <summary
        class="flex cursor-pointer list-none items-center justify-between rounded text-xs font-semibold tracking-wider text-slate-400 uppercase
               focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-400"
    >
        <span>
            {title}
            {#if selected.length > 0}
                <span class="ml-1 rounded-full bg-teal-500/20 px-1.5 py-0.5 font-mono text-[10px] text-teal-300 normal-case">
                    {selected.length}
                </span>
            {/if}
        </span>
        <span class="transition-transform group-open:rotate-180">▾</span>
    </summary>

    {#if searchable && options.length >= SEARCH_FROM}
        <input
            type="search"
            placeholder="Search {title.toLowerCase()}"
            aria-label="Search {title.toLowerCase()}"
            class="mt-2 w-full rounded-md border-slate-600 bg-slate-900 px-2 py-1 text-sm text-slate-200 placeholder:text-slate-500 focus:border-teal-400 focus:ring-teal-400"
            bind:value={query}
        />
    {/if}

    <ul class="mt-2">
        {#each filtered as option (option.id)}
            <li>
                <label class="flex cursor-pointer items-center gap-3 rounded-md px-2 py-1.5 text-slate-400 hover:bg-slate-800 has-[:checked]:text-white">
                    <input
                        type="checkbox"
                        class="size-4 shrink-0 appearance-none rounded-sm border border-slate-500 bg-slate-900 checked:border-teal-400"
                        value={option.id}
                        bind:group={selected}
                    />
                    <span class="text-sm capitalize">{option.name}</span>
                </label>
            </li>
        {:else}
            <li class="px-2 py-1.5 text-xs text-slate-500">No matches</li>
        {/each}
    </ul>
</details>

<style>
    input[type='checkbox'] {
        appearance: none;
        outline: none;
        box-shadow: none;
    }

    input[type='checkbox']:focus {
        outline: none;
        box-shadow: none;
    }

    /* keyboard focus stays visible; mouse clicks don't show a ring */
    input[type='checkbox']:focus-visible {
        outline: 2px solid #2dd4bf;
        outline-offset: 2px;
    }

    input[type='checkbox']:checked {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none' stroke='%232dd4bf' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3.5 8.5l3 3 6-7'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 80%;
    }
</style>
