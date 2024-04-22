<script lang="ts">
	import Translate from '../../../common/Translate.svelte';
	export let pageTitle: string = '';
</script>

<div class="min-h-screen max-h-[100dvh] w-full flex justify-center dark:text-white">
	<div class="flex flex-col justify-between w-full overflow-y-auto">
		<div class="max-w-2xl mx-auto w-full px-3 md:px-0 my-10">
			<div class="mb-6">
				<div class="flex justify-between items-center">
					<div class=" text-2xl font-semibold self-center"><Translate t={pageTitle} /></div>
					<slot name="heading" />
				</div>
			</div>

			<hr class=" dark:border-gray-700 my-2.5" />

			<div class="px-2.5 pt-1 flex gap-1 flex-wrap"><slot name="body" /></div>
		</div>
	</div>
</div>
