import { writable } from 'svelte/store';

export type ToastTone = 'success' | 'error' | 'info';

export type Toast = {
	id: string;
	title: string;
	message?: string;
	tone?: ToastTone;
	timeout?: number;
};

const toasts = writable<Toast[]>([]);

export function pushToast(toast: Omit<Toast, 'id'> & { id?: string }) {
	const id = toast.id ?? crypto.randomUUID();
	const tone = toast.tone ?? 'info';

	toasts.update((list) => [...list, { ...toast, id, tone }]);

	if (toast.timeout) {
		setTimeout(() => dismissToast(id), toast.timeout);
	}

	return id;
}

export function dismissToast(id: string) {
	toasts.update((list) => list.filter((item) => item.id !== id));
}

export default toasts;
