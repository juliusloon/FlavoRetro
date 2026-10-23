/** Public component contracts; no TypeScript runtime/build dependency. */
interface FlavoPaginationState { offset: number; limit: number; total: number; }
interface FlavoButtonOptions { variant?: 'primary'|'secondary'|'quiet'; disabled?: boolean; type?: 'button'|'submit'|'reset'; onClick?: (event: MouseEvent)=>void; }
interface FlavoUIApi {
    readonly version: string;
    byId(id: string): HTMLElement|null;
    text(tag: string, value: unknown, className?: string): HTMLElement;
    div(className?: string): HTMLDivElement;
    button(label: string, options?: FlavoButtonOptions): HTMLButtonElement;
    badge(value: unknown, className?: string): HTMLElement;
    kv(label: string, value: unknown): HTMLElement;
    fixed(value: unknown, digits?: number): string;
    notice(message: string, options?: {kind?: 'info'|'warning'|'error'; className?: string}): HTMLElement;
    empty(message?: string): HTMLElement;
    panel(options?: {title?: string; children?: Node[]; tag?: string}): HTMLElement;
    split(options: {left: Node; right: Node; variant?: 'reader'|'compare'|'diagram'|'explore'}): HTMLElement;
    field(options: {id: string; label: string; type?: string; value?: string; options?: {value:string;label:string}[]; onChange?: (event: Event)=>void}): HTMLElement;
    listItem(options: {title: string; meta?: string; href?: string; className?: string; onClick?: (event: MouseEvent)=>void}): HTMLAnchorElement;
    pagination(id: string, state: FlavoPaginationState, onChange: (offset:number,limit:number)=>void, sizes?: number[]): void;
    enhance(root?: Document|Element): void;
    mount(root?: Document|Element): void;
}
interface Window { FlavoUI: FlavoUIApi; FlavoPages: {register(id:string,load:()=>unknown):void;load(id:string):unknown}; }
