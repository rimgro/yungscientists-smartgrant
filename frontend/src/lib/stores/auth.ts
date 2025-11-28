import { browser } from '$app/environment';
import { derived, get, writable } from 'svelte/store';

const STORAGE_KEY = 'smartgrant.session';

export type UserRole = 'grantee' | 'grantor' | 'supervisor';

export type UserProfile = {
	id: string;
	name: string;
	email?: string;
	role: UserRole;
};

export type Session = {
	token: string;
	user: UserProfile;
};

const restoreSession = (): Session | null => {
	if (!browser) return null;

	const stored = localStorage.getItem(STORAGE_KEY);
	if (!stored) return null;

	try {
		return JSON.parse(stored) as Session;
	} catch (error) {
		console.error('Failed to parse session from storage', error);
		localStorage.removeItem(STORAGE_KEY);
		return null;
	}
};

const session = writable<Session | null>(restoreSession());

session.subscribe((value) => {
	if (!browser) return;
	if (value) {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
	} else {
		localStorage.removeItem(STORAGE_KEY);
	}
});

export const isAuthenticated = derived(session, (value) => Boolean(value?.token));
export const currentUser = derived(session, (value) => value?.user ?? null);

export function loadSessionFromStorage(): Session | null {
	return restoreSession();
}

export function getSession(): Session | null {
	return get(session) ?? restoreSession();
}

export function setSession(value: Session) {
	session.set(value);
}

export function clearSession() {
	session.set(null);
}

export default session;
