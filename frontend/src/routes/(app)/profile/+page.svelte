<script lang="ts">
	let { data } = $props();
	const { session } = data;
</script>

<div class="space-y-6">
	<div>
		<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">Profile</p>
		<h1 class="text-3xl font-semibold text-slate-50">{session.user.name}</h1>
		<p class="text-sm text-slate-400">{session.user.email}</p>
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		<div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg">
			<h3 class="text-lg font-semibold text-slate-100">Credentials</h3>
			<p class="text-sm text-slate-400">JWT stored client-side.</p>
			<div class="mt-3 space-y-2 text-sm text-slate-300">
				<p><span class="font-semibold text-slate-100">Bank ID:</span> {session.user.bank_id ?? '—'}</p>
			</div>
		</div>
		<div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg">
			<h3 class="text-lg font-semibold text-slate-100">Security</h3>
			<ul class="list-disc pl-5 text-sm text-slate-300">
				<li>LocalStorage session clearing on logout</li>
				<li>401 responses trigger redirect to /login</li>
				<li>PUBLIC_API_BASE_URL used for client-only fetches</li>
			</ul>
		</div>
	</div>
</div>
