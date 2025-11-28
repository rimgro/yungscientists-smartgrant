<script lang="ts">
	type ButtonVariant = 'primary' | 'ghost' | 'outline';
	type ButtonSize = 'sm' | 'md' | 'lg';

	let {
		variant = 'primary' as ButtonVariant,
		size = 'md' as ButtonSize,
		type = 'button' as 'button' | 'submit' | 'reset',
		disabled = false,
		class: className = '',
		children,
		...restProps
	} = $props();

	const base =
		'inline-flex items-center justify-center gap-2 rounded-full font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand focus-visible:ring-offset-surface';

	const variants: Record<ButtonVariant, string> = {
		primary:
			'bg-brand text-surface shadow-soft-lg hover:-translate-y-0.5 hover:bg-brand-strong disabled:bg-brand/40 disabled:text-slate-300',
		ghost: 'bg-white/5 text-slate-100 hover:bg-white/10 disabled:opacity-60',
		outline:
			'border border-white/20 text-slate-50 hover:border-brand hover:text-brand disabled:opacity-60'
	};

	const sizes: Record<ButtonSize, string> = {
		sm: 'px-3 py-2 text-xs',
		md: 'px-4 py-2.5 text-sm',
		lg: 'px-5 py-3 text-base'
};
</script>

<button class={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {type} {disabled} {...restProps}>
	{@render children?.()}
</button>
