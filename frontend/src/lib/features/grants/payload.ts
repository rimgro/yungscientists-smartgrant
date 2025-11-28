import type { GrantParticipantRole } from '$lib/types';
import type { StageDraft, StagePayload } from './types';

export type GrantProgramCreatePayload = {
	name: string;
	bank_account_number: string;
	stages: StagePayload[];
	participants: { user_id: string; role: GrantParticipantRole }[];
};

export function buildGrantPayload(
	name: string,
	bankAccountNumber: string,
	stageDrafts: StageDraft[],
	participants: { user_id: string; role: GrantParticipantRole }[] = []
): GrantProgramCreatePayload {
	return {
		name,
		bank_account_number: bankAccountNumber,
		stages: stageDrafts.map((stage, index) => ({
			order: index + 1,
			amount: stage.amount,
			requirements: stage.requirements.map((req) => ({
				name: req.name,
				description: req.description ?? ''
			}))
		})),
		participants
	};
}
