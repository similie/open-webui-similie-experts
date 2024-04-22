<script lang="ts">
	import { toast } from 'svelte-sonner';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;
	import { onMount, getContext, tick } from 'svelte';
	import { WEBUI_NAME, documents } from '$lib/stores';
	import {
		DocumentsApi,
		createNewDoc,
		deleteDocByName,
		getDocsThroughCollection,
		type IDocuments
	} from '$lib/apis/documents';
	import { uploadDocToVectorDB } from '$lib/apis/rag';
	import { transformFileName, transformDocumentName } from '$lib/utils';
	import Translate from '$lib/components/common/Translate.svelte';
	import Checkbox from '$lib/components/common/Checkbox.svelte';
	import EditDocModal from '$lib/components/documents/EditDocModal.svelte';
	import AddDocModal from '$lib/components/documents/AddDocModal.svelte';
	import { page } from '$app/stores';
	import { CollectionApi, type ICollection } from '$lib/apis/collections';
	import SvgIcon from '$lib/components/svg/SvgIcon.svelte';
	import { IconsTypes } from '$lib/components/svg/icon-types';
	import DocumentIcon from '$lib/components/documents/DocumentIcon.svelte';
	import DropZone from '$lib/components/documents/DropZone.svelte';
	import LoaderIcon from '$lib/components/svg/LoaderIcon.svelte';

	const i18n = getContext('i18n');
	const collectionApi = new CollectionApi();
	const documentsApi = new DocumentsApi();
	let importFiles = [];
	let collection: ICollection | null = null;
	let query = '';
	let documentsImportInputElement: HTMLInputElement;
	let tags = [];
	let uploading = false;
	let showAddDocModal = false;
	let showEditDocModal = false;
	let selectedDoc;
	let selectedTag = '';
	let fileCount = 0;
	const sendFileToVector = (file: File) => {
		return uploadDocToVectorDB(localStorage.token, $page.params.id, file).catch((error) => {
			toast.error(error);
			return null;
		});
	};

	const buildDocument = (doc, content = {}): Partial<IDocuments> => {
		return {
			collection: doc.collection,
			collection_name: doc.collection_name,
			filename: doc.filename,
			name: transformDocumentName(doc.original_filename),
			title: transformFileName(doc.original_filename),
			path: doc.path,
			original_filename: doc.original_filename,
			content: JSON.stringify(content)
		};
	};

	const createDocument = async (vectorResponse: any): Promise<IDocuments | null> => {
		try {
			const saveDocument: Partial<IDocuments> = buildDocument(vectorResponse);
			const document = await documentsApi.createDocument(saveDocument);
			return document;
		} catch (e: any) {
			console.error('Error creating document: ', e);
			toast.error(e.message);
			return null;
		}
	};

	const applyDocs = async () => {
		const docs = await documentsApi.getDocsThroughCollection($page.params.id);
		await documentsApi.addToDocStore(docs);
		documents.set(docs);
	};

	const deleteDoc = async (name) => {
		await deleteDocByName(localStorage.token, name);
		await applyDocs();
	};

	const deleteDocs = async (docs) => {
		await Promise.all(
			docs.map(async (doc) => {
				return await deleteDocByName(localStorage.token, doc.name);
			})
		);
		await applyDocs();
	};

	const unlock = (sendLength: number) => {
		fileCount++;
		uploading = fileCount < sendLength;
		if (uploading) {
			return;
		}
		fileCount = 0;
		toast.success($i18n.t('Documents uploaded successfully'));
	};

	const uploadDoc = (content) => {
		uploading = true;
		const sendContent = content.detail ? content.detail : content || {};
		const sendFile = sendContent.file ? sendContent.file : null;
		const sendLength = sendContent.length ? sendContent.length : 1;
		if (!sendFile) {
			return unlock(sendLength);
		}
		return sendFileToVector(sendFile).then((res) => {
			if (!res) {
				return unlock(sendLength);
			}
			return createDocument(res).then((document) => {
				if (!document) {
					return unlock(sendLength);
				}
				documents.update((docs) => [...docs, document]);
				unlock(sendLength);
				return tick();
			});
		});
	};

	const getCollectionDocuments = async () => {
		documents.set([]);
		await applyDocs();
	};

	const pullCollection = () => {
		return collectionApi.findOne($page.params.id).then((res) => {
			collection = res;
			return res;
		});
	};

	const fileReaderChange = () => {
		console.log(importFiles);
		const reader = new FileReader();
		reader.onload = async (event) => {
			uploading = true;
			const result = event?.target?.result;
			const savedDocs = typeof result === 'string' ? JSON.parse(result) : result;
			console.log(savedDocs);
			for (const doc of savedDocs) {
				const document = await createDocument(doc);
				if (!document) {
					continue;
				}
				documents.update((docs) => [...docs, document]);
				await tick();
			}
			await applyDocs();
			uploading = false;
			toast.success($i18n.t('Documents imported successfully'));
		};

		reader.readAsText(importFiles[0]);
	};

	const filterDocsWithTags = (docs) => {
		if (!docs) {
			return;
		}
		tags = docs.reduce((a, e) => {
			return [...new Set([...a, ...(e?.content?.tags ?? []).map((tag) => tag.name)])];
		}, []);
	};

	onMount(async () => {
		await getCollectionDocuments().then(pullCollection);
		documents.subscribe(filterDocsWithTags);
	});

	let filteredDocs;

	$: filteredDocs = $documents.filter(
		(doc) =>
			(selectedTag === '' ||
				(typeof doc?.content !== 'string' ? doc.content?.tags || [] : [])
					.map((tag) => tag.name)
					.includes(selectedTag)) &&
			(query === '' || doc.name.includes(query))
	);
</script>

<svelte:head>
	<title>{$i18n.t('Documents')} | {$WEBUI_NAME}</title>
</svelte:head>

{#if !uploading}
	<DropZone on:doc={uploadDoc} />
{/if}
{#key selectedDoc}
	<EditDocModal bind:show={showEditDocModal} {selectedDoc} />
{/key}

<AddDocModal bind:show={showAddDocModal} on:doc={uploadDoc} />

<div class="min-h-screen max-h-[100dvh] w-full flex justify-center dark:text-white">
	<div class=" flex flex-col justify-between w-full overflow-y-auto">
		<div class="max-w-2xl mx-auto w-full px-3 md:px-0 my-10">
			<div class="mb-6">
				<div class="flex justify-between items-center">
					<div class=" text-2xl font-semibold self-center">
						<Translate t="{collection ? collection.name : 'My'} Documents" />
					</div>
					<a
						href="/collections"
						class="flex items-center text-xs mt-3 mt-1 dark:text-gray-200 hover:underline transition"
						><SvgIcon icon={IconsTypes.BACK} /> <Translate t="Back to Collections" /></a
					>
				</div>
				<div class=" text-gray-500 text-xs">
					<Translate t="Use '#' in the prompt input to load and select your documents." />
				</div>
			</div>

			<div class=" flex w-full space-x-2">
				<div class="flex flex-1">
					<div class=" self-center ml-1 mr-3">
						<SvgIcon icon={IconsTypes.SEARCH} size={18} />
					</div>
					<input
						class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-none bg-transparent"
						bind:value={query}
						placeholder={$i18n.t('Search Documents')}
					/>
				</div>

				<div>
					<button
						disabled={uploading}
						class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
						on:click={() => {
							showAddDocModal = true;
						}}
					>
						{#if !uploading}
							<SvgIcon icon={IconsTypes.ADD} size={16} />
						{:else}
							<LoaderIcon className="w-4 h-4" />
						{/if}
					</button>
				</div>
			</div>

			<hr class=" dark:border-gray-700 my-2.5" />

			{#if tags.length > 0}
				<div class="px-2.5 pt-1 flex gap-1 flex-wrap">
					<div class="ml-0.5 pr-3 my-auto flex items-center">
						<Checkbox
							state={filteredDocs.filter((doc) => doc?.selected === 'checked').length ===
							filteredDocs.length
								? 'checked'
								: 'unchecked'}
							indeterminate={filteredDocs.filter((doc) => doc?.selected === 'checked').length > 0 &&
								filteredDocs.filter((doc) => doc?.selected === 'checked').length !==
									filteredDocs.length}
							on:change={(e) => {
								if (e.detail === 'checked') {
									filteredDocs = filteredDocs.map((doc) => ({ ...doc, selected: 'checked' }));
								} else if (e.detail === 'unchecked') {
									filteredDocs = filteredDocs.map((doc) => ({ ...doc, selected: 'unchecked' }));
								}
							}}
						/>
					</div>

					{#if filteredDocs.filter((doc) => doc?.selected === 'checked').length === 0}
						<button
							class="px-2 py-0.5 space-x-1 flex h-fit items-center rounded-full transition bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:text-white"
							on:click={async () => {
								selectedTag = '';
							}}
						>
							<div class=" text-xs font-medium self-center line-clamp-1"><Translate t="all" /></div>
						</button>

						{#each tags as tag}
							<button
								class="px-2 py-0.5 space-x-1 flex h-fit items-center rounded-full transition bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:text-white"
								on:click={async () => {
									selectedTag = tag;
								}}
							>
								<div class=" text-xs font-medium self-center line-clamp-1">
									#{tag}
								</div>
							</button>
						{/each}
					{:else}
						<div class="flex-1 flex w-full justify-between items-center">
							<div class="text-xs font-medium py-0.5 self-center mr-1">
								{filteredDocs.filter((doc) => doc?.selected === 'checked').length} Selected
							</div>

							<div class="flex gap-1">
								<button
									class="px-2 py-0.5 space-x-1 flex h-fit items-center rounded-full transition bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:text-white"
									on:click={async () => {
										deleteDocs(filteredDocs.filter((doc) => doc.selected === 'checked'));
									}}
								>
									<div class=" text-xs font-medium self-center line-clamp-1">
										<Translate t="delete" />
									</div>
								</button>
							</div>
						</div>
					{/if}
				</div>
			{/if}

			<div class="my-3 mb-5">
				{#each filteredDocs as doc}
					<button
						class=" flex space-x-4 cursor-pointer text-left w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
						on:click={() => {
							if (doc?.selected === 'checked') {
								doc.selected = 'unchecked';
							} else {
								doc.selected = 'checked';
							}
						}}
					>
						<div class="my-auto flex items-center">
							<Checkbox state={doc?.selected ?? 'unchecked'} />
						</div>
						<div class=" flex flex-1 space-x-4 cursor-pointer w-full">
							<div class=" flex items-center space-x-3">
								<DocumentIcon {doc} />
								<div class=" self-center flex-1">
									<div class=" font-bold line-clamp-1">#{doc.name} ({doc.filename})</div>
									<div class=" text-xs overflow-hidden text-ellipsis line-clamp-1">
										{doc.title}
									</div>
								</div>
							</div>
						</div>
						<div class="flex flex-row space-x-1 self-center">
							<button
								class="self-center w-fit text-sm z-20 px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
								type="button"
								on:click={async (e) => {
									e.stopPropagation();
									showEditDocModal = !showEditDocModal;
									selectedDoc = doc;
								}}
							>
								<SvgIcon icon={IconsTypes.PENCIL} size={24} />
							</button>

							<button
								class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
								type="button"
								on:click={(e) => {
									e.stopPropagation();

									deleteDoc(doc.name);
								}}
							>
								<SvgIcon icon={IconsTypes.TRASH} size={24} />
							</button>
						</div>
					</button>
				{/each}
			</div>

			<div class=" flex justify-end w-full mb-2">
				<div class="flex space-x-2">
					<input
						id="documents-import-input"
						bind:this={documentsImportInputElement}
						bind:files={importFiles}
						type="file"
						accept=".json"
						hidden
						on:change={fileReaderChange}
					/>

					<button
						class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
						disabled={uploading}
						on:click={() => {
							documentsImportInputElement.click();
						}}
					>
						<div class=" self-center mr-2 font-medium">
							<Translate t="Import Documents Mapping" />
						</div>
						<div class=" self-center">
							<SvgIcon icon={IconsTypes.UPLOAD} size={16} />
						</div>
					</button>

					<button
						class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
						disabled={uploading}
						on:click={async () => {
							let blob = new Blob([JSON.stringify($documents)], {
								type: 'application/json'
							});
							saveAs(blob, `documents-mapping-export-${Date.now()}.json`);
						}}
					>
						<div class=" self-center mr-2 font-medium">
							<Translate t="Export Documents Mapping" />
						</div>

						<div class=" self-center">
							<SvgIcon icon={IconsTypes.DOWNLOAD} size={16} />
						</div>
					</button>
				</div>
			</div>
		</div>
	</div>
</div>
