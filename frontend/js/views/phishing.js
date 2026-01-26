import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class PhishingView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('phishing')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                        <h1 class="page-title fade-in">Phishing Detector</h1>
                    </div>
                    
                    <div class="card glass fade-in" style="max-width: 900px; margin-bottom: 2rem;">
                        <form id="phishing-form" style="display: grid; grid-template-columns: 4fr 1fr; gap: 1rem; align-items: end;">
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.8rem;">TARGET URL</label>
                                <input type="text" id="phishing-target" required placeholder="https://suspicious-site.com/login" 
                                    style="width: 100%; padding: 0.8rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 4px; font-family: 'JetBrains Mono';">
                            </div>
                            <button type="submit" class="btn" id="phish-btn" style="height: 42px;">ANALYZE</button>
                        </form>
                    </div>

                    <!-- Results Container -->
                    <div id="phish-results" class="fade-in" style="display: none; max-width: 900px;">
                        <div id="phishing-report" class="card glass" style="padding: 0;">
                            
                            <!-- Header -->
                            <div style="padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2);">
                                <div>
                                    <div style="color: var(--text-muted); font-size: 0.8rem; letter-spacing: 1px;">ANALYZED URL</div>
                                    <div id="report-url" style="font-size: 1rem; font-weight: bold; color: var(--primary); word-break: break-all; font-family: 'JetBrains Mono';">Loading...</div>
                                </div>
                                <div id="verdict-badge" style="padding: 0.5rem 1.5rem; border-radius: 4px; font-weight: bold; font-size: 1.2rem;">--</div>
                            </div>

                            <!-- Radar Chart & Score Section -->
                            <div style="padding: 2rem; display: flex; gap: 2rem; align-items: center; justify-content: center; flex-wrap: wrap;">
                                <div style="width: 300px; height: 300px;">
                                    <canvas id="phish-radar-chart"></canvas>
                                </div>
                                <div style="text-align: center;">
                                    <div id="risk-score" style="font-size: 4rem; font-weight: bold; color: #00ff9d; text-shadow: 0 0 20px rgba(0,255,157,0.3);">0</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted); letter-spacing: 2px;">RISK SCORE</div>
                                    <div id="risk-level" style="margin-top: 0.5rem; font-size: 1rem; font-weight: bold;">LOW</div>
                                </div>
                            </div>

                            <!-- Indicators Section -->
                            <div style="padding: 1.5rem; border-top: 1px solid rgba(255,255,255,0.05);">
                                <h3 style="margin-bottom: 1rem; color: var(--secondary);">🔍 THREAT INDICATORS</h3>
                                <div id="indicators-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;"></div>
                            </div>

                            <!-- Additional Info -->
                            <div style="padding: 1.5rem; background: rgba(0,0,0,0.1); border-top: 1px solid rgba(255,255,255,0.05);">
                                <div id="extra-info" style="display: flex; gap: 2rem; flex-wrap: wrap;"></div>
                            </div>
                        </div>

                        <!-- Raw JSON Tab -->
                        <div style="margin-top: 1rem;">
                            <button onclick="toggleRawJSON()" class="btn-outline" style="font-size: 0.8rem;">Toggle Raw JSON</button>
                            <pre id="json-output" class="json-box" style="display: none; margin-top: 0.5rem;"></pre>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const form = document.getElementById('phishing-form');
        const btn = document.getElementById('phish-btn');
        const resultsArea = document.getElementById('phish-results');
        const jsonOutput = document.getElementById('json-output');

        window.toggleRawJSON = function () {
            jsonOutput.style.display = jsonOutput.style.display === 'none' ? 'block' : 'none';
        };

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const target = document.getElementById('phishing-target').value;

            btn.textContent = 'ANALYZING...';
            btn.disabled = true;
            resultsArea.style.display = 'none';

            try {
                const response = await Api.post('/security/phishing/check', { url: target });

                if (response) {
                    document.getElementById('report-url').textContent = target;
                    jsonOutput.innerHTML = Utils.formatJSON(response);

                    populatePhishingReport(response);

                    resultsArea.style.display = 'block';
                    Utils.showToast('Phishing Analysis Complete', 'success');
                }
            } catch (error) {
                Utils.showToast(error.message, 'error');
                console.error(error);
            } finally {
                btn.textContent = 'ANALYZE';
                btn.disabled = false;
            }
        });
    }
}

function populatePhishingReport(data) {
    const indicators = data.indicators || [];
    const riskScore = Math.round((data.risk_score || 0) * 100);
    const isPhishing = data.is_phishing || false;

    // Verdict Badge
    const verdictBadge = document.getElementById('verdict-badge');
    if (isPhishing) {
        verdictBadge.textContent = 'PHISHING DETECTED';
        verdictBadge.style.background = '#ff4757';
        verdictBadge.style.color = '#fff';
    } else if (riskScore > 50) {
        verdictBadge.textContent = 'SUSPICIOUS';
        verdictBadge.style.background = '#ffa502';
        verdictBadge.style.color = '#000';
    } else {
        verdictBadge.textContent = 'LIKELY SAFE';
        verdictBadge.style.background = '#00ff9d';
        verdictBadge.style.color = '#000';
    }

    // Risk Score
    const riskScoreEl = document.getElementById('risk-score');
    const riskLevelEl = document.getElementById('risk-level');
    riskScoreEl.textContent = riskScore;

    if (riskScore > 70) {
        riskScoreEl.style.color = '#ff4757';
        riskLevelEl.textContent = 'HIGH RISK';
    } else if (riskScore > 40) {
        riskScoreEl.style.color = '#ffa502';
        riskLevelEl.textContent = 'MEDIUM RISK';
    } else {
        riskScoreEl.style.color = '#00ff9d';
        riskLevelEl.textContent = 'LOW RISK';
    }

    // Indicators Grid
    const indicatorsGrid = document.getElementById('indicators-grid');
    indicatorsGrid.innerHTML = indicators.map(ind => `
        <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border-left: 3px solid ${ind.present ? '#ff4757' : '#00ff9d'}; opacity: ${ind.present ? 1 : 0.6}">
            <div style="font-weight: bold; color: ${ind.present ? '#ff4757' : '#00ff9d'}; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 1px;">
                ${ind.present ? '⚠️' : '✓'} ${ind.indicator.replace(/_/g, ' ')}
            </div>
            ${ind.details ? `<div style="color: #ccc; font-size: 0.8rem; margin-top: 0.5rem; font-family: 'JetBrains Mono'; line-height: 1.2;">${ind.details}</div>` :
            `<div style="color: #666; font-size: 0.75rem; margin-top: 0.25rem;">No threat detected</div>`}
        </div>
    `).join('');

    // Extra Info
    const age = data.domain_age_days;
    const ageDisplay = age !== null ? `${age} days (${Math.floor(age / 365)} years)` : '<span style="color: #666">WHOIS Private/Hidden</span>';

    const extraInfo = document.getElementById('extra-info');
    extraInfo.innerHTML = `
        <div style="flex: 1; min-width: 150px;"><label style="color: var(--text-muted); font-size: 0.7rem; letter-spacing: 1px;">SSL ENCRYPTION</label><br><strong style="color: ${data.ssl_valid ? 'var(--primary)' : '#ff4757'}">${data.ssl_valid ? 'ACTIVE' : 'NONE/INVALID'}</strong></div>
        <div style="flex: 1; min-width: 150px;"><label style="color: var(--text-muted); font-size: 0.7rem; letter-spacing: 1px;">DOMAIN AGE (EST)</label><br><strong>${ageDisplay}</strong></div>
        <div style="flex: 1; min-width: 150px;"><label style="color: var(--text-muted); font-size: 0.7rem; letter-spacing: 1px;">SCAN LATENCY</label><br><strong>${data.scan_duration_ms}ms</strong></div>
    `;

    // Radar Chart
    renderRadarChart(indicators);
}

function renderRadarChart(indicators) {
    const ctx = document.getElementById('phish-radar-chart').getContext('2d');
    if (window.myPhishRadar) window.myPhishRadar.destroy();

    // Map labels to better names
    const labelMap = {
        'suspicious_tld': 'TLD REPUTATION',
        'ip_in_url': 'IP ADDRESSING',
        'suspicious_keyword': 'IMPERSONATION',
        'long_url': 'URL COMPLEXITY',
        'shortened_url': 'OBFUSCATION',
        'non_standard_port': 'SERVICE PORT',
        'https_missing': 'TRANSPORT SEC'
    };

    const labels = indicators.map(i => labelMap[i.indicator] || i.indicator.toUpperCase());
    const scores = indicators.map(i => i.present ? 100 : 10); // Minimum 10 for visibility

    window.myPhishRadar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Threat Vector',
                data: scores,
                backgroundColor: 'rgba(255, 71, 87, 0.25)',
                borderColor: '#ff4757',
                pointBackgroundColor: scores.map(s => s > 50 ? '#ff4757' : '#00ff9d'),
                pointBorderColor: '#fff',
                borderWidth: 2,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255,255,255,0.1)' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    pointLabels: { color: '#aaa', font: { size: 10, weight: 'bold' } },
                    ticks: { display: false },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

export default new PhishingView();
