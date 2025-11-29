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

export type RequirementStatus = 'pending' | 'completed';

export type Requirement = {
	id: string;
	name: string;
	description?: string;
	status: RequirementStatus;
	proof_url?: string | null;
	proof_submitted_by?: string | null;
};

export type StageStatus = 'pending' | 'active' | 'completed';

export type Stage = {
	id: string;
	order: number;
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
	email?: string | null;
	name?: string | null;
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

export type PaymentContract = {
	contract_id: string;
	name: string;
	contract_type: string;
	description?: string | null;
	status: string;
	parameters: Record<string, unknown>;
	created_at: string;
};

export type PaymentRuleCheck = {
	allowed: boolean;
	reason?: string | null;
	rules_checked: string[];
	details?: Record<string, unknown> | null;
};

export type PaymentTransaction = {
	transaction_id: string;
	status: string;
	amount: number;
	type: string;
	timestamp: string;
};
