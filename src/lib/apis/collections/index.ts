import { ApiTools } from '../api';
import type { IDocuments } from '../documents';

export interface ICollection {
	name: string;
	title: string;
	content?: string;
	key: string;
	user_id: string;
	timestamp: string;
}

export class CollectionApi {
	api: ApiTools<Partial<ICollection>>;
	_cache: Record<string, IDocuments> = {};
	constructor() {
		this.api = new ApiTools<Partial<ICollection>>('collections', localStorage.token);
	}

	create(collection: Partial<ICollection>) {
		return this.api.post<ICollection>('create', collection);
	}

	delete(key: string) {
		return this.api.delete<boolean>(key, {});
	}

	update(key: string, collection: Partial<ICollection>) {
		return this.api.put<ICollection>(key, collection);
	}

	findOne(key: string) {
		return this.api.get<ICollection>(key, {});
	}

	find() {
		return this.api.get<ICollection[]>('', {});
	}
}
