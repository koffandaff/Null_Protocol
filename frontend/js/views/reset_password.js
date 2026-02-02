import Auth from '../auth.js';
import Utils from '../utils.js';
import Router from '../router.js';

class ResetPasswordView {
    async render() {
        return `
            <div style="min-height: 100vh; display: flex; flex-direction: column; position: relative; overflow: hidden;">
                <!-- Animated Background -->
                <div class="hero-gradient" style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; animation: rotateGradient 20s linear infinite;"></div>
                <div style="position: absolute; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);"></div>

                <div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 2rem 0; position: relative; z-index: 1;">
                    <div class="card glass fade-in" style="width: 100%; max-width: 400px; padding: 3rem 2rem;">
                        <h2 class="page-title" style="text-align: center; margin-bottom: 0.5rem; font-size: 1.8rem;">Recovery Protocol</h2>
                        <p id="reset-description" style="text-align: center; color: var(--text-muted); margin-bottom: 2.5rem; font-size: 0.9rem;">Verify OTP to unlock credential update.</p>
                        
                        <!-- Step 1: OTP Verification -->
                        <form id="verify-form">
                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">EMAIL ADDRESS</label>
                                <input type="email" id="email" disabled style="background: rgba(0,0,0,0.3); opacity: 0.7; cursor: not-allowed;">
                            </div>

                            <div style="margin-bottom: 2rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">6-DIGIT OTP</label>
                                <input type="text" id="otp" required placeholder="000000" maxlength="6" style="background: rgba(0,0,0,0.3); letter-spacing: 5px; font-weight: bold; text-align: center; font-size: 1.2rem;">
                            </div>
                            
                            <button type="submit" class="btn" id="verify-btn" style="width: 100%; padding: 1rem; font-weight: bold; letter-spacing: 2px;">VERIFY IDENTITY</button>
                        </form>

                        <!-- Step 2: Password Reset (Hidden by default) -->
                        <form id="reset-form" style="display: none;" class="fade-in">
                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">NEW PASSWORD</label>
                                <div style="position: relative; display: flex; align-items: center;">
                                    <input type="password" id="new-password" required placeholder="••••••••" style="width: 100%; padding-right: 40px; background: rgba(0,0,0,0.3);">
                                    <span class="material-symbols-outlined toggle-password" data-target="new-password" style="position: absolute; right: 10px; cursor: pointer; color: var(--text-muted); user-select: none;">visibility</span>
                                </div>
                            </div>

                            <div style="margin-bottom: 2rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">CONFIRM PASSWORD</label>
                                <input type="password" id="confirm-password" required placeholder="••••••••" style="background: rgba(0,0,0,0.3);">
                            </div>
                            
                            <button type="submit" class="btn" style="width: 100%; padding: 1rem; font-weight: bold; letter-spacing: 2px;">RESET PASSWORD</button>
                        </form>
                    </div>
                </div>
            </div>
            <style>
                @keyframes rotateGradient {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    async afterRender() {
        const urlParams = new URLSearchParams(window.location.hash.split('?')[1]);
        const email = urlParams.get('email');

        if (!email) {
            Utils.showToast('Session expired. Restarting recovery.', 'warning');
            setTimeout(() => Router.navigate('/forgot-password'), 2000);
            return;
        }

        document.getElementById('email').value = email;
        const verifyForm = document.getElementById('verify-form');
        const resetForm = document.getElementById('reset-form');
        const description = document.getElementById('reset-description');

        let verifiedOtp = '';

        // Verification Step
        verifyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const otp = document.getElementById('otp').value;
            const btn = document.getElementById('verify-btn');

            try {
                btn.disabled = true;
                btn.innerHTML = '<span class="material-symbols-outlined spin">sync</span> VERIFYING...';

                await Auth.verifyOtp(email, otp);

                verifiedOtp = otp;
                Utils.showToast('OTP Verified. Set your new password.', 'success');

                // Switch UI
                verifyForm.style.display = 'none';
                resetForm.style.display = 'block';
                description.textContent = 'Identity confirmed. Enter new credentials.';

            } catch (error) {
                Utils.showToast(error.message || 'Verification failed', 'error');
                btn.disabled = false;
                btn.textContent = 'VERIFY IDENTITY';
            }
        });

        // Reset Step
        resetForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (newPassword !== confirmPassword) {
                Utils.showToast('Passwords do not match', 'warning');
                return;
            }

            const btn = resetForm.querySelector('button');

            try {
                btn.disabled = true;
                btn.innerHTML = '<span class="material-symbols-outlined spin">sync</span> UPDATING...';

                await Auth.resetPassword(email, verifiedOtp, newPassword);

                Utils.showToast('Security updated successfully.', 'success');
                setTimeout(() => Router.navigate('/login'), 2000);
            } catch (error) {
                Utils.showToast(error.message || 'Failed to update credentials', 'error');
                btn.disabled = false;
                btn.textContent = 'RESET PASSWORD';
            }
        });

        // Toggles
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.onclick = () => {
                const input = document.getElementById(btn.dataset.target);
                input.type = input.type === 'password' ? 'text' : 'password';
                btn.textContent = input.type === 'password' ? 'visibility' : 'visibility_off';
            };
        });
    }
}

export default new ResetPasswordView();
