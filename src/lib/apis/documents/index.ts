import { WEBUI_API_BASE_URL } from '$lib/constants';
import { documentStore } from '$lib/stores';
import { ApiTools } from '../api';

export interface IDocumentContent {
	tags: any[];
}

export interface IDocuments {
	collection: string;
	collection_name: string;
	user_id: string;
	content: IDocumentContent | string;
	filename: string;
	original_filename: string;
	name: string;
	title: string;
	timestamp: string;
	path: string;
}

export interface RAGMetaData {
	page: number;
	source: string;
	start_index: number;
	uris?: string;
	content?: string;
	summary?: string;
}

export interface RAGResponse {
	data: string;
	distances: number[][];
	documents: string[][];
	ids: string[][];
	metadatas: RAGMetaData[][];
}

interface IDocumentStore {
	retrieveFileNames: string[];
	storedFileNames: IDocuments[];
}

export class DocumentsApi {
	api: ApiTools<Partial<IDocuments>>;
	constructor() {
		this.api = new ApiTools<Partial<IDocuments>>('documents', localStorage.token);
	}

	private sendBlobToDownload(doc: IDocuments): (res: Blob) => Blob {
		return (res: Blob) => {
			const url = URL.createObjectURL(res);
			// Create a temporary anchor element and trigger download
			const a = document.createElement('a');
			a.href = url;
			a.download = doc.original_filename || doc.filename;
			document.body.appendChild(a); // Append to the document
			a.click(); // Trigger the download
			// Clean up by removing the element and revoking the Blob URL
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
			return res;
		};
	}

	private filterRagResponses(rAGResponses: RAGResponse[]): string[] {
		return rAGResponses
			.map((res) =>
				res.metadatas
					.map((meta) => meta.map((m) => m.source))
					.flat()
					.filter((f) => f)
			)
			.flat()
			.filter((f) => f);
	}

	private getDocsInStore(): Promise<Record<string, IDocuments>> {
		return new Promise<Record<string, IDocuments>>(documentStore.subscribe);
	}

	private getShortName(name: string) {
		return name.split('/').pop() || '';
	}

	private findDocsByNameInStore(
		filenames: string[],
		docs: Record<string, IDocuments>
	): IDocumentStore {
		const retrieveFileNames: string[] = [];
		const storedFileNames: IDocuments[] = [];
		const nameHold: Record<string, boolean> = {};
		for (const name of filenames) {
			const shortName = this.getShortName(name);
			if (nameHold[shortName]) {
				continue;
			}
			nameHold[shortName] = true;
			if (docs[shortName]) {
				storedFileNames.push(docs[shortName]);
				continue;
			}
			retrieveFileNames.push(name);
		}
		return { storedFileNames, retrieveFileNames };
	}

	private getWritableStore(
		apiDocs: IDocuments[],
		storedDocs: Record<string, IDocuments>
	): Record<string, IDocuments> {
		for (const doc of apiDocs) {
			storedDocs[doc.filename] = doc;
		}
		return storedDocs;
	}

	private mergeDocs(
		storedFileNames: IDocuments[],
		apiDocs: IDocuments[],
		storedDocs: Record<string, IDocuments>
	) {
		documentStore.set(this.getWritableStore(apiDocs, storedDocs));
		return [...apiDocs, ...storedFileNames];
	}

	public async addToDocStore(docs: IDocuments[]) {
		const storedDocs = await this.getDocsInStore();
		documentStore.set(this.getWritableStore(docs, storedDocs));
	}
	/**
	 * @description Download a document
	 * @param {IDocuments} doc
	 * @returns {Buffer}
	 */
	public downloadDoc(doc: IDocuments) {
		return this.api
			.get<Blob>(`download/${doc.collection_name}`, {}, 'application/octet-stream')
			.then(this.sendBlobToDownload(doc));
	}

	/**
	 * @description We pull the documents but cache what we already have
	 * @param {RAGResponse[]} rAGResponses
	 * @returns {IDocuments[]}
	 */
	public async findDocsByNameInCollection(rAGResponses: RAGResponse[]) {
		const filenames = this.filterRagResponses(rAGResponses);
		const docs = await this.getDocsInStore();
		const store: IDocumentStore = this.findDocsByNameInStore(filenames, docs);
		// keep if off the api if we have the details
		if (!store.retrieveFileNames.length) {
			return store.storedFileNames;
		}
		const apiDocs = await this.api.get<IDocuments[]>('files/', {
			filenames: store.retrieveFileNames
		});
		return this.mergeDocs(store.storedFileNames, apiDocs, docs);
	}

	public async createDocument(document: Partial<IDocuments>) {
		return this.api.post<IDocuments>(`create`, document);
	}

	public async getDocsThroughCollection(collectionKey: string = '') {
		return this.api.get<IDocuments[]>(`?collection=${collectionKey}`);
	}
}

export const createNewDoc = async (
	token: string,
	collection_name: string,
	collection: string,
	filename: string,
	name: string,
	title: string,
	content: object | null = null
) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/create`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			collection_name: collection_name,
			collection: collection,
			filename: filename,
			name: name,
			title: title,
			...(content ? { content: JSON.stringify(content) } : {})
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getDocsThroughCollection = async (token: string = '', collectionKey: string = '') => {
	let error = null;
	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/?collection=${collectionKey}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.then((json) => {
			return json;
		})
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getDocs = async (token: string = '') => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.then((json) => {
			return json;
		})
		.catch((err) => {
			error = err.detail;
			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getDocByName = async (token: string, name: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/name/${name}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.then((json) => {
			return json;
		})
		.catch((err) => {
			error = err.detail;

			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

type DocUpdateForm = {
	name: string;
	title: string;
};

export const updateDocByName = async (token: string, name: string, form: DocUpdateForm) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/name/${name}/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			name: form.name,
			title: form.title
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.then((json) => {
			return json;
		})
		.catch((err) => {
			error = err.detail;

			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

type TagDocForm = {
	name: string;
	tags: string[];
};

export const tagDocByName = async (token: string, name: string, form: TagDocForm) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/name/${name}/tags`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			name: form.name,
			tags: form.tags
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.then((json) => {
			return json;
		})
		.catch((err) => {
			error = err.detail;

			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteDocByName = async (token: string, name: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/documents/name/${name}/delete`, {
		method: 'DELETE',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.then((json) => {
			return json;
		})
		.catch((err) => {
			error = err.detail;

			console.log(err);
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
