<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { WEBUI_NAME, collectionsModels } from '$lib/stores';
	import { CollectionApi, type ICollection } from '$lib/apis/collections';
	import AddCollectionModal from '$lib/components/collections/AddCollectionModal.svelte';
	import CollectionListItem from '$lib/components/collections/CollectionListItem.svelte';
	import Page from '$lib/components/layout/page-elements/pages/Page.svelte';
	import SvgIcon from '$lib/components/svg/SvgIcon.svelte';
	import { IconsTypes } from '$lib/components/svg/icon-types';
	import RoundedButton from '$lib/components/layout/page-elements/buttons/RoundedButton.svelte';
	import Translate from '$lib/components/common/Translate.svelte';
	import SettingsModal from '$lib/components/documents/SettingsModal.svelte';
	const i18n = getContext('i18n');
	let showCreationModal = false;
	let showSettingsModal = false;
	const collectionApi = new CollectionApi();
	const pageName = 'Collections' || WEBUI_NAME;
	const defaultCollection: ICollection = {
		name: '',
		title: '',
		content: '',
		key: '',
		timestamp: '',
		user_id: ''
	};

	const clearCollection = () => {
		for (const key in defaultCollection) {
			defaultCollection[key] = '';
		}
	};

	const pullCollection = () => {
		return collectionApi.find().then(collectionsModels.set);
	};

	const showModal = () => {
		showCreationModal = !showCreationModal;
	};

	const showSettings = () => {
		showSettingsModal = !showSettingsModal;
	};

	const handleMessage = (e) => {
		if (!e.detail) {
			return;
		}
		clearCollection();
		pullCollection();
	};

	onMount(() => {
		pullCollection();
	});
</script>

<svelte:head>
	<title>{$i18n.t(pageName)}</title>
</svelte:head>

<SettingsModal bind:show={showSettingsModal} />

<AddCollectionModal
	bind:show={showCreationModal}
	collection={defaultCollection}
	on:collection={handleMessage}
/>

<Page pageTitle="My Collections">
	<div class="flex gap-2" slot="heading">
		<RoundedButton onClick={showSettings}>
			<SvgIcon icon={IconsTypes.GEAR} size={16} className="w-4 h-4" />
			<div class=" text-xs"><Translate t="Document Settings" /></div>
		</RoundedButton>
		<RoundedButton onClick={showModal}>
			<SvgIcon icon={IconsTypes.ADD} size={16} className="w-4 h-4" />
			<div class=" text-xs"><Translate t="Create Collection" /></div>
		</RoundedButton>
	</div>

	<div slot="body" class="flex flex-wrap">
		{#each $collectionsModels as collection}
			<CollectionListItem {collection} on:collection={pullCollection} />
		{/each}
	</div></Page
>
