import js from '@eslint/js';
import svelte from 'eslint-plugin-svelte';
import svelteParser from 'svelte-eslint-parser';
import tsParser from '@typescript-eslint/parser';
import globals from 'globals';
import prettier from 'eslint-config-prettier';

export default [
	{
		ignores: ['build', 'node_modules', '.svelte-kit']
	},
	js.configs.recommended,
	...svelte.configs['flat/recommended'],
	prettier,
	{
		files: ['**/*.svelte'],
		languageOptions: {
			parser: svelteParser,
			parserOptions: {
				parser: tsParser,
				extraFileExtensions: ['.svelte'],
				ecmaVersion: 'latest',
				sourceType: 'module'
			},
			globals: { ...globals.browser, ...globals.node }
		},
		rules: {
			'svelte/no-at-html-tags': 'off',
			'svelte/require-each-key': 'off',
			'svelte/no-navigation-without-resolve': 'off',
			'no-unused-vars': 'warn',
			'no-undef': 'off'
		}
	},
	{
		files: ['**/*.{ts,js}'],
		languageOptions: {
			parser: tsParser,
			parserOptions: {
				ecmaVersion: 'latest',
				sourceType: 'module'
			},
			globals: { ...globals.browser, ...globals.node }
		},
		rules: {
			'no-unused-vars': 'warn',
			'no-undef': 'off',
			'svelte/no-navigation-without-resolve': 'off'
		}
	}
];
