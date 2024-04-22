<script lang="ts">
	import { getContext } from 'svelte';
	export let t: string = '';
	const i18n = getContext('i18n');
</script>

<span>{$i18n.t(t)}</span>
