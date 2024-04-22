export enum IconsTypes {
	GEAR = 'gear',
	ADD = 'add',
	CLOSE = 'close',
	BACK = 'back',
	TRASH = 'trash',
	PENCIL = 'pencil',
	SEARCH = 'search',
	UPLOAD = 'upload',
	DOWNLOAD = 'download',
	DOCUMENT = 'document'
}

export interface IconBody {
	path?: string;
	fill: string;
	color?: string | null;
	colorStroke?: string | null;
	className: string;
	viewBox: string;
	fillRule: 'evenodd' | 'inherit' | 'nonzero' | null | undefined;
	strokeLinecap: 'butt' | 'round' | 'square' | 'inherit' | null | undefined;
	strokeLinejoin: 'miter' | 'round' | 'bevel' | 'inherit' | null | undefined;
	strokeWidth: number;
}
