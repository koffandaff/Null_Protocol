import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class VpnView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('vpn')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">VPN Configuration</h1>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                        <div class="card glass fade-in">
                            <h3 style="margin-bottom: 1.5rem;">Generate Config</h3>
                            <div style="margin-bottom: 1.5rem;">
                                <button class="btn" id="tab-openvpn" style="margin-right: 0.5rem;">OpenVPN</button>
                                <button class="btn-outline" id="tab-wireguard">WireGuard</button>
                            </div>
                            <form id="vpn-form">
                                <input type="hidden" id="vpn-type" value="openvpn">
                                <div id="openvpn-fields">
                                    <div style="margin-bottom: 1rem;"><label>Server Address</label><input type="text" id="server-addr" placeholder="vpn.example.com"></div>
                                    <div style="margin-bottom: 1rem;"><label>Port</label><input type="number" id="port" value="1194"></div>
                                    <div style="margin-bottom: 1rem;"><label>Protocol</label><select id="protocol"><option value="udp">UDP</option><option value="tcp">TCP</option></select></div>
                                </div>
                                <div id="wireguard-fields" style="display: none;">
                                    <div style="margin-bottom: 1rem;"><label>Server Public Key</label><input type="text" id="server-pubkey" placeholder="Base64 Key"></div>
                                    <div style="margin-bottom: 1rem;"><label>Server Endpoint</label><input type="text" id="server-endpoint" placeholder="vpn.example.com:51820"></div>
                                </div>
                                <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;">GENERATE CONFIG</button>
                            </form>
                        </div>
                        <div class="card glass fade-in" style="animation-delay: 0.1s;">
                            <h3 style="margin-bottom: 1.5rem;">My Configurations</h3>
                            <div id="config-list" style="display: flex; flex-direction: column; gap: 1rem;">
                                <p style="color: var(--text-muted); text-align: center;">Loading configs...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const form = document.getElementById('vpn-form');
        const typeInput = document.getElementById('vpn-type');
        const openvpnFields = document.getElementById('openvpn-fields');
        const wireguardFields = document.getElementById('wireguard-fields');
        const tabOpenvpn = document.getElementById('tab-openvpn');
        const tabWireguard = document.getElementById('tab-wireguard');

        tabOpenvpn.addEventListener('click', () => {
            typeInput.value = 'openvpn';
            openvpnFields.style.display = 'block';
            wireguardFields.style.display = 'none';
            tabOpenvpn.className = 'btn';
            tabWireguard.className = 'btn-outline';
        });

        tabWireguard.addEventListener('click', () => {
            typeInput.value = 'wireguard';
            openvpnFields.style.display = 'none';
            wireguardFields.style.display = 'block';
            tabOpenvpn.className = 'btn-outline';
            tabWireguard.className = 'btn';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const type = typeInput.value;
            let body = {};
            let endpoint = '';
            if (type === 'openvpn') {
                body = { server_address: document.getElementById('server-addr').value, port: parseInt(document.getElementById('port').value), protocol: document.getElementById('protocol').value };
                endpoint = '/vpn/openvpn';
            } else {
                body = { server_public_key: document.getElementById('server-pubkey').value, server_endpoint: document.getElementById('server-endpoint').value };
                endpoint = '/vpn/wireguard';
            }
            try {
                await Api.post(endpoint, body);
                Utils.showToast('Config Generated', 'success');
                this.loadConfigs();
            } catch (error) { Utils.showToast(error.message, 'error'); }
        });
        this.loadConfigs();
    }

    async loadConfigs() {
        try {
            const configs = await Api.get('/vpn/configs');
            const list = document.getElementById('config-list');
            if (configs && configs.length > 0) {
                list.innerHTML = configs.map(cfg => `
                    <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div><div style="font-weight: 600;">${cfg.name}</div><div style="font-size: 0.8rem; color: var(--text-muted);">${cfg.type.toUpperCase()} • ${Utils.parseDate(cfg.created_at)}</div></div>
                        <button class="btn-outline" style="font-size: 0.8rem; padding: 0.25rem 0.75rem;">VIEW</button>
                    </div>
                `).join('');
            } else {
                list.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No configurations found.</p>';
            }
        } catch (e) { console.error(e); }
    }
}

export default new VpnView();
