<script lang="ts">
	import LoaderIcon from '../svg/LoaderIcon.svelte';
	import DocumentIcon from '../svg/DocumentIcon.svelte';
	export let doc;
</script>

<div class="p-2.5 bg-red-400 text-white rounded-lg">
	{#if doc}
		<DocumentIcon />
	{:else}
		<LoaderIcon />
	{/if}
</div>
