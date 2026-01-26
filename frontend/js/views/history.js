import Auth from '../auth.js';
import Api from '../api.js';
import Utils from '../utils.js';
import Components from '../components.js';

class HistoryView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('history')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">Operation History</h1>
                    <div class="card glass fade-in">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                            <h3>Recent Scans</h3>
                            <button class="btn-outline" id="refresh-history" style="font-size: 0.8rem;">REFRESH</button>
                        </div>
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                                <thead>
                                    <tr style="border-bottom: 1px solid var(--border-color);">
                                        <th style="padding: 1rem;">Type</th><th style="padding: 1rem;">Target</th><th style="padding: 1rem;">Status</th><th style="padding: 1rem;">Date</th><th style="padding: 1rem;">Action</th>
                                    </tr>
                                </thead>
                                <tbody id="history-table-body">
                                    <tr><td colspan="5" style="padding: 2rem; text-align: center;">Loading history...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div id="result-modal" class="glass" style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80%; height: 80%; z-index: 1000; padding: 2rem; border-radius: 20px; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2 id="modal-title">Scan Result</h2><button class="btn-outline" id="close-modal">CLOSE</button>
                </div>
                <pre id="modal-content" style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; font-family: 'JetBrains Mono';"></pre>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        this.loadHistory();
        document.getElementById('refresh-history').addEventListener('click', () => this.loadHistory());
        document.getElementById('close-modal').addEventListener('click', () => { document.getElementById('result-modal').style.display = 'none'; });
    }

    async loadHistory() {
        try {
            const result = await Api.get('/scans/user/history');
            const tbody = document.getElementById('history-table-body');
            if (result && result.scans && result.scans.length > 0) {
                tbody.innerHTML = result.scans.map(scan => `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 1rem;"><span style="text-transform: capitalize;">${scan.scan_type}</span></td>
                        <td style="padding: 1rem;">${scan.target}</td>
                        <td style="padding: 1rem;"><span style="color: ${this.getStatusColor(scan.status)}">${scan.status}</span></td>
                        <td style="padding: 1rem; font-size: 0.8rem;">${Utils.parseDate(scan.created_at)}</td>
                        <td style="padding: 1rem;"><button class="btn-outline view-result-btn" data-id="${scan.id}" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">VIEW</button></td>
                    </tr>
                `).join('');
                document.querySelectorAll('.view-result-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const id = e.target.getAttribute('data-id');
                        try {
                            const scanData = await Api.get(`/scans/${id}`);
                            document.getElementById('modal-title').textContent = `${scanData.scan_type.toUpperCase()} Scan: ${scanData.target}`;
                            document.getElementById('modal-content').innerHTML = Utils.formatJSON(scanData.results);
                            document.getElementById('result-modal').style.display = 'block';
                        } catch (err) { Utils.showToast(err.message, 'error'); }
                    });
                });
            } else { tbody.innerHTML = '<tr><td colspan="5" style="padding: 2rem; text-align: center;">No history found.</td></tr>'; }
        } catch (error) { Utils.showToast('Failed to load history', 'error'); }
    }

    getStatusColor(status) {
        switch (status) {
            case 'completed': return 'var(--primary)';
            case 'failed': return 'var(--danger)';
            case 'running': return 'var(--secondary)';
            default: return 'var(--text-muted)';
        }
    }
}

export default new HistoryView();
