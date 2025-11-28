import type { GrantParticipantRole, GrantProgram } from '$lib/types';

const MANAGER_ROLES: GrantParticipantRole[] = ['grantor', 'supervisor'];

export function getUserRolesForGrant(grant: Pick<GrantProgram, 'participants'>, userId: string): GrantParticipantRole[] {
	return grant.participants
		.filter((participant) => participant.active && participant.user_id === userId)
		.map((participant) => participant.role as GrantParticipantRole);
}

export function canManageMilestones(grant: Pick<GrantProgram, 'participants'>, userId: string): boolean {
	const roles = getUserRolesForGrant(grant, userId);
	return roles.some((role) => MANAGER_ROLES.includes(role));
}
