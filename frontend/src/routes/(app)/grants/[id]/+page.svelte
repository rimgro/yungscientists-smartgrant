<script lang="ts">
	import { onMount } from 'svelte';
	import { Button, Card } from '$lib/components';
	import StageTracker from '$lib/features/grants/StageTracker.svelte';
	import { api, ApiError } from '$lib/api';
import { canManageMilestones, getUserRolesForGrant } from '$lib/features/grants/permissions';
import { pushToast } from '$lib/stores/notifications';
import { getSession } from '$lib/stores/auth';
import type { GrantParticipantRole, GrantProgram } from '$lib/types';

let { params } = $props();
let grant: GrantProgram | null = $state(null);
let loading = $state(true);
let error = $state('');
let inviteUserId = $state('');
let inviteRole: GrantParticipantRole = $state('grantee');
let inviteBusy = $state(false);
let removeBusyId = $state<string | null>(null);
const currentUserId = getSession()?.user.id ?? '';
const canManage = $derived(grant && currentUserId ? canManageMilestones(grant, currentUserId) : false);
const isGrantor = $derived(
	grant && currentUserId ? getUserRolesForGrant(grant, currentUserId).includes('grantor') : false
);
	const isGrantee = $derived(
		grant && currentUserId ? getUserRolesForGrant(grant, currentUserId).includes('grantee') : false
	);
	let proofs = $state<Record<string, string>>({});
	let confirmBusy = $state(false);
let roleBusyId = $state<string | null>(null);

	const loadGrant = async () => {
		loading = true;
		error = '';
		try {
			const programs = await api.get<GrantProgram[]>('/grants');
			grant = programs.find((g) => g.id === params.id) ?? null;
			if (grant) {
				proofs = grant.stages.reduce<Record<string, string>>((acc, stage) => {
					for (const req of stage.requirements) {
						acc[req.id] = req.proof_url ?? '';
					}
					return acc;
				}, {});
			}
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

	const completeRequirement = async (requirementId: string) => {
		try {
			await api.post(`/grants/requirements/${requirementId}/complete`);
			pushToast({ title: 'Requirement marked complete', tone: 'success', timeout: 2000 });
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to complete requirement';
			if (err instanceof ApiError && err.status === 403) {
				pushToast({
					title: 'Not allowed',
					message: 'Only grantors or supervisors can complete requirements.',
					tone: 'error',
					timeout: 3500
				});
				return;
			}
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
			if (err instanceof ApiError && err.status === 403) {
				pushToast({
					title: 'Not allowed',
					message: 'Only grantors or supervisors can complete stages.',
					tone: 'error',
					timeout: 3500
				});
				return;
			}
			pushToast({ title: 'Action failed', message, tone: 'error', timeout: 3500 });
		}
	};

	const submitProof = async (requirementId: string) => {
		const proofValue = proofs[requirementId]?.trim() ?? '';
		if (!proofValue) {
			pushToast({ title: 'Missing proof', message: 'Add a link or reference to your evidence.', tone: 'error', timeout: 2500 });
			return;
		}
		try {
			await api.post(`/grants/requirements/${requirementId}/proof`, { proof_url: proofValue });
			pushToast({ title: 'Proof submitted', tone: 'success', timeout: 2000 });
			await loadGrant();
		} catch (err) {
			if (err instanceof ApiError && err.status === 403) {
				pushToast({
					title: 'Not allowed',
					message: 'Only grantees can submit proof for this requirement.',
					tone: 'error',
					timeout: 3500
				});
				return;
			}
			const message = err instanceof Error ? err.message : 'Unable to submit proof';
			pushToast({ title: 'Submit failed', message, tone: 'error', timeout: 3500 });
		}
	};

const inviteParticipant = async () => {
		if (!grant) return;
		if (!inviteUserId.trim()) {
			pushToast({
				title: 'Missing user',
				message: 'Введите email или user_id участника',
				tone: 'error',
				timeout: 2500
			});
			return;
		}
		inviteBusy = true;
		try {
			const body = inviteUserId.includes('@')
				? { user_email: inviteUserId, role: inviteRole }
				: { user_id: inviteUserId, role: inviteRole };
			await api.post(`/grants/${grant.id}/invite`, body);
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

	const removeParticipant = async (participantId: string) => {
		if (!grant) return;
		removeBusyId = participantId;
		try {
			await api.delete(`/grants/${grant.id}/participants/${participantId}`);
			pushToast({ title: 'Participant removed', tone: 'success', timeout: 2000 });
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to remove participant';
			pushToast({ title: 'Error removing', message, tone: 'error', timeout: 3500 });
		} finally {
			removeBusyId = null;
		}
	};

	const changeRole = async (participantId: string, role: 'supervisor' | 'grantee') => {
		if (!grant) return;
		roleBusyId = participantId;
		try {
			await api.patch(`/grants/${grant.id}/participants/${participantId}`, { role });
			pushToast({
				title: 'Role updated',
				message: role === 'supervisor' ? 'Participant promoted to supervisor' : 'Participant demoted to grantee',
				tone: 'success',
				timeout: 2000
			});
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to update role';
			pushToast({ title: 'Role change failed', message, tone: 'error', timeout: 3500 });
		} finally {
			roleBusyId = null;
		}
	};

const confirmGrant = async () => {
		if (!grant) return;
		confirmBusy = true;
		try {
			await api.post(`/grants/${grant.id}/confirm`);
			pushToast({ title: 'Grant confirmed', message: 'Deposit recorded and stage 1 activated', tone: 'success', timeout: 2500 });
			await loadGrant();
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unable to confirm grant';
			pushToast({ title: 'Confirm failed', message, tone: 'error', timeout: 3500 });
		} finally {
			confirmBusy = false;
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
		<div class="flex items-center gap-2">
			{#if grant?.status === 'draft' && isGrantor}
				<Button size="sm" onclick={confirmGrant} disabled={confirmBusy}>
					{confirmBusy ? 'Confirming…' : 'Confirm & deposit'}
				</Button>
			{/if}
			<Button variant="ghost" size="sm" onclick={() => history.back()}>Back</Button>
		</div>
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
					{#if !canManage}
						<p class="mb-3 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300">
							You can view this grant, but only the grantor or supervisors can mark requirements or stages
							as complete.
						</p>
					{/if}
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
									{#if stage.completion_status === 'active' && canManage}
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
													{#if req.proof_url}
														<p class="text-[11px] text-emerald-200">
															Proof: <a class="underline" href={req.proof_url} target="_blank" rel="noreferrer">{req.proof_url}</a>
														</p>
													{:else}
														<p class="text-[11px] text-slate-500">Proof: not submitted</p>
													{/if}
												</div>
												{#if req.status !== 'completed' && stage.completion_status === 'active' && canManage}
													<Button size="sm" variant="ghost" onclick={() => completeRequirement(req.id)}>
														Complete
													</Button>
												{:else if req.status !== 'completed' && stage.completion_status === 'active' && isGrantee}
													<div class="flex flex-1 flex-col gap-2">
														<input
															class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
															placeholder="Link to evidence or storage location"
															bind:value={proofs[req.id]}
														/>
														<div class="flex items-center gap-2">
															<Button size="sm" variant="ghost" onclick={() => submitProof(req.id)}>
																Submit proof
															</Button>
															{#if req.proof_url}
																<span class="text-[11px] text-slate-400">Last submitted proof will be used for approval.</span>
															{/if}
														</div>
													</div>
												{:else if req.status !== 'completed' && stage.completion_status === 'active' && !isGrantee}
													<p class="text-xs text-amber-300">
														Only grantees can submit proof for this requirement.
													</p>
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
				<Card title="Contract action" description="Stub — contract integration not implemented.">
					<p class="text-sm text-slate-300">
						This widget will trigger contract execution once the backend is ready. Nothing to do here yet.
					</p>
				</Card>
				<Card title="Participants" description="Manage who can access this grant.">
					{#if grant}
						<ul class="divide-y divide-white/10 text-sm text-slate-200">
							{#each grant.participants as participant}
								<li class="flex items-center justify-between py-2">
									<div>
										<p class="font-semibold capitalize">{participant.role}</p>
										<p class="text-xs text-slate-400">
											{participant.email ?? participant.user_id}
										</p>
									</div>
									<div class="flex items-center gap-2">
										{#if isGrantor && participant.role === 'grantee'}
											<Button
												size="sm"
												variant="ghost"
												disabled={roleBusyId === participant.id}
												onclick={() => changeRole(participant.id, 'supervisor')}
												title="Promote to supervisor"
											>
												{roleBusyId === participant.id ? 'Promoting…' : 'Promote'}
											</Button>
										{/if}
										{#if isGrantor && participant.role === 'supervisor'}
											<Button
												size="sm"
												variant="ghost"
												disabled={roleBusyId === participant.id}
												onclick={() => changeRole(participant.id, 'grantee')}
												title="Demote to grantee"
											>
												{roleBusyId === participant.id ? 'Demoting…' : 'Demote'}
											</Button>
										{/if}
										{#if isGrantor && participant.role !== 'grantor'}
											<Button
												size="sm"
												variant="ghost"
												disabled={removeBusyId === participant.id}
												onclick={() => removeParticipant(participant.id)}
												title="Remove participant"
											>
												{removeBusyId === participant.id ? 'Removing…' : 'Kick'}
											</Button>
										{/if}
									</div>
								</li>
							{/each}
						</ul>
					{/if}
					{#if isGrantor}
						<div class="mt-4 space-y-3 text-sm text-slate-200">
							<label class="space-y-1">
								<span class="font-semibold">User (email or ID)</span>
								<input
									class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand"
									placeholder="email@domain или UUID"
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
					{/if}
				</Card>
			</div>
		</div>
	{/if}
</div>
