<script lang="ts">
	import { Button, Card, SectionHeader } from '$lib/components';
</script>

<section class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
	<div class="space-y-6">
		<p class="text-xs font-semibold uppercase tracking-[0.28em] text-brand">Mir SmartGrant</p>
		<h1 class="text-4xl font-semibold leading-tight text-slate-50 sm:text-5xl">
			Client-side SmartGrant workspace for grants, approvals, and MIR payouts.
		</h1>
		<p class="max-w-2xl text-lg text-slate-300">
			SPA-first SvelteKit build. Static deploy, CSR-only routing, typed stores, and modular
			features for auth, grants, and payments.
		</p>
		<div class="flex flex-wrap gap-4">
			<a class="btn-primary" href="/register">Get started</a>
			<a class="rounded-full border border-white/10 px-5 py-3 text-sm font-semibold text-slate-100 hover:border-brand hover:text-brand" href="/login">
				Use existing account
			</a>
		</div>
		<div class="grid gap-4 sm:grid-cols-3">
			{#each [
				{ title: 'Auth', body: 'JWT session stored client-side with guard layouts.' },
				{ title: 'Grants', body: 'Stages, requirements, and MIR payout triggers.' },
				{ title: 'Payments', body: 'Wallet connect + ledger visibility.' }
			] as item}
				<div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
					<p class="font-semibold text-slate-50">{item.title}</p>
					<p class="text-slate-400">{item.body}</p>
				</div>
			{/each}
		</div>
	</div>

	<Card
		title="Static CSR deployment"
		description="Adapter-static + fallback routing for Nginx/S3. SSR disabled at root layout."
	>
		<SectionHeader
			eyebrow="Architecture"
			title="Project backbone"
			kicker="Routes grouped by auth/app, typed stores, Tailwind styling, and API wrapper."
		/>
		<ul class="space-y-3 text-sm text-slate-200">
			<li>• `src/routes/+layout.ts` sets `ssr=false` and `prerender=true`</li>
			<li>• `(auth)/` login & register; `(app)/` dashboard, grants, profile</li>
			<li>• Global stores: auth session + toasts; API wrapper injects JWT</li>
			<li>• Tailwind + custom theme.css for Mir palette</li>
		</ul>
		<div class="mt-4 flex gap-3">
			<a class="btn-primary" href="/dashboard">Open dashboard</a>
			<a class="rounded-full border border-white/10 px-4 py-2 text-sm font-semibold text-slate-100 hover:border-brand hover:text-brand" href="/grants/new">Launch wizard</a>
		</div>
	</Card>
</section>
