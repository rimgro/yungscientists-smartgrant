import { loadSessionFromStorage } from '$lib/stores/auth';
import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = () => {
	const session = loadSessionFromStorage();
	if (!session) throw redirect(302, '/login');

	return { session };
};
