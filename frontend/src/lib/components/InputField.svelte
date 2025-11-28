<script lang="ts">
	type InputType = 'text' | 'email' | 'password' | 'number' | 'tel';

	let {
		id,
		label,
		type = 'text' as InputType,
		placeholder = '',
		value = '',
		required = false,
		error = '',
		helper = ''
	} = $props();
</script>

<label class="space-y-2 text-sm text-slate-200" for={id}>
	<div class="flex items-center justify-between">
		<span class="font-semibold">{label}</span>
		{#if helper}
			<span class="text-xs text-slate-400">{helper}</span>
		{/if}
	</div>

	<input
		id={id}
		class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand focus:ring-2 focus:ring-brand disabled:cursor-not-allowed disabled:opacity-60"
		type={type}
		placeholder={placeholder}
		bind:value
		{required}
		aria-invalid={error ? 'true' : 'false'}
	/>

	{#if error}
		<p class="text-xs font-medium text-rose-300">{error}</p>
	{/if}
</label>
