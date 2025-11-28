import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	testDir: './tests/e2e',
	use: {
		baseURL: 'http://localhost:5173',
		headless: true
	}
};

export default config;
