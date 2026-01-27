import Auth from '../auth.js';
import Utils from '../utils.js';
import Router from '../router.js';

class LoginView {
    async render() {
        return `
            <div class="container" style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                <div class="card glass fade-in" style="width: 100%; max-width: 400px;">
                    <h2 class="page-title" style="text-align: center;">Fsociety Login</h2>
                    <p style="text-align: center; color: var(--text-muted); margin-bottom: 2rem;">Enter the system</p>
                    
                    <form id="login-form">
                         <div style="margin-bottom: 1rem;">
                            <label style="display: block; margin-bottom: 0.5rem;">Email</label>
                            <input type="email" id="email" required>
                        </div>
                        
                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; margin-bottom: 0.5rem;">Password</label>
                            <div style="position: relative; display: flex; align-items: center;">
                                <input type="password" id="password" required style="width: 100%; padding-right: 40px;">
                                <span class="material-symbols-outlined toggle-password" style="position: absolute; right: 10px; cursor: pointer; color: var(--text-muted); user-select: none; z-index: 10;">visibility</span>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn" style="width: 100%;">ACCESS SYSTEM</button>
                    </form>

                    <div style="margin-top: 1.5rem; text-align: center;">
                        <a href="#/signup" style="color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary);">Create an account</a>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        const passwordInput = document.getElementById('password');
        const toggleBtn = document.querySelector('.toggle-password');

        if (toggleBtn && passwordInput) {
            toggleBtn.onclick = () => {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    toggleBtn.textContent = 'visibility_off';
                } else {
                    passwordInput.type = 'password';
                    toggleBtn.textContent = 'visibility';
                }
            };
        }

        const form = document.getElementById('login-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                await Auth.login(email, password);
                Utils.showToast('Access Granted', 'success');
                Router.navigate('/dashboard');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });
    }
}

export default new LoginView();
