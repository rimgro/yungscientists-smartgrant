import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { clearSession, getSession } from '$lib/stores/auth';

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

type RequestOptions = RequestInit & {
	skipAuthRedirect?: boolean;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
	const session = getSession();
	const headers = new Headers(options.headers ?? {});

	if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
		headers.set('Content-Type', 'application/json');
	}

	if (session?.token) {
		headers.set('Authorization', `Bearer ${session.token}`);
	}

	const response = await fetch(`${API_BASE_URL}${path}`, {
		method: options.method ?? 'GET',
		...options,
		headers
	});

	if (response.status === 401 && browser) {
		clearSession();
		if (!options.skipAuthRedirect) {
			await goto('/login');
		}
		throw new Error('Unauthorized');
	}

	if (!response.ok) {
		const message = await parseError(response);
		throw new Error(message);
	}

	if (response.status === 204) return undefined as T;

	const contentType = response.headers.get('content-type');
	if (contentType?.includes('application/json')) {
		return (await response.json()) as T;
	}

	return (await response.text()) as T;
}

async function parseError(response: Response) {
	const contentType = response.headers.get('content-type');
	if (contentType?.includes('application/json')) {
		const body = await response.json();
		return body.message ?? body.error ?? JSON.stringify(body);
	}
	return response.statusText || 'Request failed';
}

export const api = {
	get: <T>(path: string, options?: RequestOptions) => request<T>(path, { ...options, method: 'GET' }),
	post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
		request<T>(path, {
			...options,
			method: 'POST',
			body: body instanceof FormData ? body : JSON.stringify(body ?? {})
		}),
	put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
		request<T>(path, {
			...options,
			method: 'PUT',
			body: body instanceof FormData ? body : JSON.stringify(body ?? {})
		}),
	patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
		request<T>(path, {
			...options,
			method: 'PATCH',
			body: body instanceof FormData ? body : JSON.stringify(body ?? {})
		}),
	delete: <T>(path: string, options?: RequestOptions) =>
		request<T>(path, { ...options, method: 'DELETE' })
};

export type ApiClient = typeof api;
