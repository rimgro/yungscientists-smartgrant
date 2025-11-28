<script lang="ts">
	import { Button } from '$lib/components';

	let { connected = false, walletId = 'MIR-XXXX', onConnect = (_event: MouseEvent) => {} } = $props();
</script>

<div class="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg">
	<div>
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Wallet</p>
		<h3 class="text-lg font-semibold text-slate-100">Mir payment rail</h3>
		<p class="text-sm text-slate-400">
			{connected ? `Connected as ${walletId}` : 'Link your MIR wallet to release payouts.'}
		</p>
	</div>
	<div class="flex items-center gap-3">
		<span
			class={`h-2 w-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`}
			aria-hidden="true"
		></span>
		<Button onclick={onConnect}>{connected ? 'Reconnect' : 'Connect wallet'}</Button>
	</div>
</div>
