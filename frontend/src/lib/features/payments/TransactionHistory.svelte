<script lang="ts">
	type Txn = {
		id: string;
		type: string;
		amount: number;
		reference: string;
		timestamp: string;
	};

	let { items = [] as Txn[] } = $props();
</script>

<div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg">
	<div class="mb-4 flex items-center justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Payments</p>
			<h3 class="text-lg font-semibold text-slate-100">Transaction history</h3>
		</div>
		<span class="text-xs text-slate-400">Source: MIR ledger</span>
	</div>
	<div class="overflow-x-auto">
		<table class="w-full text-left text-sm">
			<thead class="text-xs uppercase text-slate-400">
				<tr>
					<th class="pb-2">Reference</th>
					<th class="pb-2">Type</th>
					<th class="pb-2">Amount</th>
					<th class="pb-2">Timestamp</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-white/5">
				{#if items.length === 0}
					<tr>
						<td class="py-3 text-slate-500" colspan="4">No transactions yet.</td>
					</tr>
				{:else}
					{#each items as txn}
						<tr>
							<td class="py-3 font-semibold text-slate-100">{txn.reference}</td>
							<td class="py-3 text-slate-300">{txn.type}</td>
							<td class="py-3 text-emerald-300">${txn.amount.toLocaleString()}</td>
							<td class="py-3 text-slate-400">{txn.timestamp}</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</div>
