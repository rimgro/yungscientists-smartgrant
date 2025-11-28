<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { z } from 'zod';
import { Button, InputField } from '$lib/components';

	type RegistrationPayload = {
		name: string;
		email: string;
		password: string;
		bank_id?: string;
	};

	const dispatch = createEventDispatcher<{ submit: RegistrationPayload }>();

	let { busy = false } = $props();
	let form: RegistrationPayload = {
		name: '',
		email: '',
		password: '',
		bank_id: ''
	};
	let errors: Partial<Record<keyof RegistrationPayload, string>> = $state({});

	const schema = z.object({
		name: z.string().min(2, 'Add your full name'),
		email: z.string().email('Use a valid email'),
		password: z.string().min(8, 'Use at least 8 characters'),
		bank_id: z.string().optional()
	});

	const handleSubmit = (event: SubmitEvent) => {
		event.preventDefault();
		const validation = schema.safeParse(form);
		if (!validation.success) {
			const fieldErrors = validation.error.flatten().fieldErrors;
			errors = {
				name: fieldErrors.name?.[0],
				email: fieldErrors.email?.[0],
				password: fieldErrors.password?.[0],
				bank_id: fieldErrors.bank_id?.[0]
			};
			return;
		}

		errors = {};
		dispatch('submit', validation.data);
	};
</script>

<form class="space-y-5 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl" onsubmit={handleSubmit}>
	<header class="space-y-2">
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Create account</p>
		<h1 class="text-2xl font-semibold text-slate-100">Join SmartGrant</h1>
		<p class="text-sm text-slate-400">We’ll link your MIR bank ID after signup if provided.</p>
	</header>

	<div class="space-y-4">
		<InputField
			id="name"
			label="Full name"
			placeholder="Ada Lovelace"
			bind:value={form.name}
			error={errors.name}
			required
		/>
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
		<InputField
			id="bank-id"
			label="Bank ID (optional)"
			placeholder="MIR-ACCOUNT-123"
			bind:value={form.bank_id}
			error={errors.bank_id}
		/>
	</div>

	<div class="flex items-center justify-between gap-3">
		<div class="text-xs text-slate-400">We’ll send a verification email to activate access.</div>
		<Button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create account'}</Button>
	</div>
</form>
