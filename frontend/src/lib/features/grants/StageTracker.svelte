<script lang="ts">
import type { Stage } from '$lib/types';

let { stages = [] as Stage[] } = $props();

const completed = $derived(stages.filter((stage) => stage.completion_status === 'completed').length);
const total = $derived(stages.length || 1);
const progress = $derived(Math.min(100, Math.round((completed / total) * 100)));
</script>

<div class="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg">
	<header class="flex items-center justify-between">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Stages</p>
			<h3 class="text-lg font-semibold text-slate-100">Lifecycle tracker</h3>
		</div>
		<span class="rounded-full bg-brand/10 px-3 py-1 text-xs font-semibold text-brand">
			{completed}/{total} complete
		</span>
	</header>

	<div class="h-3 overflow-hidden rounded-full bg-white/10">
	<div class="h-full bg-brand transition-all" style={`width: ${progress}%`}></div>
	</div>

	<ol class="space-y-3">
		{#each stages as stage}
			<li class="flex items-start gap-3 rounded-xl border border-white/5 bg-white/5 px-4 py-3">
				<span
					class={`mt-1 h-3 w-3 rounded-full ${
						stage.completion_status === 'completed'
							? 'bg-brand'
							: stage.completion_status === 'active'
								? 'bg-amber-300'
								: 'bg-slate-500'
					}`}
				></span>
				<div class="flex-1">
					<div class="flex items-center justify-between gap-3">
						<div>
							<p class="text-sm font-semibold text-slate-100">
								#{stage.order} · Stage {stage.order}
							</p>
							<p class="text-xs text-slate-400">
								${stage.amount.toLocaleString()} · {stage.requirements.length} requirements
							</p>
						</div>
						<span
							class={`rounded-full px-3 py-1 text-xs font-semibold ${
								stage.completion_status === 'completed'
									? 'bg-brand/15 text-brand'
									: stage.completion_status === 'active'
										? 'bg-amber-500/15 text-amber-200'
										: 'bg-white/10 text-slate-300'
							}`}
						>
							{stage.completion_status === 'completed'
								? 'Completed'
								: stage.completion_status === 'active'
									? 'Active'
									: 'Pending'}
						</span>
					</div>
					{#if stage.requirements.length}
						<ul class="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
							{#each stage.requirements as req}
								<li class="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-200">
									<span
										class={`h-2 w-2 rounded-full ${req.status === 'completed' ? 'bg-emerald-400' : 'bg-slate-500'}`}
									></span>
									<span class="font-semibold">{req.name}</span>
									<span class="text-[11px] text-slate-400">{req.description}</span>
								</li>
							{/each}
						</ul>
					{/if}
				</div>
			</li>
		{/each}
	</ol>
</div>
