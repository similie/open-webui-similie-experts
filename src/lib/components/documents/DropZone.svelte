<script lang="ts">
	type FileObject = {
		type: string;
		url: string;
	};
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { SUPPORTED_FILE_TYPE, SUPPORTED_FILE_EXTENSIONS } from '$lib/constants';
	import AddFilesPlaceholder from '$lib/components/AddFilesPlaceholder.svelte';
	import Translate from '../common/Translate.svelte';
	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');
	const dropZone = document.querySelector('body');
	let dragged = false;

	let files: FileObject[] = [];

	const endFailedDrag = () => {
		toast.error($i18n.t(`File not found.`));
		dragged = false;
	};

	onMount(() => {
		const onDragOver = (e) => {
			e.preventDefault();
			dragged = true;
		};

		const onDragLeave = () => {
			dragged = false;
		};

		const onDrop = async (e) => {
			e.preventDefault();
			console.log(e);
			if (e.dataTransfer?.files) {
				let reader = new FileReader();

				reader.onload = (event) => {
					files = [
						...files,
						{
							type: 'image',
							url: `${event?.target?.result}`
						}
					];
				};

				const inputFiles = e.dataTransfer?.files;

				if (inputFiles && inputFiles.length <= 0) {
					return endFailedDrag();
				}
				const length = inputFiles?.length;
				for (let i = 0; i < length; i++) {
					const file = inputFiles[i];
					console.log(file, file.name.split('.').at(-1));
					if (
						SUPPORTED_FILE_TYPE.includes(file['type']) ||
						SUPPORTED_FILE_EXTENSIONS.includes(file.name.split('.').at(-1))
					) {
						dispatch('doc', { file, length, count: i });
					} else {
						toast.error(
							`Unknown File Type '${file['type']}', but accepting and treating as plain text`
						);
						dispatch('doc', { file, length, count: i });
					}
				}
			}

			dragged = false;
		};

		dropZone?.addEventListener('dragover', onDragOver);
		dropZone?.addEventListener('drop', onDrop);
		dropZone?.addEventListener('dragleave', onDragLeave);

		return () => {
			dropZone?.removeEventListener('dragover', onDragOver);
			dropZone?.removeEventListener('drop', onDrop);
			dropZone?.removeEventListener('dragleave', onDragLeave);
		};
	});
</script>

{#if dragged}
	<div
		class="fixed w-full h-full flex z-50 touch-none pointer-events-none"
		id="dropzone"
		role="region"
		aria-label="Drag and Drop Container"
	>
		<div class="absolute rounded-xl w-full h-full backdrop-blur bg-gray-800/40 flex justify-center">
			<div class="m-auto pt-64 flex flex-col justify-center">
				<div class="max-w-md">
					<AddFilesPlaceholder>
						<div class=" mt-2 text-center text-sm dark:text-gray-200 w-full">
							<Translate t="Drop any files here to add to my documents" />
						</div>
					</AddFilesPlaceholder>
				</div>
			</div>
		</div>
	</div>
{/if}
