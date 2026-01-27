import Auth from '../auth.js';
import Api from '../api.js';
import Utils from '../utils.js';
import Components from '../components.js';

class ProfileView {
    async render() {
        const user = JSON.parse(localStorage.getItem('user')) || {};
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar()}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">User Profile</h1>
                    
                    <div class="card glass fade-in" style="max-width: 600px;">
                        <form id="profile-form">
                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem;">Username</label>
                                <input type="text" id="username" value="${user.username}" disabled style="opacity: 0.7;">
                            </div>
                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem;">Email</label>
                                <input type="email" id="email" value="${user.email}" disabled style="opacity: 0.7;">
                            </div>
                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem;">Full Name</label>
                                <input type="text" id="full_name" value="${user.full_name || ''}">
                            </div>
                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem;">Bio</label>
                                <textarea id="bio" rows="4">${user.bio || ''}</textarea>
                            </div>
                            <button type="submit" class="btn">UPDATE PROFILE</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const form = document.getElementById('profile-form');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('full_name').value;
            const bio = document.getElementById('bio').value;

            // Mock update for now as backend doesn't support profile update yet
            // In a real app, we would PUT /user/me
            const user = JSON.parse(localStorage.getItem('user'));
            user.full_name = fullName;
            user.bio = bio;
            localStorage.setItem('user', JSON.stringify(user));

            Utils.showToast('Profile Updated (Local)', 'success');
        });
    }
}

export default new ProfileView();
