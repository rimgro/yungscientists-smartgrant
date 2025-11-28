export type User = {
	id: string;
	name: string;
	email: string;
	bank_id?: string;
	role?: string;
};

export type TokenResponse = {
	access_token: string;
	token_type: string;
};

export type RequirementStatus = 'pending' | 'active' | 'completed';

export type Requirement = {
	id: string;
	stage_id: string;
	name: string;
	description?: string;
	status: RequirementStatus;
};

export type StageStatus = 'pending' | 'active' | 'completed';

export type Stage = {
	id: string;
	grant_program_id: string;
	order: number;
	name?: string;
	amount: number;
	completion_status: StageStatus;
	requirements: Requirement[];
};

export type GrantParticipantRole = 'grantor' | 'supervisor' | 'grantee';

export type GrantParticipant = {
	id: string;
	user_id: string;
	grant_program_id: string;
	role: GrantParticipantRole;
	active: boolean;
};

export type GrantProgram = {
	id: string;
	name: string;
	bank_account_number: string;
	status: string;
	participants: GrantParticipant[];
	stages: Stage[];
};
