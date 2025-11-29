<script lang="ts">
import { onMount } from 'svelte';
import { Button, Card } from '$lib/components';
import StageTracker from '$lib/features/grants/StageTracker.svelte';
import { api, ApiError } from '$lib/api';
import { canManageMilestones, getUserRolesForGrant } from '$lib/features/grants/permissions';
import { pushToast } from '$lib/stores/notifications';
import { getSession } from '$lib/stores/auth';
import type { GrantParticipantRole, GrantProgram, PaymentContract, PaymentRuleCheck, PaymentTransaction } from '$lib/types';

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
let contracts: PaymentContract[] = $state([]);
let contractsLoading = $state(false);
let contractError = $state('');
let selectedContractId = $state('');
let purchaseCard = $state('1234567812345678');
let purchaseMcc = $state('5411');
let purchaseMerchant = $state('demo_merchant');
let purchaseAmount = $state(100);
let contractCheck: PaymentRuleCheck | null = $state(null);
let contractTxn: PaymentTransaction | null = $state(null);
let contractBusy = $state(false);
let stagePaymentOpen = $state(false);
let stagePaymentStageId = $state<string | null>(null);
let stageContractId: string | null = $state(null);
let stagePaymentBusy = $state(false);
let stagePaymentResult: PaymentTransaction | null = $state(null);
let stagePaymentError = $state('');
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
			await loadContracts();
			if (stagePaymentStageId) {
				setStageContract(stagePaymentStageId);
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unable to load grant';
		} finally {
			loading = false;
		}
	};

	onMount(loadGrant);

	const loadContracts = async () => {
		if (!purchaseCard) return;
		contractsLoading = true;
		contractError = '';
		try {
			const response = await api.get<{ contracts: PaymentContract[] }>(
				`/payment-middleware/cards/${purchaseCard}/contracts`
			);
			contracts = response.contracts;
			if (contracts.length && !selectedContractId) {
				selectedContractId = contracts[0].contract_id;
			}
		} catch (err) {
			contractError = err instanceof Error ? err.message : 'Unable to load contracts';
		} finally {
			contractsLoading = false;
		}
	};

	const getStageContractId = (stageId: string): string | null => {
		if (!grant) return null;
		const stage = grant.stages.find((s) => s.id === stageId);
		if (!stage) return null;
		const tokenReq = stage.requirements.find((req) => req.description?.startsWith('payment_contract_id:'));
		if (tokenReq?.description) {
			const [, id] = tokenReq.description.split(':');
			return id ?? null;
		}
		return null;
	};

	const openStagePayment = (stageId: string, amount: number) => {
		stagePaymentStageId = stageId;
		purchaseAmount = amount;
		stagePaymentResult = null;
		stagePaymentError = '';
		stagePaymentOpen = true;
		setStageContract(stageId);
		loadContracts();
	};

	const closeStagePayment = () => {
		stagePaymentOpen = false;
		stagePaymentStageId = null;
	};

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

	const isContractStage = (stage: GrantProgram['stages'][number]) =>
		stage.requirements.some((req) => req.description?.startsWith('payment_contract_id:'));

	const setStageContract = (stageId: string) => {
		const contractId = getStageContractId(stageId);
		stageContractId = contractId;
		if (contractId) {
			selectedContractId = contractId;
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

	const executeContract = async (mode: 'dry' | 'process') => {
		if (!selectedContractId) {
			pushToast({ title: 'Select a contract', message: 'Choose a contract to run checks.', tone: 'error' });
			return;
		}
		contractBusy = true;
		contractCheck = null;
		contractTxn = null;
		const purchaseInfo = {
			mcc: purchaseMcc,
			cost: purchaseAmount,
			merchant_id: purchaseMerchant,
			card_number: purchaseCard
		};
		try {
			if (mode === 'dry') {
				contractCheck = await api.post<PaymentRuleCheck>('/payment-middleware/contracts/execute', {
					contract_id: selectedContractId,
					purchase_info: purchaseInfo
				});
			} else {
				contractTxn = await api.post<PaymentTransaction>(
					`/payment-middleware/process-purchase-with-contract?contract_id=${selectedContractId}`,
					purchaseInfo
				);
				pushToast({ title: 'Purchase processed', tone: 'success', timeout: 2500 });
			}
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Contract call failed';
			pushToast({ title: 'Contract error', message, tone: 'error', timeout: 3500 });
		} finally {
			contractBusy = false;
		}
	};

	const payStageViaMiddleware = async () => {
		if (!stagePaymentStageId) return;
		if (!stageContractId) {
			stagePaymentError = 'No contract linked to this stage.';
			return;
		}
		const stage = grant?.stages.find((s) => s.id === stagePaymentStageId);
		if (!stage || stage.completion_status !== 'active') {
			stagePaymentError = 'Stage must be active to run the contract.';
			return;
		}
		if (stagePaymentResult) {
			stagePaymentError = 'Contract already executed for this stage.';
			return;
		}
		stagePaymentBusy = true;
		stagePaymentError = '';
		stagePaymentResult = null;
		const purchaseInfo = {
			mcc: purchaseMcc,
			cost: purchaseAmount,
			merchant_id: purchaseMerchant,
			card_number: purchaseCard
		};
		try {
			selectedContractId = stageContractId;
			const endpoint = `/payment-middleware/process-purchase-with-contract?contract_id=${stageContractId}`;
			stagePaymentResult = await api.post<PaymentTransaction>(endpoint, purchaseInfo);
			pushToast({
				title: 'Stage payment sent',
				message: `Transaction ${stagePaymentResult.transaction_id} recorded.`,
				tone: 'success',
				timeout: 3000
			});
			try {
				await completeStage(stagePaymentStageId);
			} catch {
				// Swallow errors; completeStage already surfaces toasts.
			}
		} catch (err) {
			stagePaymentError = err instanceof Error ? err.message : 'Failed to process stage payment';
		} finally {
			stagePaymentBusy = false;
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
									<div class="flex items-center gap-2">
										{#if stage.completion_status === 'active' && canManage && !isContractStage(stage)}
											<Button size="sm" variant="ghost" onclick={() => completeStage(stage.id)}>
												Mark stage complete
											</Button>
										{/if}
										{#if stage.completion_status === 'active' && isGrantee && isContractStage(stage)}
											<Button size="sm" onclick={() => openStagePayment(stage.id, stage.amount)}>
												Pay via middleware
											</Button>
										{/if}
									</div>
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
												{#if req.description?.startsWith('payment_contract_id:')}
													<p class="text-xs text-emerald-200">Smart contract enforced — manual proof disabled.</p>
												{:else if req.status !== 'completed' && stage.completion_status === 'active' && canManage}
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
				<Card
					title="Payment middleware"
					description="Execute contract rules before a payout. Only grantees can run payments."
				>
					<div class="space-y-3 text-sm text-slate-200">
						{#if stageContractId}
							<p class="text-xs text-emerald-200">This stage uses contract {stageContractId}.</p>
						{:else}
							<p class="text-xs text-amber-200">No contract linked to this stage.</p>
						{/if}
						<div class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300">
							<p class="font-semibold text-slate-100">Card</p>
							<p>
								This is the card number used to charge the purchase. Contracts apply only if this card is
								listed in "Applicable cards".
							</p>
						</div>
						<div class="grid gap-3 md:grid-cols-2">
							<label class="space-y-1">
								<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Card</span>
								<input
									class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
									value={purchaseCard}
									oninput={(e) => {
										purchaseCard = e.currentTarget.value;
									}}
									onchange={loadContracts}
								/>
							</label>
							<label class="space-y-1">
								<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Contract</span>
								<select
									class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand disabled:opacity-60"
									disabled={true}
									value={stageContractId ?? selectedContractId}
								>
									{#if stageContractId}
										<option value={stageContractId}>{stageContractId}</option>
									{:else if contracts.length === 0}
										<option value="">No contracts</option>
									{:else}
										{#each contracts as contract}
											<option value={contract.contract_id}>{contract.name} ({contract.contract_type})</option>
										{/each}
									{/if}
								</select>
							</label>
						</div>
						<div class="grid gap-3 md:grid-cols-3">
							<label class="space-y-1">
								<span class="text-xs uppercase tracking-[0.2em] text-slate-400">MCC</span>
								<input
									class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
									value={purchaseMcc}
									oninput={(e) => (purchaseMcc = e.currentTarget.value)}
								/>
							</label>
							<label class="space-y-1">
								<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Merchant</span>
								<input
									class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
									value={purchaseMerchant}
									oninput={(e) => (purchaseMerchant = e.currentTarget.value)}
								/>
							</label>
							<label class="space-y-1">
								<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Amount</span>
								<input
									type="number"
									min="1"
									step="1"
									class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
									value={purchaseAmount}
									oninput={(e) => (purchaseAmount = Number(e.currentTarget.value))}
								/>
							</label>
						</div>
						{#if contractError}
							<p class="rounded-lg border border-amber-400/50 bg-amber-500/10 px-3 py-2 text-xs text-amber-100">
								{contractError}
							</p>
						{/if}
						<div class="flex flex-wrap items-center gap-2">
							<Button size="sm" onclick={() => executeContract('dry')} disabled={contractBusy || !selectedContractId}>
								{contractBusy ? 'Running…' : 'Dry-run contract'}
							</Button>
							<Button
								size="sm"
								variant="ghost"
								onclick={() => executeContract('process')}
								disabled={contractBusy || !selectedContractId}
								title="Process purchase with contract enforcement"
							>
								{contractBusy ? 'Processing…' : 'Process with contract'}
							</Button>
							<Button size="sm" variant="ghost" onclick={loadContracts} disabled={contractsLoading}>
								{contractsLoading ? 'Refreshing…' : 'Refresh contracts'}
							</Button>
						</div>
						{#if contractCheck}
							<div class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs">
								<p class={contractCheck.allowed ? 'text-emerald-200' : 'text-rose-200'}>
									{contractCheck.allowed ? 'Allowed' : 'Blocked'} · {contractCheck.reason ?? 'No reason provided'}
								</p>
								{#if contractCheck.details}
									<p class="text-slate-400">Details: {JSON.stringify(contractCheck.details)}</p>
								{/if}
							</div>
						{/if}
						{#if contractTxn}
							<div class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-emerald-200">
								<p>Transaction {contractTxn.transaction_id} · {contractTxn.status}</p>
								<p class="text-slate-300">Amount: {contractTxn.amount} · Type: {contractTxn.type}</p>
							</div>
						{/if}
					</div>
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

{#if stagePaymentOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
		<div class="w-full max-w-xl rounded-2xl border border-white/10 bg-slate-900 p-6 shadow-2xl">
			<div class="flex items-start justify-between gap-3">
				<div>
					<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Stage payment</p>
					<h3 class="text-lg font-semibold text-slate-50">Verify and pay via middleware</h3>
					<p class="text-sm text-slate-400">Runs purchase validation and contract rules before sending.</p>
				</div>
				<Button variant="ghost" size="sm" onclick={closeStagePayment}>Close</Button>
			</div>
			<div class="mt-4 space-y-3 text-sm text-slate-200">
				<div class="grid gap-3 md:grid-cols-2">
					<label class="space-y-1">
						<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Card</span>
						<input
							class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
							value={purchaseCard}
							oninput={(e) => {
								purchaseCard = e.currentTarget.value;
							}}
							onchange={loadContracts}
						/>
					</label>
					<label class="space-y-1">
						<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Contract</span>
						<select
							class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand disabled:opacity-60"
							disabled={contractsLoading || !contracts.length}
							bind:value={selectedContractId}
						>
							{#if contracts.length === 0}
								<option value="">No contracts</option>
							{:else}
								{#each contracts as contract}
									<option value={contract.contract_id}>{contract.name} ({contract.contract_type})</option>
								{/each}
							{/if}
						</select>
					</label>
				</div>
				<div class="grid gap-3 md:grid-cols-3">
					<label class="space-y-1">
						<span class="text-xs uppercase tracking-[0.2em] text-slate-400">MCC</span>
						<input
							class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
							value={purchaseMcc}
							oninput={(e) => (purchaseMcc = e.currentTarget.value)}
						/>
					</label>
					<label class="space-y-1">
						<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Merchant</span>
						<input
							class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
							value={purchaseMerchant}
							oninput={(e) => (purchaseMerchant = e.currentTarget.value)}
						/>
					</label>
					<label class="space-y-1">
						<span class="text-xs uppercase tracking-[0.2em] text-slate-400">Amount</span>
						<input
							type="number"
							min="1"
							step="1"
							class="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand focus:ring-1 focus:ring-brand"
							value={purchaseAmount}
							oninput={(e) => (purchaseAmount = Number(e.currentTarget.value))}
						/>
					</label>
				</div>
				{#if stagePaymentError}
					<p class="rounded-lg border border-rose-400/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
						{stagePaymentError}
					</p>
				{/if}
				<div class="flex items-center gap-2">
					<Button size="sm" onclick={payStageViaMiddleware} disabled={stagePaymentBusy}>
						{stagePaymentBusy ? 'Processing…' : 'Verify & pay'}
					</Button>
					<Button size="sm" variant="ghost" onclick={closeStagePayment}>Cancel</Button>
					<Button size="sm" variant="ghost" onclick={loadContracts} disabled={contractsLoading}>
						{contractsLoading ? 'Refreshing…' : 'Refresh contracts'}
					</Button>
				</div>
				{#if stagePaymentResult}
					<div class="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-emerald-200">
						<p>Transaction {stagePaymentResult.transaction_id} · {stagePaymentResult.status}</p>
						<p class="text-slate-300">Amount: {stagePaymentResult.amount} · Type: {stagePaymentResult.type}</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
