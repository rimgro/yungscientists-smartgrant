<script lang="ts">
	let { data, children } = $props();
	const user = data.session.user;
</script>

<section class="space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 shadow-lg">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Authenticated</p>
			<h2 class="text-xl font-semibold text-slate-100">Welcome back, {user.name}</h2>
			<p class="text-sm text-slate-400">{user.email}</p>
		</div>
		<div class="flex flex-wrap gap-2 text-xs text-slate-300">
			<a class="rounded-full border border-white/10 px-4 py-2 font-semibold hover:border-brand hover:text-brand" href="/dashboard">Dashboard</a>
			<a class="rounded-full border border-white/10 px-4 py-2 font-semibold hover:border-brand hover:text-brand" href="/grants">Grants</a>
			<a class="rounded-full border border-white/10 px-4 py-2 font-semibold hover:border-brand hover:text-brand" href="/profile">Profile</a>
		</div>
	</div>

	{@render children()}
</section>
