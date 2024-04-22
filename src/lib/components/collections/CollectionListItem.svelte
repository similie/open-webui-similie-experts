<script lang="ts">
	import type { ICollection } from '$lib/apis/collections';
	import RoundedButton from '$lib/components/layout/page-elements/buttons/RoundedButton.svelte';
	import AddCollectionModal from './AddCollectionModal.svelte';
	import SvgIcon from '../svg/SvgIcon.svelte';
	import { IconsTypes } from '../svg/icon-types';
	import { createEventDispatcher } from 'svelte';
	export let collection: ICollection;
	let showCreationModal = false;
	const editModal = () => {
		showCreationModal = !showCreationModal;
	};
	const dispatch = createEventDispatcher();
	const eventHandler = (e) => {
		if (!e.detail) {
			return dispatch('collection', null);
		}
		collection = e.detail;
	};
</script>

<AddCollectionModal bind:show={showCreationModal} {collection} on:collection={eventHandler} />

<div class="m-1 w-64 h-32">
	<div class="max-w-sm bg-white dark:bg-gray-850 rounded-lg overflow-hidden shadow-md">
		<div class="w-full p-4">
			<div class="flex">
				<div class="text-lg font-semibold mr-2">
					<a href="/collections/{collection.key}">{collection.name}</a>
				</div>
				<div class="ml-auto">
					<RoundedButton onClick={editModal}>
						<SvgIcon size={16} className="w-3 h-3" icon={IconsTypes.GEAR} />
					</RoundedButton>
				</div>
			</div>
			<!-- <div class=" text-xs text-gray-500"><em>{collection.title}</em></div> -->
			<div class="mt-2 text-sm text-gray-500">{collection.content}</div>
		</div>
	</div>
</div>
