<script lang="ts">
	import { toast } from 'svelte-sonner';
	import Modal from '../common/Modal.svelte';

	import { CollectionApi, type ICollection } from '$lib/apis/collections';
	import Translate from '../common/Translate.svelte';
	import SvgIcon from '../svg/SvgIcon.svelte';
	import { IconsTypes } from '../svg/icon-types';
	import { createEventDispatcher } from 'svelte';

	export let show = false;

	const collectionApi = new CollectionApi();
	const dispatch = createEventDispatcher();
	let disabled = false;

	export let collection: ICollection;

	const sendToServer = () => {
		return collection.key
			? collectionApi.update(collection.key, collection)
			: collectionApi.create(collection);
	};

	const clearContent = (collection: ICollection | null) => {
		dispatch('collection', collection);
		show = false;
		disabled = false;
	};

	const submitHandler = () => {
		disabled = true;
		sendToServer().then((collection: ICollection) => {
			toast.success('Collection saved');
			clearContent(collection);
		});
	};

	const deleteHandler = () => {
		collectionApi.delete(collection.key).then(() => {
			clearContent(null);
		});
	};
</script>

<Modal size="sm" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 py-4">
			<div class=" text-lg font-medium self-center">
				<Translate t="{collection?.key ? 'Update' : 'Create'} Collection" />
			</div>

			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<SvgIcon icon={IconsTypes.CLOSE} className="w-5 h-5" />
			</button>
		</div>
		<hr class=" dark:border-gray-800" />

		<div class="flex flex-col md:flex-row w-full px-5 py-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class="mb-3 w-full flex flex-row">
						<div class="flex-grow">
							<div class="text-sm font-semibold mb-2"><Translate t="Name" />*</div>
							<input
								id="collection-name-input"
								bind:value={collection.name}
								{disabled}
								required
								type="text"
								maxlength="20"
								class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
							/>
						</div>
					</div>

					<div class=" flex flex-col space-y-1.5">
						<div class="flex flex-col w-full">
							<div class="text-sm font-semibold mb-2"><Translate t="Description" /></div>
							<textarea
								class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
								id="collection-conte-input"
								bind:value={collection.content}
								{disabled}
							/>
						</div>
					</div>

					<div class="flex pt-5 text-sm font-medium">
						{#if collection.key}
							<button
								class=" px-4 py-2 bg-red-600 hover:bg-red-700 text-gray-100 transition rounded"
								type="button"
								on:click={deleteHandler}
							>
								<Translate t="Delete" />
							</button>
						{/if}

						<button
							class=" px-4 py-2 ml-auto bg-emerald-600 hover:bg-emerald-700 text-gray-100 transition rounded"
							type="submit"
							disabled={disabled || !collection.name}
						>
							<Translate t={collection.key ? 'Save' : 'Create'} />
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>
