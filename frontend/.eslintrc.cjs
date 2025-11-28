export default {
	root: true,
	env: {
		browser: true,
		es2023: true,
		node: true
	},
	parser: 'svelte-eslint-parser',
	parserOptions: {
		parser: '@typescript-eslint/parser',
		sourceType: 'module',
		extraFileExtensions: ['.svelte'],
		project: './tsconfig.json'
	},
	plugins: ['@typescript-eslint', 'svelte'],
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/recommended',
		'plugin:svelte/recommended',
		'prettier'
	],
	ignorePatterns: ['.svelte-kit', 'build', 'dist', 'node_modules']
};
