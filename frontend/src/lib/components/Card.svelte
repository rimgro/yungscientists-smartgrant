<script lang="ts">
	import type { Snippet } from 'svelte';

	const { title = '', description = '', children, action }: {
		title?: string;
		description?: string;
		children?: Snippet;
		action?: Snippet;
	} = $props();
</script>

<section class="card border border-white/5 bg-white/5 p-6 shadow-lg">
	{#if title}
		<div class="mb-2 flex items-center justify-between gap-3">
			<h3 class="text-lg font-semibold text-slate-100">{title}</h3>
			{@render action?.()}
		</div>
	{/if}
	{#if description}
		<p class="mb-4 text-sm text-slate-400">{description}</p>
	{/if}
	<div class="space-y-4">
		{@render children?.()}
	</div>
</section>
