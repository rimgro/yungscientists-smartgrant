import { browser } from '$app/environment';
import type { User } from '$lib/types';
import { derived, get, writable } from 'svelte/store';

const STORAGE_KEY = 'smartgrant.session';

export type Session = {
	token: string;
	user: User;
};

const isValidSession = (value: unknown): value is Session => {
	if (!value || typeof value !== 'object') return false;
	const session = value as Record<string, unknown>;
	const user = session.user as Record<string, unknown> | undefined;
	return (
		typeof session.token === 'string' &&
		!!user &&
		typeof user.id === 'string' &&
		typeof user.email === 'string' &&
		typeof user.name === 'string'
	);
};

const restoreSession = (): Session | null => {
	if (!browser) return null;

	const stored = localStorage.getItem(STORAGE_KEY);
	if (!stored) return null;

	try {
		const parsed = JSON.parse(stored);
		if (isValidSession(parsed)) {
			return parsed;
		}
		throw new Error('Session shape invalid');
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
