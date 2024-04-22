<script lang="ts">
	export let onClick: () => void;
</script>

<button
	class="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition"
	type="button"
	on:click={onClick}
>
	<slot />
</button>
