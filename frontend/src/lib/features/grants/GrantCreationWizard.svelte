<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Button, Card, InputField, SectionHeader } from '$lib/components';
	import type { RequirementDraft, StageDraft } from './types';

	const dispatch = createEventDispatcher<{ submit: StageDraft[] }>();

	let { stages: initialStagesProp = initialStages(), activeStep: initialActiveStep = 0 } = $props();
	let stages = $state(initialStagesProp);
	let activeStep = $state(initialActiveStep);
	let error = $state('');

	function initialStages(): StageDraft[] {
		return [
			{
				amount: 5000,
				requirements: [{ name: 'Upload proposal and budget', description: '' }]
			}
		];
	}

	const addStage = () => {
		stages = [
			...stages,
			{
				amount: 1000,
				requirements: [{ name: 'Describe deliverable', description: '' }]
			}
		];
		activeStep = stages.length - 1;
	};

	const updateStage = (index: number, changes: Partial<StageDraft>) => {
		stages = stages.map((stage: StageDraft, i: number) => (i === index ? { ...stage, ...changes } : stage));
	};

	const updateRequirement = (stageIndex: number, reqIndex: number, changes: Partial<RequirementDraft>) => {
		const next = stages.map((stage: StageDraft, i: number) => {
			if (i !== stageIndex) return stage;
			const reqs = stage.requirements.map((req: RequirementDraft, rIdx: number) =>
				rIdx === reqIndex ? { ...req, ...changes } : req
			);
			return { ...stage, requirements: reqs };
		});
		stages = next;
	};

	const addRequirement = (stageIndex: number) => {
		const next = stages.map((stage: StageDraft, i: number) =>
			i === stageIndex ? { ...stage, requirements: [...stage.requirements, { name: '', description: '' }] } : stage
		);
		stages = next;
	};

	const removeRequirement = (stageIndex: number, reqIndex: number) => {
		const next = stages.map((stage: StageDraft, i: number) => {
			if (i !== stageIndex) return stage;
			const reqs = stage.requirements.filter((_req: RequirementDraft, rIdx: number) => rIdx !== reqIndex);
			return { ...stage, requirements: reqs.length ? reqs : [{ name: '', description: '' }] };
		});
		stages = next;
	};

	const handleSubmit = () => {
		const hasEmpty = stages.some(
			(stage: StageDraft) =>
				!stage.amount ||
				stage.requirements.length === 0 ||
				stage.requirements.some((req: RequirementDraft) => !req.name?.trim())
		);
		if (hasEmpty) {
			error = 'Add an amount and at least one requirement name for each stage.';
			return;
		}
		error = '';
		dispatch('submit', stages);
	};
</script>

<Card title="Grant creation wizard" description="Define milestones, payouts, and required evidence.">
	<SectionHeader
		eyebrow="Stages"
		title="Configure milestones"
		kicker="Set clear requirements up front to make approval smoother for supervisors and grantors."
	/>

	<div class="grid grid-cols-1 gap-4 md:grid-cols-12">
		<div class="md:col-span-4">
			<div class="space-y-2">
				{#each stages as stage, index}
					<button
						type="button"
						class={`flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition ${index === activeStep ? 'border-brand bg-brand/10 text-brand' : 'border-white/10 bg-white/5 text-slate-300 hover:border-brand/40 hover:text-slate-100'}`}
						onclick={() => (activeStep = index)}
					>
						<span class="font-semibold">Stage {index + 1}</span>
						<span class="text-xs text-slate-400">${stage.amount.toLocaleString()}</span>
					</button>
				{/each}
				<Button variant="ghost" size="sm" onclick={addStage}>Add stage</Button>
			</div>
		</div>

		<div class="space-y-4 md:col-span-8">
			{#if stages[activeStep]}
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<InputField
						id="stage-budget"
						label="Budget (USD)"
						type="number"
						placeholder="5000"
						min="0"
						step="100"
						bind:value={stages[activeStep].amount}
						on:change={(event: Event) =>
							updateStage(activeStep, { amount: Number((event.target as HTMLInputElement).value) })}
						required
					/>
					<div class="sm:col-span-2 space-y-3">
						<div class="flex items-center justify-between">
							<p class="text-sm font-semibold text-slate-100">Requirements</p>
							<Button size="sm" variant="ghost" onclick={() => addRequirement(activeStep)}>Add requirement</Button>
						</div>
						{#each stages[activeStep].requirements as req, reqIndex}
							<div class="space-y-2 rounded-xl border border-white/10 bg-white/5 p-3">
								<div class="flex items-center justify-between">
									<span class="text-xs uppercase text-slate-400">Requirement {reqIndex + 1}</span>
									{#if stages[activeStep].requirements.length > 1}
										<button class="text-xs text-rose-300 hover:text-rose-200" type="button" onclick={() => removeRequirement(activeStep, reqIndex)}>
											Remove
										</button>
									{/if}
								</div>
								<textarea
									class="min-h-[80px] w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand focus:ring-2 focus:ring-brand"
									placeholder="What must be done before payout?"
									bind:value={req.name}
									oninput={(event) =>
										updateRequirement(activeStep, reqIndex, { name: (event.target as HTMLTextAreaElement).value })}
								></textarea>
								<textarea
									class="min-h-[60px] w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand focus:ring-2 focus:ring-brand"
									placeholder="Links, acceptance criteria (optional)"
									bind:value={req.description}
									oninput={(event) =>
										updateRequirement(activeStep, reqIndex, {
											description: (event.target as HTMLTextAreaElement).value
										})}
								></textarea>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<div class="flex items-center justify-between">
				{#if error}
					<p class="text-sm font-medium text-rose-300">{error}</p>
				{/if}
				<Button onclick={handleSubmit}>Save wizard</Button>
			</div>
		</div>
	</div>
</Card>
