<script lang="ts">
	let { data } = $props();
	const { session } = data;
</script>

<div class="space-y-6">
	<div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg">
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Profile</p>
		<h1 class="text-3xl font-semibold text-slate-50">{session.user.name}</h1>
		<p class="text-sm text-slate-400">{session.user.email}</p>
	</div>
</div>
