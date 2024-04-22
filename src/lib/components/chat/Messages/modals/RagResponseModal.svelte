<script lang="ts">
	import type { IDocuments, RAGResponse } from '$lib/apis/documents';
	import { IconsTypes } from '$lib/components/svg/icon-types';
	import SvgIcon from '$lib/components/svg/SvgIcon.svelte';
	import Modal from '../../../common/Modal.svelte';
	import Translate from '$lib/components/common/Translate.svelte';
	import { DocumentsApi } from '$lib/apis/documents';
	import { onMount } from 'svelte';
	import { collectionsModels } from '$lib/stores';
	import { CollectionApi, type ICollection } from '$lib/apis/collections';
	export let show = false;
	export let documents: RAGResponse[] = [];
	const documentsApi = new DocumentsApi();
	const collectionApi = new CollectionApi();
	let collectionsMap: Record<string, ICollection> = {};
	let docs: IDocuments[] = [];
	let metaPageValues: Record<string, number[]> = {};
	const toggleModal = () => {
		show = !show;
	};
	let sending = false;
	const ready = (documents: IDocuments[]) => {
		docs = documents;
	};

	const extraMeta = () => {
		const metaRecords: Record<string, number[]> = {};
		for (const doc of documents) {
			for (const meta of doc.metadatas) {
				for (const file of meta) {
					const source = file.source;
					const filename: string = source.split('/').pop() || '';
					metaRecords[filename] = metaRecords[filename] || [];
					if (metaRecords[filename].indexOf(file.page) !== -1) {
						continue;
					}
					metaRecords[filename].push(file.page);
				}
			}
		}
		metaPageValues = metaRecords;
	};

	const sendToCollection = async () => {
		extraMeta();
		documentsApi.findDocsByNameInCollection(documents).then(ready);
	};

	$: if (documents.length && !docs.length && !sending) {
		sending = true;
		sendToCollection();
	}

	const getCollection = () => {
		collectionApi.find().then((collections) => {
			if (!collections.length) {
				return;
			}
			collectionsModels.set(collections);
		});
	};

	const downloadFile = (doc: IDocuments) => {
		documentsApi.downloadDoc(doc);
	};

	const sendPages = (fileName: string) => {
		return metaPageValues[fileName].join(', '); // metaPageValues[fileName].map((m, index) => m + (index < length - 1 ? ', ' : '');
	};

	onMount(() => {
		collectionsModels.subscribe((value) => {
			if (!value.length) {
				return getCollection();
			}
			value.forEach((collection) => {
				collectionsMap[collection.key] = collection;
			});
		});
	});
</script>

<Modal size="sm" bind:show>
	<div class="flex justify-between dark:text-gray-300 px-5 py-4">
		<div class="text-lg font-medium self-center">
			<Translate t="Retrieval Augmented Generation" />
		</div>
		<button on:click={toggleModal} class="self-center">
			<SvgIcon icon={IconsTypes.CLOSE} />
		</button>
	</div>
	<hr class=" dark:border-gray-700 my-2.5" />

	<div class="px-5 py-4">
		{#if docs.length}
			{#each docs as doc}
				<div class="flex justify-between">
					<div class="flex flex-col flex-grow mr-3">
						<div class="text-sm font-medium">{doc.name}</div>
						<div class="text-xs flex">
							{#if collectionsMap[doc.collection].name}
								<div class="mr-1">
									<Translate t="Collection" />: {collectionsMap[doc.collection].name}
								</div>
							{/if}
							<!-- {#if metaPageValues[doc.original_filename || doc.filename]}
								<div>
									<Translate
										t={metaPageValues[doc.original_filename || doc.filename].length > 1
											? 'Pages'
											: 'Page'}
									/>: {sendPages(doc.original_filename || doc.filename)}
								</div>
							{/if} -->
						</div>
					</div>
					<div class="flex">
						<button
							class="px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
							on:click={() => downloadFile(doc)}
						>
							<SvgIcon icon={IconsTypes.DOWNLOAD} size={16} />
						</button>
					</div>
				</div>
				<hr class=" dark:border-gray-700 my-2.5" />
			{/each}
		{:else}
			<div class="text-center">
				<Translate t="Loading..." />
			</div>
		{/if}
	</div></Modal
>
