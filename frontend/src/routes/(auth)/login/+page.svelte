<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import LoginForm from '$lib/features/auth/LoginForm.svelte';
	import { pushToast } from '$lib/stores/notifications';
	import { setSession, type Session } from '$lib/stores/auth';
	import type { TokenResponse, User } from '$lib/types';

	let busy = false;

	const handleSubmit = async (event: CustomEvent<{ email: string; password: string }>) => {
		busy = true;
		try {
			const token = await api.post<TokenResponse>('/auth/login', event.detail, { skipAuthRedirect: true });
			const user = await api.get<User>('/auth/me', {
				headers: { Authorization: `Bearer ${token.access_token}` },
				skipAuthRedirect: true
			});
			const session: Session = { token: token.access_token, user: { ...user, role: user.role ?? 'User' } };
			setSession(session);
			pushToast({ title: 'Signed in', message: 'Session restored', tone: 'success', timeout: 2500 });
			await goto('/dashboard');
		} catch (error) {
			const message = error instanceof Error ? error.message : 'Unable to sign in';
			pushToast({ title: 'Login failed', message, tone: 'error', timeout: 4000 });
		} finally {
			busy = false;
		}
	};
</script>

<div class="mx-auto max-w-2xl">
	<LoginForm busy={busy} on:submit={handleSubmit} />
	<p class="mt-4 text-sm text-slate-400">
		No account yet? <a class="text-brand hover:underline" href="/register">Register</a>
	</p>
</div>
