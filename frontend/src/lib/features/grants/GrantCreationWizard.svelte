<script lang="ts">
import { createEventDispatcher } from 'svelte';
import { Button, Card, InputField, SectionHeader } from '$lib/components';

	export type StageDraft = {
		name: string;
		amount: number;
		due: string;
		requirement: string;
		description?: string;
	};

	const dispatch = createEventDispatcher<{ submit: StageDraft[] }>();

	let { stages: initialStagesProp = initialStages(), activeStep: initialActiveStep = 0 } = $props();
	let stages = $state(initialStagesProp);
	let activeStep = $state(initialActiveStep);
	let error = $state('');

	function initialStages(): StageDraft[] {
		return [
			{
				name: 'Milestone 1',
				amount: 5000,
				due: new Date().toISOString().slice(0, 10),
				requirement: 'Upload proposal and budget',
				description: ''
			}
		];
	}

	const addStage = () => {
		stages = [
			...stages,
			{
				name: `Milestone ${stages.length + 1}`,
				amount: 1000,
				due: new Date().toISOString().slice(0, 10),
				requirement: 'Describe deliverable',
				description: ''
			}
		];
		activeStep = stages.length - 1;
	};

	const updateStage = (index: number, changes: Partial<StageDraft>) => {
		stages = stages.map((stage: StageDraft, i: number) => (i === index ? { ...stage, ...changes } : stage));
	};

	const handleSubmit = () => {
		const hasEmpty = stages.some((stage: StageDraft) => !stage.name || !stage.requirement);
		if (hasEmpty) {
			error = 'Please name each milestone and describe its requirement.';
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
						<span class="font-semibold">{stage.name}</span>
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
						id="stage-name"
						label="Stage name"
						placeholder="Prototype delivery"
						bind:value={stages[activeStep].name}
						on:change={(event: Event) =>
							updateStage(activeStep, { name: (event.target as HTMLInputElement).value })}
						required
					/>
					<InputField
						id="stage-budget"
						label="Budget (USD)"
						type="number"
						placeholder="5000"
						bind:value={stages[activeStep].amount}
						on:change={(event: Event) =>
							updateStage(activeStep, { amount: Number((event.target as HTMLInputElement).value) })}
						required
					/>
					<InputField
						id="stage-date"
						label="Target date"
						type="text"
						placeholder="2025-01-15"
						bind:value={stages[activeStep].due}
						on:change={(event: Event) =>
							updateStage(activeStep, { due: (event.target as HTMLInputElement).value })}
						required
					/>
					<label class="space-y-2 text-sm text-slate-200" for="stage-requirement">
						<div class="flex items-center justify-between">
							<span class="font-semibold">Requirement</span>
						</div>
						<textarea
							id="stage-requirement"
							class="min-h-[120px] w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand focus:ring-2 focus:ring-brand"
							placeholder="Upload a 5 minute demo recording and short summary."
							bind:value={stages[activeStep].requirement}
							oninput={(event) =>
								updateStage(activeStep, { requirement: (event.target as HTMLTextAreaElement).value })}
						></textarea>
					</label>
					<InputField
						id="stage-requirement-description"
						label="Requirement details (optional)"
						placeholder="Links, acceptance criteria"
						bind:value={stages[activeStep].description}
						on:change={(event: Event) =>
							updateStage(activeStep, { description: (event.target as HTMLInputElement).value })}
					/>
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
