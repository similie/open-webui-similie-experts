import type { ICollection } from '$lib/apis/collections';
import type { IDocuments } from '$lib/apis/documents';
import { APP_NAME } from '$lib/constants';
import { writable } from 'svelte/store';

// Backend
export const WEBUI_NAME = writable(APP_NAME);
export const config = writable(undefined);
export const user = writable(undefined);

// Frontend
export const MODEL_DOWNLOAD_POOL = writable({});

export const theme = writable('system');
export const chatId = writable('');

export const chats = writable([]);
export const tags = writable([]);
export const models = writable([]);

export const modelfiles = writable([]);
export const prompts = writable([]);
export const documents = writable<IDocuments[]>([]);

export const documentStore = writable<Record<string, IDocuments>>({});

export const collectionsModels = writable<ICollection[]>([] as ICollection[]);
export const settings = writable({});
export const showSettings = writable(false);
export const showChangelog = writable(false);
