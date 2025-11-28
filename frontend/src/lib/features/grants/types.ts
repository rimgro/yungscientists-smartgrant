export type RequirementDraft = {
	name: string;
	description?: string;
};

export type StageDraft = {
	amount: number;
	requirements: RequirementDraft[];
};

export type StagePayload = {
	order: number;
	amount: number;
	requirements: { name: string; description?: string }[];
};
