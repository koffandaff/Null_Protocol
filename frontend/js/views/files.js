import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class FileView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('files')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">Malware & File Analysis</h1>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                        <div class="card glass fade-in">
                            <h3>Hash Check</h3>
                            <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Check file hashes against databases.</p>
                            <form id="hash-form">
                                <div style="margin-bottom: 1rem;">
                                    <label>File Hash</label>
                                    <input type="text" id="file-hash" required placeholder="MD5/SHA1/SHA256">
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <label>Analysis Source</label>
                                    <select id="hash-source">
                                        <option value="hash/check">Internal Database</option>
                                        <option value="virustotal/check">VirusTotal</option>
                                    </select>
                                </div>
                                <button type="submit" class="btn" style="width: 100%;">CHECK HASH</button>
                            </form>
                        </div>

                        <div class="card glass fade-in" style="animation-delay: 0.1s;">
                            <h3>Upload Analysis</h3>
                            <form id="upload-form">
                                <div style="margin-bottom: 1rem;">
                                    <label>Select File</label>
                                    <input type="file" id="file-input" required>
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <label>Description</label>
                                    <input type="text" id="file-desc" placeholder="Optional">
                                </div>
                                <button type="submit" class="btn btn-outline" style="width: 100%;">UPLOAD & ANALYZE</button>
                            </form>
                        </div>
                    </div>

                    <div id="file-results" class="card glass fade-in" style="display: none; margin-top: 2rem;">
                        <h3 style="margin-bottom: 1rem; color: var(--secondary);">Analysis Results</h3>
                        <pre id="file-output" style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: 'JetBrains Mono'; font-size: 0.9rem;"></pre>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const hashForm = document.getElementById('hash-form');
        const uploadForm = document.getElementById('upload-form');
        const resultsArea = document.getElementById('file-results');
        const output = document.getElementById('file-output');

        hashForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const hash = document.getElementById('file-hash').value;
            const source = document.getElementById('hash-source').value;
            try {
                const response = await Api.post(`/files/${source}`, { hash });
                output.innerHTML = Utils.formatJSON(response);
                resultsArea.style.display = 'block';
                Utils.showToast('Hash scan completed', 'success');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });

        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('file-input');
            const desc = document.getElementById('file-desc').value;
            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`http://localhost:8000/api/files/upload/analyze?description=${encodeURIComponent(desc)}`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'Upload failed');

                output.innerHTML = Utils.formatJSON(data);
                resultsArea.style.display = 'block';
                Utils.showToast('File analyzed', 'success');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });
    }
}

export default new FileView();
