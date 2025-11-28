<script lang="ts">
	type ContractState = 'Awaiting Oracle' | 'Funded' | 'Disbursed' | 'Paused';
	let { state = 'Awaiting Oracle' as ContractState, label = 'Smart contract status' } = $props();

	const colors: Record<ContractState, string> = {
		'Awaiting Oracle': 'bg-amber-500/20 text-amber-200 border-amber-500/30',
		Funded: 'bg-brand/15 text-brand border-brand/40',
		Disbursed: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
		Paused: 'bg-rose-500/15 text-rose-200 border-rose-500/30'
	};
</script>

<div class="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 shadow-lg">
	<div>
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Contracts</p>
		<h3 class="text-sm font-semibold text-slate-100">{label}</h3>
	</div>
	<span class={`rounded-full border px-4 py-2 text-xs font-semibold ${colors[state]}`}>{state}</span>
</div>
