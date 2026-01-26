import Auth from '../auth.js';
import Utils from '../utils.js';
import Router from '../router.js';

class SignupView {
    async render() {
        return `
            <div class="container" style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                <div class="card glass fade-in" style="width: 100%; max-width: 400px;">
                    <h2 class="page-title" style="text-align: center;">Join Fsociety</h2>
                    <p style="text-align: center; color: var(--text-muted); margin-bottom: 2rem;">Initialize your connection.</p>
                    
                    <form id="signup-form">
                        <div style="margin-bottom: 1rem;">
                            <label>Username</label>
                            <input type="text" id="username" required placeholder="elliot_alderson">
                        </div>

                        <div style="margin-bottom: 1rem;">
                            <label>Email</label>
                            <input type="email" id="email" required placeholder="fsociety@protonmail.com">
                        </div>

                        <div style="margin-bottom: 1rem;">
                            <label>Full Name</label>
                            <input type="text" id="full_name" placeholder="Optional">
                        </div>
                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; margin-bottom: 0.5rem;">Password</label>
                            <div style="position: relative; display: flex; align-items: center;">
                                <input type="password" id="password" required placeholder="••••••••" style="width: 100%; padding-right: 40px;">
                                <span class="material-symbols-outlined toggle-password" style="position: absolute; right: 10px; cursor: pointer; color: var(--text-muted); user-select: none; z-index: 10;">visibility</span>
                            </div>
                            
                            <!-- Detailed Strength Meter -->
                            <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.8rem; color: var(--text-muted);">
                                <div id="req-len" class="req-item"><span class="icon">○</span> 8+ Characters</div>
                                <div id="req-num" class="req-item"><span class="icon">○</span> Number (0-9)</div>
                                <div id="req-cap" class="req-item"><span class="icon">○</span> Uppercase (A-Z)</div>
                                <div id="req-sym" class="req-item"><span class="icon">○</span> Symbol (!@#$)</div>
                            </div>
                        </div>

                        <div style="margin-bottom: 2rem;">
                            <label style="display: block; margin-bottom: 0.5rem;">Confirm Password</label>
                            <input type="password" id="confirm-password" required placeholder="••••••••">
                        </div>
                        
                        <button type="submit" class="btn" style="width: 100%;">INITIALIZE USER</button>
                    </form>

                    <div style="margin-top: 1.5rem; text-align: center;">
                        <a href="#/login" style="color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary);">Already initialized? Login</a>
                    </div>
                </div>
            </div>
            <style>
                .req-item { display: flex; align-items: center; gap: 0.5rem; transition: all 0.3s; }
                .req-item.valid { color: var(--primary); }
                .req-item.valid .icon { content: '✓'; }
            </style>
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

        // Strength checker needs to be global or attached to input
        passwordInput.addEventListener('keyup', () => {
            const password = passwordInput.value;
            const updateReq = (id, valid) => {
                const el = document.getElementById(id);
                if (valid) {
                    el.classList.add('valid');
                    el.querySelector('.icon').textContent = '✓';
                } else {
                    el.classList.remove('valid');
                    el.querySelector('.icon').textContent = '○';
                }
            };

            updateReq('req-len', password.length >= 8);
            updateReq('req-num', /[0-9]/.test(password));
            updateReq('req-cap', /[A-Z]/.test(password));
            updateReq('req-sym', /[^a-zA-Z0-9]/.test(password));
        });

        const form = document.getElementById('signup-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userData = {
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                full_name: document.getElementById('full_name').value,
                password: document.getElementById('password').value
            };

            try {
                await Auth.signup(userData);
                Utils.showToast('Account Created. Please Login.', 'success');
                Router.navigate('/login');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });
    }
}

export default new SignupView();
