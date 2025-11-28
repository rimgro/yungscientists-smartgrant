const defaultTheme = require('tailwindcss/defaultTheme');
const forms = require('@tailwindcss/forms');
const typography = require('@tailwindcss/typography');

/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			fontFamily: {
				sans: ['"Space Grotesk"', 'Manrope', ...defaultTheme.fontFamily.sans],
				display: ['"Space Grotesk"', ...defaultTheme.fontFamily.sans]
			},
			colors: {
				brand: {
					DEFAULT: '#0ea5e9',
					deep: '#075985',
					muted: '#e0f2fe',
					strong: '#075985'
				},
				ink: '#0b1221',
				surface: '#0f172a'
			},
			boxShadow: {
				'soft-lg': '0 20px 60px -24px rgba(14, 165, 233, 0.35)'
			}
		}
	},
	plugins: [forms, typography]
};
