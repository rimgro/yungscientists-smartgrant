<script lang="ts">
	let { title = '', description = '' } = $props();
</script>

<section class="card border border-white/5 bg-white/5 p-6 shadow-lg">
	{#if title}
		<div class="mb-2 flex items-center justify-between gap-3">
			<h3 class="text-lg font-semibold text-slate-100">{title}</h3>
			<slot name="action" />
		</div>
	{/if}
	{#if description}
		<p class="mb-4 text-sm text-slate-400">{description}</p>
	{/if}
	<div class="space-y-4">
		<slot />
	</div>
</section>
