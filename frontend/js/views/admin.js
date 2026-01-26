import Auth from '../auth.js';
import Api from '../api.js';
import Utils from '../utils.js';
import Components from '../components.js';

class AdminView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('admin')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">System Administration</h1>
                    <div class="card glass fade-in">
                        <h3>User Database</h3>
                        <div style="margin-top: 1rem; overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                                <thead>
                                    <tr style="border-bottom: 1px solid var(--border-color);">
                                        <th style="padding: 1rem;">ID</th><th style="padding: 1rem;">Username</th><th style="padding: 1rem;">Email</th><th style="padding: 1rem;">Role</th><th style="padding: 1rem;">Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="users-table-body">
                                    <tr><td colspan="5" style="padding: 1rem; text-align: center;">Loading users...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        try {
            const users = await Api.get('/admin/users');
            const tbody = document.getElementById('users-table-body');
            if (users && users.length > 0) {
                tbody.innerHTML = users.map(user => `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 1rem; font-family: 'JetBrains Mono'; font-size: 0.8rem;">${user.id.substring(0, 8)}...</td>
                        <td style="padding: 1rem;">${user.username}</td>
                        <td style="padding: 1rem;">${user.email}</td>
                        <td style="padding: 1rem;"><span style="color: ${user.role === 'admin' ? 'var(--secondary)' : 'var(--primary)'}">${user.role}</span></td>
                        <td style="padding: 1rem;"><button class="btn-outline delete-btn" data-id="${user.id}" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; border-color: var(--danger); color: var(--danger);">DELETE</button></td>
                    </tr>
                `).join('');
                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const userId = e.target.getAttribute('data-id');
                        if (confirm('Delete this user?')) {
                            try { await Api.delete(`/admin/users/${userId}`); Utils.showToast('User deleted', 'success'); this.afterRender(); }
                            catch (err) { Utils.showToast(err.message, 'error'); }
                        }
                    });
                });
            } else { tbody.innerHTML = '<tr><td colspan="5" style="padding: 1rem; text-align: center;">No users found.</td></tr>'; }
        } catch (error) { Utils.showToast('Failed to load users', 'error'); }
    }
}

export default new AdminView();
