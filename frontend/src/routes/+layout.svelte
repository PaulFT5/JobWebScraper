<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import Sidebar from '$lib/components/Sidebar.svelte';

    let { children, data } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex min-h-screen">
    <Sidebar filters={data} />
    <main class="min-w-0 flex-1">
        {@render children()}
    </main>
</div>