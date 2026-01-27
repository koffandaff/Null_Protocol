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
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; max-width: 1000px;">
                        <!-- Hash Check Card -->
                        <div class="card glass fade-in">
                            <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: var(--primary);">fingerprint</span>
                                Hash Check
                            </h3>
                            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;">Check file hashes against malware databases including VirusTotal.</p>
                            <form id="hash-form">
                                <div style="margin-bottom: 1rem;">
                                    <label>File Hash</label>
                                    <input type="text" id="file-hash" required>
                                </div>
                                <div style="margin-bottom: 1rem;">
                                    <label>Hash Type</label>
                                    <select id="hash-type">
                                        <option value="sha256">SHA-256</option>
                                        <option value="sha1">SHA-1</option>
                                        <option value="md5">MD5</option>
                                    </select>
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                                        <input type="checkbox" id="use-virustotal" checked>
                                        <span>Use VirusTotal API</span>
                                    </label>
                                </div>
                                <button type="submit" class="btn" style="width: 100%;">ANALYZE HASH</button>
                            </form>
                        </div>

                        <!-- Upload Analysis Card -->
                        <div class="card glass fade-in" style="animation-delay: 0.1s;">
                            <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: var(--secondary);">upload_file</span>
                                Upload Analysis
                            </h3>
                            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;">Upload a file for deep static analysis and malware detection.</p>
                            <form id="upload-form">
                                <div style="margin-bottom: 1rem;">
                                    <label>Select File</label>
                                    <input type="file" id="file-input" required>
                                </div>
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                                        <input type="checkbox" id="upload-virustotal" checked>
                                        <span>Cross-reference with VirusTotal</span>
                                    </label>
                                </div>
                                <button type="submit" class="btn btn-outline" style="width: 100%;">UPLOAD & ANALYZE</button>
                            </form>
                        </div>
                    </div>

                    <!-- Results Section -->
                    <div id="file-results" class="card glass fade-in" style="display: none; margin-top: 2rem; max-width: 1000px; padding: 0;">
                        
                        <!-- Results Header -->
                        <div style="padding: 1.5rem; background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="margin: 0; color: var(--secondary); font-family: 'JetBrains Mono';">ANALYSIS REPORT</h3>
                                <div id="result-filename" style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;"></div>
                            </div>
                            <div id="result-verdict" style="padding: 0.5rem 1rem; border-radius: 4px; font-weight: bold; font-size: 0.85rem;"></div>
                        </div>

                        <!-- Tabs -->
                        <div class="tabs" style="display: flex; gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <button class="tab-btn active" data-tab="visual">VISUAL</button>
                            <button class="tab-btn" data-tab="details">DETAILS</button>
                            <button class="tab-btn" data-tab="raw">RAW JSON</button>
                        </div>

                        <!-- Tab: Visual -->
                        <div id="tab-visual" class="tab-content" style="display: block; padding: 1.5rem;">
                            <!-- Scorecards -->
                            <div id="scorecards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem;"></div>
                            
                            <!-- Charts Row -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                                    <h4 style="margin: 0 0 1rem 0; color: var(--primary); font-size: 0.85rem; letter-spacing: 1px;">THREAT PROFILE</h4>
                                    <div style="height: 250px;">
                                        <canvas id="radar-chart"></canvas>
                                    </div>
                                </div>
                                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                                    <h4 style="margin: 0 0 1rem 0; color: var(--secondary); font-size: 0.85rem; letter-spacing: 1px;">DETECTION BREAKDOWN</h4>
                                    <div style="height: 250px;">
                                        <canvas id="doughnut-chart"></canvas>
                                    </div>
                                </div>
                            </div>

                            <!-- Warnings -->
                            <div id="warnings-section" style="margin-top: 2rem; display: none;">
                                <h4 style="color: #ff4757; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">warning</span> WARNINGS
                                </h4>
                                <ul id="warnings-list" style="list-style: none; padding: 0;"></ul>
                            </div>

                            <!-- Recommendations -->
                            <div id="recommendations-section" style="margin-top: 2rem; display: none;">
                                <h4 style="color: var(--primary); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">lightbulb</span> RECOMMENDATIONS
                                </h4>
                                <ul id="recommendations-list" style="list-style: none; padding: 0;"></ul>
                            </div>
                        </div>

                        <!-- Tab: Details -->
                        <div id="tab-details" class="tab-content" style="display: none; padding: 1.5rem;">
                            <div id="details-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;"></div>
                        </div>

                        <!-- Tab: Raw JSON -->
                        <div id="tab-raw" class="tab-content" style="display: none; padding: 1.5rem;">
                            <pre id="file-output" style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: 'JetBrains Mono'; font-size: 0.8rem; max-height: 500px;"></pre>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const hashForm = document.getElementById('hash-form');
        const uploadForm = document.getElementById('upload-form');

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
                btn.classList.add('active');
                document.getElementById(`tab-${btn.dataset.tab}`).style.display = 'block';
            };
        });

        // Hash Check
        hashForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const hash = document.getElementById('file-hash').value.trim();
            const hashType = document.getElementById('hash-type').value;
            const useVT = document.getElementById('use-virustotal').checked;

            try {
                Utils.showToast('Analyzing hash...', 'info');

                // First check local database
                const localResponse = await Api.post('/files/hash/check', { hash, hash_type: hashType });

                // If VirusTotal enabled, also query VT
                let vtResponse = null;
                if (useVT) {
                    try {
                        vtResponse = await Api.post('/files/virustotal/check', { hash });
                    } catch (vtError) {
                        console.warn('VirusTotal check failed:', vtError);
                    }
                }

                // Merge results
                const mergedResult = this.mergeHashResults(localResponse, vtResponse);
                this.displayResults(mergedResult, 'hash');
                Utils.showToast('Hash analysis complete', 'success');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });

        // File Upload
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('file-input');
            const useVT = document.getElementById('upload-virustotal').checked;
            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                Utils.showToast('Analyzing file...', 'info');
                const token = localStorage.getItem('access_token');
                const response = await fetch(`http://localhost:8000/api/files/upload/analyze?use_virustotal=${useVT}`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'Upload failed');

                this.displayResults(data, 'file');
                Utils.showToast('File analysis complete', 'success');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });
    }

    mergeHashResults(localResult, vtResult) {
        const merged = { ...localResult };

        if (vtResult) {
            merged.virustotal = {
                positives: vtResult.positives || 0,
                total: vtResult.total || 0,
                permalink: vtResult.permalink,
                scan_date: vtResult.scan_date,
                scans: vtResult.scans
            };

            // If VT found detections, update risk level
            if (vtResult.positives > 0) {
                merged.reputation.known_malicious = true;
                merged.reputation.detection_count = Math.max(merged.reputation.detection_count, vtResult.positives);
                merged.risk_level = vtResult.positives > 10 ? 'critical' : 'high';
            }
        }

        return merged;
    }

    displayResults(data, type) {
        const resultsArea = document.getElementById('file-results');
        const output = document.getElementById('file-output');
        const filenameEl = document.getElementById('result-filename');
        const verdictEl = document.getElementById('result-verdict');

        // Show filename or hash
        filenameEl.textContent = type === 'file'
            ? `${data.filename} (${this.formatBytes(data.file_size)})`
            : `Hash: ${data.hash?.substring(0, 16)}...`;

        // Show verdict
        const riskLevel = data.risk_level || 'info';
        const verdictColors = {
            'critical': { bg: '#ff4757', text: 'CRITICAL THREAT' },
            'high': { bg: '#ff6b6b', text: 'HIGH RISK' },
            'medium': { bg: '#ffa502', text: 'MEDIUM RISK' },
            'low': { bg: '#2ed573', text: 'LOW RISK' },
            'info': { bg: '#3498db', text: 'UNKNOWN' }
        };
        const verdict = verdictColors[riskLevel] || verdictColors.info;
        verdictEl.style.background = verdict.bg;
        verdictEl.style.color = '#fff';
        verdictEl.textContent = verdict.text;

        // Raw JSON
        output.innerHTML = Utils.formatJSON(data);

        // Scorecards
        this.renderScorecards(data, type);

        // Charts
        this.renderCharts(data, type);

        // Warnings
        this.renderWarnings(data.warnings || []);

        // Recommendations
        this.renderRecommendations(data.recommendations || []);

        // Details
        this.renderDetails(data, type);

        resultsArea.style.display = 'block';
    }

    renderScorecards(data, type) {
        const container = document.getElementById('scorecards');
        const cards = [];

        if (type === 'file') {
            cards.push(
                { label: 'ENTROPY', value: data.entropy?.toFixed(2) || '--', color: data.entropy > 7.5 ? '#ff4757' : 'var(--primary)' },
                { label: 'FILE SIZE', value: this.formatBytes(data.file_size), color: 'var(--secondary)' },
                { label: 'MIME TYPE', value: data.mime_type?.split('/')[1]?.toUpperCase() || '--', color: '#ffa502' },
                { label: 'STRINGS', value: data.strings_found?.length || 0, color: '#3498db' }
            );
        }

        // Common cards
        const detections = data.virustotal?.positives || data.reputation?.detection_count || 0;
        const total = data.virustotal?.total || 70;
        cards.push(
            { label: 'DETECTIONS', value: `${detections}/${total}`, color: detections > 0 ? '#ff4757' : '#2ed573' },
            { label: 'CONFIDENCE', value: `${Math.round((data.confidence || 0) * 100)}%`, color: 'var(--primary)' }
        );

        container.innerHTML = cards.map(card => `
            <div class="glass" style="padding: 1rem; border-radius: 8px; text-align: center; border-left: 3px solid ${card.color};">
                <div style="font-size: 1.5rem; font-weight: bold; color: ${card.color}; font-family: 'JetBrains Mono';">${card.value}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1px; margin-top: 0.3rem;">${card.label}</div>
            </div>
        `).join('');
    }

    renderCharts(data, type) {
        // Destroy existing charts
        if (window.fileRadarChart) window.fileRadarChart.destroy();
        if (window.fileDoughnutChart) window.fileDoughnutChart.destroy();

        // Radar Chart - Threat Profile
        const radarCtx = document.getElementById('radar-chart').getContext('2d');
        const threatFactors = this.calculateThreatFactors(data, type);

        window.fileRadarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Malware Match', 'Entropy', 'Executable', 'Macros', 'Encryption', 'VT Detections'],
                datasets: [{
                    label: 'Threat Level',
                    data: threatFactors,
                    backgroundColor: 'rgba(255, 71, 87, 0.3)',
                    borderColor: '#ff4757',
                    pointBackgroundColor: '#ff4757',
                    pointBorderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { display: false },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        angleLines: { color: 'rgba(255,255,255,0.1)' },
                        pointLabels: { color: '#a0a0a0', font: { size: 10 } }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });

        // Doughnut Chart - Detection Breakdown
        const doughnutCtx = document.getElementById('doughnut-chart').getContext('2d');
        const vtPositives = data.virustotal?.positives || 0;
        const vtTotal = data.virustotal?.total || 70;
        const vtClean = vtTotal - vtPositives;

        window.fileDoughnutChart = new Chart(doughnutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Detected', 'Clean', 'Unknown'],
                datasets: [{
                    data: [vtPositives, vtClean, vtTotal === 0 ? 70 : 0],
                    backgroundColor: ['#ff4757', '#2ed573', '#3498db'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#a0a0a0', padding: 15 } }
                }
            }
        });
    }

    calculateThreatFactors(data, type) {
        const factors = [];

        // Malware Match (0-100)
        factors.push(data.reputation?.known_malicious ? 100 : (data.reputation?.known_clean ? 0 : 30));

        // Entropy (0-100, high = bad)
        const entropy = data.entropy || 0;
        factors.push(Math.min(100, (entropy / 8) * 100));

        // Executable
        factors.push(data.is_executable ? 80 : 0);

        // Macros
        factors.push(data.contains_macros ? 90 : 0);

        // Encryption
        factors.push(data.is_encrypted ? 60 : 0);

        // VT Detections
        const vtRatio = data.virustotal ? (data.virustotal.positives / Math.max(1, data.virustotal.total)) * 100 : 0;
        factors.push(vtRatio);

        return factors;
    }

    renderWarnings(warnings) {
        const section = document.getElementById('warnings-section');
        const list = document.getElementById('warnings-list');

        if (warnings.length === 0) {
            section.style.display = 'none';
            return;
        }

        section.style.display = 'block';
        list.innerHTML = warnings.map(w => `
            <li style="padding: 0.8rem; background: rgba(255, 71, 87, 0.1); border-left: 3px solid #ff4757; margin-bottom: 0.5rem; border-radius: 4px;">
                ${w}
            </li>
        `).join('');
    }

    renderRecommendations(recommendations) {
        const section = document.getElementById('recommendations-section');
        const list = document.getElementById('recommendations-list');

        if (recommendations.length === 0) {
            section.style.display = 'none';
            return;
        }

        section.style.display = 'block';
        list.innerHTML = recommendations.map(r => `
            <li style="padding: 0.8rem; background: rgba(0, 255, 157, 0.05); border-left: 3px solid var(--primary); margin-bottom: 0.5rem; border-radius: 4px;">
                ${r}
            </li>
        `).join('');
    }

    renderDetails(data, type) {
        const grid = document.getElementById('details-grid');
        const sections = [];

        // File Info Section
        if (type === 'file') {
            sections.push(`
                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                    <h4 style="color: var(--primary); margin-bottom: 1rem; font-size: 0.85rem;">FILE INFORMATION</h4>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">
                        <div style="margin-bottom: 0.5rem;"><strong>Filename:</strong> ${data.filename}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Size:</strong> ${this.formatBytes(data.file_size)}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>MIME Type:</strong> ${data.mime_type}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Magic Bytes:</strong> ${data.magic_bytes}</div>
                    </div>
                </div>
            `);
        }

        // Hash Section
        sections.push(`
            <div class="glass" style="padding: 1rem; border-radius: 8px;">
                <h4 style="color: var(--secondary); margin-bottom: 1rem; font-size: 0.85rem;">HASH SIGNATURES</h4>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.75rem; word-break: break-all;">
                    <div style="margin-bottom: 0.5rem;"><strong>MD5:</strong> ${data.hash_md5 || data.hash || '--'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>SHA1:</strong> ${data.hash_sha1 || '--'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>SHA256:</strong> ${data.hash_sha256 || data.hash || '--'}</div>
                </div>
            </div>
        `);

        // Reputation Section
        sections.push(`
            <div class="glass" style="padding: 1rem; border-radius: 8px;">
                <h4 style="color: #ffa502; margin-bottom: 1rem; font-size: 0.85rem;">REPUTATION</h4>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">
                    <div style="margin-bottom: 0.5rem;"><strong>Known Malicious:</strong> ${data.reputation?.known_malicious ? '⚠️ YES' : '✅ NO'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>Detection Names:</strong> ${data.reputation?.detection_names?.join(', ') || 'None'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>Tags:</strong> ${data.reputation?.tags?.join(', ') || 'None'}</div>
                </div>
            </div>
        `);

        // VirusTotal Section
        if (data.virustotal) {
            sections.push(`
                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                    <h4 style="color: #3498db; margin-bottom: 1rem; font-size: 0.85rem;">VIRUSTOTAL</h4>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">
                        <div style="margin-bottom: 0.5rem;"><strong>Detections:</strong> ${data.virustotal.positives}/${data.virustotal.total}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Scan Date:</strong> ${data.virustotal.scan_date || 'N/A'}</div>
                        <div style="margin-bottom: 0.5rem;"><a href="${data.virustotal.permalink}" target="_blank" style="color: var(--primary);">View Full Report →</a></div>
                    </div>
                </div>
            `);
        }

        grid.innerHTML = sections.join('');
    }

    formatBytes(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
    }
}

export default new FileView();
