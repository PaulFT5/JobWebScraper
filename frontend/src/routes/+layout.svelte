<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import MockScoreSwitch from '$lib/components/MockScoreSwitch.svelte';

    let { children, data } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex min-h-screen">
    <Sidebar filters={data} />
    <main class="relative min-w-0 flex-1">
        <!-- TEMPORARY mock-score switch -->
        <div class="absolute top-3 right-4 z-20">
            <MockScoreSwitch />
        </div>
        {@render children()}
    </main>
</div>