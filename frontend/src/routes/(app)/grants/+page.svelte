<script lang="ts">
	import { onMount } from 'svelte';
	import { Button, Card } from '$lib/components';
	import { api } from '$lib/api';
	import type { GrantProgram } from '$lib/types';

	let grants: GrantProgram[] = [];
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			grants = await api.get<GrantProgram[]>('/grants');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to load grants';
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Grants</p>
			<h1 class="text-3xl font-semibold text-slate-50">Programs</h1>
		</div>
		<a class="btn-primary" href="/grants/new">New grant</a>
	</div>

	{#if error}
		<p class="rounded-lg border border-amber-400/50 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
			{error}
		</p>
	{:else}
		<div class="grid gap-4 md:grid-cols-2">
			{#if loading}
				<Card title="Loading" description="Fetching grants from API...">
					<p class="text-sm text-slate-400">Please wait.</p>
				</Card>
			{:else if !grants.length}
				<Card title="No grants yet" description="Create one to get started.">
					<Button variant="ghost" size="sm" onclick={() => (window.location.href = '/grants/new')}>
						Create grant
					</Button>
				</Card>
			{:else}
				{#each grants as grant}
					<Card title={grant.name} description={`Bank account: ${grant.bank_account_number}`}>
						<p class="text-sm text-slate-400">
							{grant.stages.length || '0'} stages · Status: {grant.status}
						</p>
						<Button variant="ghost" size="sm" onclick={() => (window.location.href = `/grants/${grant.id}`)}>
							Open
						</Button>
					</Card>
				{/each}
			{/if}
		</div>
	{/if}
</div>
