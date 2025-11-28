import { describe, expect, it } from 'vitest';
import type { GrantProgram } from '$lib/types';
import { canManageMilestones, getUserRolesForGrant } from './permissions';

const baseGrant: GrantProgram = {
	id: 'grant-1',
	name: 'Test',
	bank_account_number: 'MIR-001',
	status: 'draft',
	stages: [],
	participants: []
};

describe('grant permissions', () => {
	it('returns all active roles for a user', () => {
		const grant: GrantProgram = {
			...baseGrant,
			participants: [
				{ id: '1', user_id: 'u1', grant_program_id: baseGrant.id, role: 'grantor', active: true },
				{ id: '2', user_id: 'u1', grant_program_id: baseGrant.id, role: 'supervisor', active: true },
				{ id: '3', user_id: 'u1', grant_program_id: baseGrant.id, role: 'grantee', active: false }
			]
		};

		const roles = getUserRolesForGrant(grant, 'u1');
		expect(roles).toEqual(['grantor', 'supervisor']);
	});

	it('allows grantor and supervisor to manage milestones', () => {
		const grant: GrantProgram = {
			...baseGrant,
			participants: [
				{ id: '1', user_id: 'u1', grant_program_id: baseGrant.id, role: 'grantor', active: true },
				{ id: '2', user_id: 'u2', grant_program_id: baseGrant.id, role: 'supervisor', active: true }
			]
		};

		expect(canManageMilestones(grant, 'u1')).toBe(true);
		expect(canManageMilestones(grant, 'u2')).toBe(true);
	});

	it('blocks grantees and inactive roles from milestone actions', () => {
		const grant: GrantProgram = {
			...baseGrant,
			participants: [
				{ id: '1', user_id: 'u1', grant_program_id: baseGrant.id, role: 'grantee', active: true },
				{ id: '2', user_id: 'u1', grant_program_id: baseGrant.id, role: 'supervisor', active: false }
			]
		};

		expect(canManageMilestones(grant, 'u1')).toBe(false);
		expect(getUserRolesForGrant(grant, 'u1')).toEqual(['grantee']);
	});
});
