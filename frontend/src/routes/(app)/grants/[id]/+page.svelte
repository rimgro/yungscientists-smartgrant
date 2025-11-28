<script lang="ts">
	import { onMount } from 'svelte';
	import { Button, Card } from '$lib/components';
	import StageTracker from '$lib/features/grants/StageTracker.svelte';
	import RequirementUpload from '$lib/features/grants/RequirementUpload.svelte';
	import { api } from '$lib/api';
	import { pushToast } from '$lib/stores/notifications';
	import type { GrantParticipantRole, GrantProgram } from '$lib/types';

	let { params } = $props();
	let grant: GrantProgram | null = $state(null);
	let loading = $state(true);
	let error = $state('');
	let inviteUserId = $state('');
	let inviteRole: GrantParticipantRole = $state('grantee');
	let inviteBusy = $state(false);

	const loadGrant = async () => {
		loading = true;
		error = '';
		try {
			const programs = await api.get<GrantProgram[]>('/grants');
			grant = programs.find((g) => g.id === params.id) ?? null;
			if (!grant) {
				error = 'Grant not found';
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to load grant';
		} finally {
			loading = false;
		}
	};

	onMount(loadGrant);

	const handleUpload = (file: File) => {
		console.log('Upload file for requirement', file.name);
	};

	const completeRequirement = async (requirementId: string) => {
		try {
			await api.post(`/grants/requirements/${requirementId}/complete`);
			pushToast({ title: 'Requirement marked complete', tone: 'success', timeout: 2000 });
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to complete requirement';
			pushToast({ title: 'Action failed', message, tone: 'error', timeout: 3500 });
		}
	};

	const completeStage = async (stageId: string) => {
		try {
			await api.post(`/grants/stages/${stageId}/complete`);
			pushToast({ title: 'Stage completed', tone: 'success', timeout: 2000 });
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to complete stage';
			pushToast({ title: 'Action failed', message, tone: 'error', timeout: 3500 });
		}
	};

	const triggerContract = async () => {
		if (!grant) return;
		try {
			await api.post(`/contracts/${grant.id}/execute`);
			pushToast({ title: 'Contract executed', tone: 'success', timeout: 2000 });
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to execute contract';
			pushToast({ title: 'Contract call failed', message, tone: 'error', timeout: 3500 });
		}
	};

	const inviteParticipant = async () => {
		if (!grant) return;
		if (!inviteUserId.trim()) {
			pushToast({ title: 'Missing user', message: 'Введите user_id участника', tone: 'error', timeout: 2500 });
			return;
		}
		inviteBusy = true;
		try {
			await api.post(`/grants/${grant.id}/invite`, { user_id: inviteUserId, role: inviteRole });
			pushToast({ title: 'Приглашение отправлено', tone: 'success', timeout: 2000 });
			inviteUserId = '';
			inviteRole = 'grantee';
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Не удалось пригласить';
			pushToast({ title: 'Ошибка приглашения', message, tone: 'error', timeout: 3500 });
		} finally {
			inviteBusy = false;
		}
	};
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Grant</p>
			<h1 class="text-3xl font-semibold text-slate-50">{grant?.name ?? 'Loading...'}</h1>
			<p class="text-sm text-slate-400">
				Bank account: {grant?.bank_account_number ?? '—'} · Status: {grant?.status ?? 'loading'}
			</p>
		</div>
		<Button variant="ghost" size="sm" onclick={() => history.back()}>Back</Button>
	</div>

	{#if error}
		<p class="rounded-lg border border-amber-400/50 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
			{error}
		</p>
	{:else if loading}
		<Card title="Loading grant" description="Fetching data from API..." />
	{:else if grant}
		<div class="grid gap-4 lg:grid-cols-3">
			<div class="lg:col-span-2 space-y-4">
				<StageTracker stages={grant.stages} />
				<Card title="Stages and requirements">
					<ul class="space-y-3 text-sm text-slate-200">
						{#each grant.stages as stage}
							<li class="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
								<div class="flex items-center justify-between">
									<div>
										<p class="font-semibold text-slate-100">
											Stage {stage.order} · ${stage.amount.toLocaleString()}
										</p>
										<p class="text-xs text-slate-400">Status: {stage.completion_status}</p>
									</div>
									{#if stage.completion_status === 'active'}
										<Button size="sm" variant="ghost" onclick={() => completeStage(stage.id)}>
											Mark stage complete
										</Button>
									{/if}
								</div>
								{#if stage.requirements.length}
									<ul class="mt-3 space-y-2">
										{#each stage.requirements as req}
											<li class="flex items-start justify-between gap-3 rounded-lg bg-white/5 px-3 py-2">
												<div>
													<p class="font-semibold">{req.name}</p>
													<p class="text-xs text-slate-400">{req.description ?? '—'}</p>
													<p class="text-[11px] text-slate-500">Status: {req.status}</p>
												</div>
												{#if req.status !== 'completed' && stage.completion_status === 'active'}
													<Button size="xs" variant="ghost" onclick={() => completeRequirement(req.id)}>
														Complete
													</Button>
												{/if}
											</li>
										{/each}
									</ul>
								{:else}
									<p class="text-xs text-slate-400">No requirements added.</p>
								{/if}
							</li>
						{/each}
					</ul>
				</Card>
			</div>
			<div class="space-y-4">
				<Card title="Submit requirement">
					<RequirementUpload requirementName="Upload proof" onUpload={handleUpload} />
				</Card>
				<Card title="Contract action" description="Call backend stub to exercise grant contract.">
					<Button class="w-full" onclick={triggerContract}>Execute contract</Button>
				</Card>
				<Card title="Invite participant" description="Добавить grantee или supervisor в грант.">
					<div class="space-y-3 text-sm text-slate-200">
						<label class="space-y-1">
							<span class="font-semibold">User ID</span>
							<input
								class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand"
								placeholder="UUID пользователя"
								bind:value={inviteUserId}
							/>
						</label>
						<label class="space-y-1">
							<span class="font-semibold">Role</span>
							<select
								class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand"
								bind:value={inviteRole}
							>
								<option value="grantee">grantee</option>
								<option value="supervisor">supervisor</option>
							</select>
						</label>
						<Button class="w-full" disabled={inviteBusy} onclick={inviteParticipant}>
							{inviteBusy ? 'Отправка…' : 'Пригласить'}
						</Button>
					</div>
				</Card>
			</div>
		</div>
	{/if}
</div>
