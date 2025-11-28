<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { z } from 'zod';
	import { Button, InputField } from '$lib/components';
	import type { UserRole } from '$lib/stores/auth';

	type RegistrationPayload = {
		name: string;
		email: string;
		password: string;
		role: UserRole;
	};

	const dispatch = createEventDispatcher<{ submit: RegistrationPayload }>();

	let { busy = false } = $props();
	let form: RegistrationPayload = {
		name: '',
		email: '',
		password: '',
		role: 'grantee'
	};
	let errors: Partial<Record<keyof RegistrationPayload, string>> = {};

	const schema = z.object({
		name: z.string().min(2, 'Add your full name'),
		email: z.string().email('Use a valid email'),
		password: z.string().min(8, 'Use at least 8 characters'),
		role: z.enum(['grantee', 'grantor', 'supervisor'])
	});

	const handleSubmit = () => {
		const validation = schema.safeParse(form);
		if (!validation.success) {
			const fieldErrors = validation.error.flatten().fieldErrors;
			errors = {
				name: fieldErrors.name?.[0],
				email: fieldErrors.email?.[0],
				password: fieldErrors.password?.[0],
				role: fieldErrors.role?.[0]
			};
			return;
		}

		errors = {};
		dispatch('submit', validation.data);
	};
</script>

<form class="space-y-5 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl">
	<header class="space-y-2">
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Create account</p>
		<h1 class="text-2xl font-semibold text-slate-100">Join SmartGrant</h1>
		<p class="text-sm text-slate-400">
			Set your role to tailor the experience for Grantees, Grantors, or Supervisors.
		</p>
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
		<label class="space-y-2 text-sm text-slate-200">
			<div class="flex items-center justify-between">
				<span class="font-semibold">Role</span>
				{#if errors.role}
					<span class="text-xs font-medium text-rose-300">{errors.role}</span>
				{/if}
			</div>
			<select
				class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand"
				bind:value={form.role}
			>
				<option value="grantee">Grantee — submit milestones and files</option>
				<option value="grantor">Grantor — approve stages & fund releases</option>
				<option value="supervisor">Supervisor — oversight & compliance</option>
			</select>
		</label>
	</div>

	<div class="flex items-center justify-between gap-3">
		<div class="text-xs text-slate-400">We’ll send a verification email to activate access.</div>
		<Button type="submit" disabled={busy} on:click|preventDefault={handleSubmit}>
			{busy ? 'Creating…' : 'Create account'}
		</Button>
	</div>
</form>
