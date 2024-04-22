<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { collectionsModels } from '$lib/stores';
	import { removeFirstHashWord, isValidHttpUrl } from '$lib/utils';
	import { tick, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { CollectionApi, type ICollection } from '$lib/apis/collections';
	import Translate from '$lib/components/common/Translate.svelte';
	const i18n = getContext('i18n');

	export let prompt = '';

	const dispatch = createEventDispatcher();
	let selectedIdx = 0;

	let filteredItems: ICollection[] = [];
	let collections: ICollection[] = [];
	const collectionApi = new CollectionApi();

	$: collections = [
		...$collectionsModels.filter((collection) =>
			collection.name.includes(prompt.split(' ')?.at(0)?.substring(1) ?? '')
		)
	];

	const setCollections = () => {
		return collectionApi.find().then((collections) => {
			collectionsModels.set(collections);
		});
	};

	onMount(() => {
		let checked = false;
		collectionsModels.subscribe((values: ICollection[]) => {
			if ((!values || !values.length) && !checked) {
				checked = true;
				return setCollections();
			}
			collections = values.map((collection) => ({
				...collection
			}));
		});
	});

	$: filteredCollections = collections
		.filter((collection) => collection.name.includes(prompt.split(' ')?.at(0)?.substring(1) ?? ''))
		.sort((a, b) => a.name.localeCompare(b.name));

	$: filteredItems = [...filteredCollections];

	$: if (prompt) {
		selectedIdx = 0;

		console.log(filteredCollections);
	}

	export const selectUp = () => {
		selectedIdx = Math.max(0, selectedIdx - 1);
	};

	export const selectDown = () => {
		selectedIdx = Math.min(selectedIdx + 1, filteredItems.length - 1);
	};

	const confirmSelect = async (doc) => {
		dispatch('select', {
			...doc,
			type: 'collection',
			title: doc.content,
			collection_names: [doc.key]
		});

		prompt = removeFirstHashWord(prompt);
		const chatInputElement = document.getElementById('chat-textarea');

		await tick();
		chatInputElement?.focus();
		await tick();
	};

	const confirmSelectWeb = async (url) => {
		dispatch('url', url);

		prompt = removeFirstHashWord(prompt);
		const chatInputElement = document.getElementById('chat-textarea');

		await tick();
		chatInputElement?.focus();
		await tick();
	};
</script>

{#if filteredItems.length > 0 || prompt.split(' ')?.at(0)?.substring(1).startsWith('http')}
	<div class="md:px-2 mb-3 text-left w-full absolute bottom-0 left-0 right-0">
		<div class="flex w-full px-2">
			<div class=" bg-gray-100 dark:bg-gray-700 w-10 rounded-l-xl text-center">
				<div class=" text-lg font-semibold mt-2">#</div>
			</div>

			<div class="max-h-60 flex flex-col w-full rounded-r-xl bg-white">
				<div class="m-1 overflow-y-auto p-1 rounded-r-xl space-y-0.5">
					{#each filteredItems as doc, docIdx}
						<button
							class=" px-3 py-1.5 rounded-xl w-full text-left {docIdx === selectedIdx
								? ' bg-gray-100 selected-command-option-button'
								: ''}"
							type="button"
							on:click={() => {
								console.log(doc);

								confirmSelect(doc);
							}}
							on:mousemove={() => {
								selectedIdx = docIdx;
							}}
							on:focus={() => {}}
						>
							<div class=" font-medium text-black line-clamp-1">
								{`#${doc.name}`}
							</div>

							<div class=" text-xs text-gray-600 line-clamp-1">
								{doc.content}
							</div>
						</button>
					{/each}

					{#if prompt.split(' ')?.at(0)?.substring(1).startsWith('http')}
						<button
							class="px-3 py-1.5 rounded-xl w-full text-left bg-gray-100 selected-command-option-button"
							type="button"
							on:click={() => {
								const url = prompt.split(' ')?.at(0)?.substring(1);
								if (isValidHttpUrl(url)) {
									confirmSelectWeb(url);
								} else {
									toast.error(
										$i18n.t(
											'Oops! Looks like the URL is invalid. Please double-check and try again.'
										)
									);
								}
							}}
						>
							<div class=" font-medium text-black line-clamp-1">
								{prompt.split(' ')?.at(0)?.substring(1)}
							</div>

							<div class=" text-xs text-gray-600 line-clamp-1"><Translate t="Web" /></div>
						</button>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
