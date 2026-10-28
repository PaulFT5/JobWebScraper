<script lang="ts">
    import ScoreCard from '$lib/components/ScoreCard.svelte';
    import JobPanel from '$lib/components/JobPanel.svelte';
    import JobDetails from '$lib/components/JobDetails.svelte';
</script>

<div class="flex h-screen flex-col">
    <ScoreCard />
    <div class="flex min-h-0 flex-1 flex-col bg-slate-50 px-6 pt-5">
        <JobPanel />
    </div>
</div>

<JobDetails />