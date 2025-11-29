export type RequirementDraft = {
	name: string;
	description?: string;
};

export type StageContractDraft = {
	enabled: boolean;
	name: string;
	applicable_cards: string;
	allowed_mcc: string;
	blocked_mcc: string;
	blocked_merchants: string;
	max_amount: number;
	description?: string;
};

export type StageDraft = {
	amount: number;
	requirements: RequirementDraft[];
	contract?: StageContractDraft;
};

export type StagePayload = {
	order: number;
	amount: number;
	requirements: { name: string; description?: string }[];
};
