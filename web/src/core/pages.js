/** Page lifecycle registry. Controllers register once; the router owns URL/history. */
const PageRegistry = (() => {
    const controllers = new Map();
    const ids = new Set(ROUTE_DEFINITIONS.pages.map(page=>page.id));
    function register(id,load) {
        if(!ids.has(id))throw new Error('Unregistered page route: '+id);
        if(controllers.has(id))throw new Error('Duplicate page controller: '+id);
        if(typeof load!=='function')throw new TypeError('Page controller must be a function');
        controllers.set(id,load);
    }
    function load(id) { return controllers.get(id)?.(); }
    return Object.freeze({register,load});
})();
globalThis.FlavoPages=PageRegistry;
