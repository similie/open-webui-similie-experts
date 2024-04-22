<script lang="ts">
	import type { RAGResponse } from '$lib/apis/documents';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import SvgIcon from '$lib/components/svg/SvgIcon.svelte';
	import { IconsTypes } from '$lib/components/svg/icon-types';
	import RagResponseModal from './modals/RagResponseModal.svelte';
	export let documents: RAGResponse[] = [];
	export let isLastMessage = true;
	let showModal = false;
	const toggleModal = () => {
		showModal = !showModal;
	};

	// $: console.log(documents);
</script>

<RagResponseModal show={showModal} {documents} />

<div class=" {isLastMessage ? 'visible' : 'invisible group-hover:visible'} p-1">
	<Tooltip content="Document Retrieval Details" placement="bottom">
		<button on:click={toggleModal}>
			<SvgIcon icon={IconsTypes.DOCUMENT} />
		</button>
	</Tooltip>
</div>
