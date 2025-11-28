<script lang="ts">
	import { goto } from '$app/navigation';
	import GrantCreationWizard, { type StageDraft } from '$lib/features/grants/GrantCreationWizard.svelte';
	import { pushToast } from '$lib/stores/notifications';
	import { api } from '$lib/api';
	import type { GrantProgram } from '$lib/types';

	let name = '';
	let bankAccount = '';
	let busy = false;
	let wizardStages: StageDraft[] = [];

	const handleSubmit = async (event: CustomEvent<StageDraft[]>) => {
		if (!name.trim() || !bankAccount.trim()) {
			pushToast({ title: 'Missing fields', message: 'Add a name and bank account', tone: 'error', timeout: 2500 });
			return;
		}
		busy = true;
		wizardStages = event.detail;
		try {
			const payload = {
				name,
				bank_account_number: bankAccount,
				stages: wizardStages.map((stage, index) => ({
					order: index + 1,
					amount: stage.amount,
					requirements: [
						{
							name: stage.requirement,
							description: stage.description || ''
						}
					]
				})),
				participants: []
			};
			const grant = await api.post<GrantProgram>('/grants', payload);
			pushToast({ title: 'Grant created', message: 'Draft saved with backend', tone: 'success', timeout: 2500 });
			await goto(`/grants/${grant.id}`);
		} catch (error) {
			const message = error instanceof Error ? error.message : 'Unable to create grant';
			pushToast({ title: 'Save failed', message, tone: 'error', timeout: 3500 });
		} finally {
			busy = false;
		}
	};
</script>

<div class="space-y-6">
	<div>
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Grants</p>
		<h1 class="text-3xl font-semibold text-slate-50">Create new grant</h1>
		<p class="text-sm text-slate-400">
			Define milestones, requirement uploads, and payout amounts before syncing to MIR.
		</p>
	</div>

	<div class="grid gap-4 lg:grid-cols-3">
		<div class="space-y-4 lg:col-span-1">
			<label class="space-y-2 text-sm text-slate-200">
				<span class="font-semibold">Program name</span>
				<input
					class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand"
					placeholder="STEM Fellowship 2025"
					bind:value={name}
					required
				/>
			</label>
			<label class="space-y-2 text-sm text-slate-200">
				<span class="font-semibold">Bank account number</span>
				<input
					class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand"
					placeholder="MIR-ACCOUNT-001"
					bind:value={bankAccount}
					required
				/>
			</label>
			{#if busy}
				<p class="text-xs text-slate-400">Saving...</p>
			{/if}
		</div>

		<div class="lg:col-span-2">
			<GrantCreationWizard on:submit={handleSubmit} />
		</div>
	</div>
</div>
