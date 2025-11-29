<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { isAuthenticated } from '$lib/stores/auth';

	onMount(() => {
		if (!get(isAuthenticated)) {
			goto('/login');
			return;
		}

		const unsubscribe = isAuthenticated.subscribe((authed) => {
			if (!authed) goto('/login');
		});

		return unsubscribe;
	});
</script>

<section class="space-y-4 max-w-3xl">
	<p class="text-xs font-semibold uppercase tracking-[0.24em] text-brand">SmartGrant</p>
	<h1 class="text-4xl font-semibold text-slate-50">Grant management workspace</h1>
	<p class="text-lg text-slate-300">
		SmartGrant keeps your grant programs, participant roles, and payout checkpoints in one place so you can review milestones, confirm proofs, and trigger disbursements without bouncing between tools.
	</p>
	<div class="flex gap-3">
		<a class="btn-primary" href="/grants">Go to grants</a>
		<a class="rounded-full border border-white/10 px-4 py-2 text-sm font-semibold text-slate-100 hover:border-brand hover:text-brand" href="/profile">
			View profile
		</a>
	</div>
</section>
