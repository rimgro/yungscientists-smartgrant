<script lang="ts">
import { Button } from '$lib/components';

let { requirementName = 'Upload proof', onUpload = (file: File) => file } = $props();
let fileName = $state('');

	const handleChange = (event: Event) => {
		const target = event.target as HTMLInputElement;
		if (!target.files?.length) return;
		const file = target.files[0];
		fileName = file.name;
		onUpload(file);
	};
</script>

<div class="rounded-2xl border border-dashed border-brand/40 bg-brand/5 p-5 text-sm text-slate-100">
	<p class="text-xs font-semibold uppercase tracking-[0.22em] text-brand">{requirementName}</p>
	<p class="mb-4 text-sm text-slate-300">
		Attach PDFs, docs, or media that prove completion. Encrypted at rest in MIR storage.
	</p>
	<label class="flex flex-col items-start gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-4 text-left transition hover:border-brand hover:bg-brand/5">
		<span class="text-sm font-semibold text-slate-100">
			{fileName ? `Selected: ${fileName}` : 'Drag & drop or select a file'}
		</span>
		<input class="hidden" type="file" onchange={handleChange} />
		<Button variant="ghost" size="sm">Choose file</Button>
	</label>
</div>
