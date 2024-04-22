<script lang="ts">
	import { CollectionApi } from '$lib/apis/collections';
	import { collectionsModels } from '$lib/stores';
	import { onMount } from 'svelte';
	export let collections: string[] = [];
	const collectionApi = new CollectionApi();
	let collectionRecords: Record<string, boolean> = {};
	const checkCollections = () => {
		for (const collection of collections) {
			collectionRecords[collection] = true;
		}
	};
	const pullCollections = async () => {
		await collectionApi.find().then(collectionsModels.set);
	};
	onMount(pullCollections);
	$: if (Object.keys(collectionRecords).length) {
		collections = Object.keys(collectionRecords).filter((key) => collectionRecords[key]);
	} else if (!Object.keys(collectionRecords).length && collections.length) {
		checkCollections();
	}
</script>

<div class="grid grid-cols-4">
	{#each $collectionsModels as collection}
		<div class="flex space-x-2 text-sm">
			<input
				type="checkbox"
				bind:checked={collectionRecords[collection.key]}
				value={collection.key}
			/>
			<div class="capitalize">{collection.name}</div>
		</div>
	{/each}
</div>
