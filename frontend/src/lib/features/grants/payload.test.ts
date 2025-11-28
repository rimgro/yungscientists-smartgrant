import { describe, expect, it } from 'vitest';
import { buildGrantPayload } from './payload';
import type { StageDraft } from './types';

describe('buildGrantPayload', () => {
	it('maps stages to sequential payload with requirements', () => {
		const drafts: StageDraft[] = [
			{ amount: 1000, requirements: [{ name: 'Do A', description: 'desc A' }, { name: 'Do A2' }] },
			{ amount: 2000, requirements: [{ name: 'Do B' }] }
		];

		const payload = buildGrantPayload('Grant', 'ACC-1', drafts);

		expect(payload).toMatchObject({
			name: 'Grant',
			bank_account_number: 'ACC-1',
			participants: []
		});
		expect(payload.stages).toHaveLength(2);
		expect(payload.stages[0]).toEqual({
			order: 1,
			amount: 1000,
			requirements: [
				{ name: 'Do A', description: 'desc A' },
				{ name: 'Do A2', description: '' }
			]
		});
		expect(payload.stages[1]).toEqual({
			order: 2,
			amount: 2000,
			requirements: [{ name: 'Do B', description: '' }]
		});
	});

	it('passes through participants', () => {
		const payload = buildGrantPayload(
			'Grant',
			'ACC-1',
			[{ amount: 100, requirements: [{ name: 'Do A' }] }],
			[{ user_id: 'user-1', role: 'grantee' }]
		);

		expect(payload.participants).toEqual([{ user_id: 'user-1', role: 'grantee' }]);
	});
});
