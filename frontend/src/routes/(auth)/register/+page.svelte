<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import RegisterForm from '$lib/features/auth/RegisterForm.svelte';
	import { pushToast } from '$lib/stores/notifications';
	import { setSession, type Session } from '$lib/stores/auth';
	import type { TokenResponse, User } from '$lib/types';

	let busy = false;

	const handleSubmit = async (event: CustomEvent<{
		name: string;
		email: string;
		password: string;
		bank_id?: string;
	}>) => {
		busy = true;
		try {
			const payload = { ...event.detail, bank_id: event.detail.bank_id || undefined };
			await api.post<User>('/auth/register', payload, { skipAuthRedirect: true });

			const token = await api.post<TokenResponse>(
				'/auth/login',
				{ email: payload.email, password: payload.password },
				{ skipAuthRedirect: true }
			);
			const user = await api.get<User>('/auth/me', {
				headers: { Authorization: `Bearer ${token.access_token}` },
				skipAuthRedirect: true
			});
			const session: Session = { token: token.access_token, user: { ...user, role: user.role ?? 'User' } };
			setSession(session);
			pushToast({ title: 'Account created', message: 'You are now signed in', tone: 'success', timeout: 2500 });
			await goto('/grants');
		} catch (error) {
			const message = error instanceof Error ? error.message : 'Unable to register';
			pushToast({ title: 'Registration failed', message, tone: 'error', timeout: 4000 });
		} finally {
			busy = false;
		}
	};
</script>

<div class="mx-auto max-w-2xl">
	<RegisterForm busy={busy} on:submit={handleSubmit} />
	<p class="mt-4 text-sm text-slate-400">
		Already have an account? <a class="text-brand hover:underline" href="/login">Login</a>
	</p>
</div>
