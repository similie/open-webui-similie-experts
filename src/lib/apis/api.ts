import { WEBUI_API_BASE_URL } from '$lib/constants';

interface ISendPayload {
	method: string;
	headers: {
		Accept?: string;
		'Content-Type': string;
		authorization: string;
	};
	body?: string;
}

export class ApiTools<T> {
	token: string;
	apiBase: string;
	constructor(apiBase: string, token: string) {
		this.token = token;
		this.apiBase = `${WEBUI_API_BASE_URL}/${apiBase}`;
	}

	private get headers() {
		return {
			'Content-Type': 'application/json',
			authorization: `Bearer ${this.token}`
		};
	}

	private buildHeaders(returnContentType: string = 'application/json') {
		const headers = this.headers;
		headers['Accept'] = returnContentType;
		return headers;
	}

	private fetchPayload(method: string, payload?: T, returnContentType?: string): ISendPayload {
		const sendPayload: ISendPayload = {
			method: method,
			headers: this.buildHeaders(returnContentType)
		};

		if (method === 'GET') {
			return sendPayload;
		}
		sendPayload.body = payload ? JSON.stringify(payload) : '';
		return sendPayload;
	}

	private encodeValue(value: any) {
		const valuesType = typeof value;
		try {
			if (valuesType === 'object') {
				return encodeURIComponent(JSON.stringify(value));
			} else {
				return encodeURIComponent(value);
			}
		} catch {
			return encodeURIComponent(value);
		}
	}

	private jsonToQueryString(json: object) {
		const keys = Object.keys(json);
		if (!keys.length) {
			return '';
		}
		return (
			'?' + keys.map((key) => encodeURIComponent(key) + '=' + this.encodeValue(json[key])).join('&')
		);
	}

	private sendRequest = async (
		path: string,
		method: string,
		payload?: T,
		returnContentType?: string
	) => {
		let error = null;
		const res = await fetch(
			`${this.apiBase}/${path}`,
			this.fetchPayload(method, payload, returnContentType)
		)
			.then(async (res) => {
				if (!res.ok) throw await res.json();

				if ((returnContentType || '').includes('application/octet-stream')) {
					return res.blob();
				}
				return res.json();
			})
			.catch((err) => {
				error = err.detail;
				console.log(err);
				return null;
			});

		if (error) {
			throw new Error(error);
		}
		return res;
	};

	public async post<K>(path: string, payload: T): Promise<K> {
		return this.sendRequest(path, 'POST', payload);
	}

	public async get<K>(path: string, query: object = {}, returnContentType?: string): Promise<K> {
		return this.sendRequest(
			path + `${this.jsonToQueryString(query)}`,
			'GET',
			undefined,
			returnContentType
		);
	}

	public async put<K>(path: string, payload: T): Promise<K> {
		return this.sendRequest(path, 'PUT', payload);
	}

	public async delete<K>(path: string, payload: T): Promise<K> {
		return this.sendRequest(path, 'DELETE', payload);
	}
}
