<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { isAuthenticated, currentUser, clearSession } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	let { children } = $props();

	const handleLogout = async () => {
		clearSession();
		await goto('/login');
	};
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="theme-color" content="#0ea5e9" />
</svelte:head>

<div class="relative min-h-screen text-slate-100">
	<div class="pointer-events-none absolute inset-0 overflow-hidden">
		<div class="absolute left-10 top-16 h-52 w-52 rounded-full bg-brand/20 blur-3xl"></div>
		<div class="absolute right-10 top-10 h-64 w-64 rounded-full bg-brand/10 blur-3xl"></div>
		<div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(14,165,233,0.08),transparent_45%)]"></div>
	</div>

	<header class="sticky top-0 z-30 backdrop-blur-md">
		<div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
			<a class="flex items-center gap-3 rounded-full bg-white/10 px-4 py-2 text-sm font-semibold uppercase tracking-[0.18em] text-slate-100 shadow-soft-lg" href="/">
				<span class="grid h-10 w-10 place-items-center rounded-2xl bg-brand/20 text-brand-strong">SG</span>
				<span>SmartGrant</span>
			</a>
			<nav class="flex items-center gap-3 text-sm">
				{#if $isAuthenticated}
					<a class="rounded-full px-4 py-2 text-slate-200 transition hover:bg-white/10" href="/grants">
						Grants
					</a>
					<a class="rounded-full px-4 py-2 text-slate-200 transition hover:bg-white/10" href="/profile">
						Profile
					</a>
					<button class="rounded-full px-4 py-2 text-slate-200 transition hover:bg-white/10" onclick={handleLogout}>
						Logout
					</button>
				{:else}
					<a class="rounded-full px-4 py-2 text-slate-200 transition hover:bg-white/10" href="/login">
						Login
					</a>
					<a class="btn-primary" href="/register">Create account</a>
				{/if}
			</nav>
		</div>
	</header>

	<main class="relative z-10 mx-auto max-w-6xl px-6 py-10">{@render children()}</main>

	<footer class="relative z-10 border-t border-white/5 bg-surface/50">
		<div class="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 text-xs text-slate-400 sm:flex-row sm:items-center sm:justify-between">
			<span>Client-side SvelteKit SPA · Static deploy ready</span>
			<span class="font-medium text-slate-300">Mir Grants Platform</span>
		</div>
	</footer>
</div>
