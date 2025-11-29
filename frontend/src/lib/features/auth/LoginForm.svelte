<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { z } from 'zod';
	import { Button, InputField } from '$lib/components';

	type Credentials = {
		email: string;
		password: string;
	};

	const dispatch = createEventDispatcher<{ submit: Credentials }>();

	let { busy = false } = $props();
	let form: Credentials = { email: '', password: '' };
	let errors: Partial<Record<keyof Credentials, string>> = $state({});

	const schema = z.object({
		email: z.string().email('Use a valid email'),
		password: z.string().min(8, 'Use at least 8 characters')
	});

	const updateErrors = (issues: typeof errors) => {
		errors = issues;
	};

	const handleSubmit = (event: SubmitEvent) => {
		event.preventDefault();
		const validation = schema.safeParse(form);
		if (!validation.success) {
			const fieldErrors = validation.error.flatten().fieldErrors;
			updateErrors({
				email: fieldErrors.email?.[0],
				password: fieldErrors.password?.[0]
			});
			return;
		}

		updateErrors({});
		dispatch('submit', validation.data);
	};
</script>

<form class="space-y-5 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl" onsubmit={handleSubmit}>
	<header class="space-y-2">
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Welcome back</p>
		<h1 class="text-2xl font-semibold text-slate-100">Sign in to SmartGrant</h1>
		<p class="text-sm text-slate-400">Access the grants workspace and manage payouts.</p>
	</header>

	<div class="space-y-4">
		<InputField
			id="email"
			label="Email"
			type="email"
			placeholder="you@mir.org"
			bind:value={form.email}
			error={errors.email}
			required
		/>
		<InputField
			id="password"
			label="Password"
			type="password"
			placeholder="••••••••"
			bind:value={form.password}
			error={errors.password}
			helper="Min 8 characters"
			required
		/>
	</div>

	<div class="flex items-center justify-between gap-3">
		<div class="text-xs text-slate-400">Mir account holders use the same credentials</div>
		<Button type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</Button>
	</div>
</form>
