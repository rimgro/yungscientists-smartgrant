<script lang="ts">
	let { eyebrow = '', title = '', kicker = '' } = $props();
</script>

<div class="mb-6 flex flex-col gap-2">
	{#if eyebrow}
		<span class="text-xs font-semibold uppercase tracking-[0.28em] text-brand">{eyebrow}</span>
	{/if}
	{#if title}
		<h2 class="text-2xl font-semibold text-slate-100 sm:text-3xl">{title}</h2>
	{/if}
	{#if kicker}
		<p class="max-w-2xl text-sm text-slate-400">{kicker}</p>
	{/if}
</div>
