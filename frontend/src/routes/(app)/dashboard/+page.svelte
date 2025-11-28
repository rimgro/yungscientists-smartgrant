<script lang="ts">
import { onMount } from 'svelte';
import { Button, Card, SectionHeader } from '$lib/components';
import StageTracker from '$lib/features/grants/StageTracker.svelte';
import WalletConnect from '$lib/features/payments/WalletConnect.svelte';
import TransactionHistory from '$lib/features/payments/TransactionHistory.svelte';
import ContractStatus from '$lib/features/payments/ContractStatus.svelte';
import { api } from '$lib/api';
import type { GrantProgram } from '$lib/types';

let { data } = $props();
const { session } = data;

let grants: GrantProgram[] = $state([]);
let loading = $state(true);
let error = $state('');
const walletId = $derived(grants[0]?.bank_account_number ?? 'MIR-ACCOUNT');

onMount(async () => {
	try {
		grants = await api.get<GrantProgram[]>('/grants');
	} catch (err) {
		error = err instanceof Error ? err.message : 'Unable to load grants';
	} finally {
		loading = false;
	}
});

const txns = [
	{ id: 't1', type: 'Disbursement', amount: 5000, reference: 'SG-001-1', timestamp: '2024-11-02 13:00' },
	{ id: 't2', type: 'Escrow', amount: 8000, reference: 'SG-001-2', timestamp: '2024-11-15 09:12' }
];
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Dashboard</p>
			<h1 class="text-3xl font-semibold text-slate-50">Overview</h1>
			<p class="text-sm text-slate-400">
				Bank ID: {session.user.bank_id ?? '—'} · Grants linked to MIR payouts
			</p>
		</div>
		<Button class="btn-primary" onclick={() => (window.location.href = '/grants/new')}>Create grant</Button>
	</div>

	<div class="grid gap-4 lg:grid-cols-3">
		<Card title="Active Grants" description="Synced with MIR identifiers">
			<div class="text-4xl font-semibold text-slate-50">{loading ? '…' : grants.length}</div>
			<p class="text-sm text-slate-400">Participants and statuses pulled from the API.</p>
		</Card>
		<Card title="Pending approvals" description="Stages awaiting review">
			<div class="text-4xl font-semibold text-amber-200">
				{loading
					? '…'
					: grants
							.flatMap((g) => g.stages)
							.filter((s) => s.completion_status === 'active' || s.completion_status === 'pending').length}
			</div>
			<p class="text-sm text-slate-400">Complete requirements to release payouts.</p>
		</Card>
		<Card title="Disbursed" description="Total paid out via MIR">
			<div class="text-4xl font-semibold text-emerald-200">$5,000</div>
			<p class="text-sm text-slate-400">Remaining escrow: $8,000</p>
		</Card>
	</div>

	<div class="grid gap-4 lg:grid-cols-3">
		<div class="lg:col-span-2 space-y-4">
			<SectionHeader
				eyebrow="Grant"
				title={loading ? 'Loading...' : grants[0]?.name ?? 'No grants yet'}
				kicker={loading ? '' : `Bank account: ${grants[0]?.bank_account_number ?? '—'}`}
			/>
			{#if error}
				<p class="rounded-lg border border-amber-400/50 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
					{error}
				</p>
			{:else}
				<StageTracker stages={grants[0]?.stages ?? []} />
			{/if}
		</div>
		<div class="space-y-4">
			<ContractStatus state="Awaiting Oracle" stub />
			<WalletConnect connected={false} walletId={walletId} stub />
			<TransactionHistory items={txns} stub />
		</div>
	</div>
</div>
