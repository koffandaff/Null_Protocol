import Auth from './auth.js';
import Components from './components.js';

class Router {
    constructor() {
        this.routes = {};
        window.addEventListener('hashchange', () => this.handleRoute());
        this.app = document.getElementById('app');
    }

    addRoute(path, view, requiresAuth = false) {
        this.routes[path] = { view, requiresAuth };
    }

    navigate(path) {
        window.location.hash = path;
    }

    async handleRoute() {
        let path = window.location.hash.slice(1) || '/';

        // Normalize paths that don't start with /
        if (path !== '/' && !path.startsWith('/')) {
            path = '/' + path;
        }

        const route = this.routes[path] || this.routes['/login'];

        if (!route) {
            this.navigate('/');
            return;
        }

        if (route.requiresAuth && !Auth.isAuthenticated()) {
            this.navigate('/login');
            return;
        }

        if (path === '/login' && Auth.isAuthenticated()) {
            this.navigate('/dashboard');
            return;
        }

        try {
            this.app.innerHTML = await route.view.render();

            // Inject floating chat widget on authenticated pages (except chat page itself)
            if (route.requiresAuth && path !== '/chat') {
                this.app.innerHTML += Components.renderFloatingChat();
            }

            if (route.view.afterRender) {
                await route.view.afterRender();
            }
        } catch (e) {
            console.error('Route Error', e);
            this.app.innerHTML = '<h1>Error loading page</h1>';
        }
    }


    init() {
        this.handleRoute();
    }
}

export default new Router();
