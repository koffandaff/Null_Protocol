# 🛡️ OpenVPN Configuration Decoder & Tester

Fsociety's VPN module includes an advanced **Config Analyzer** that audits `.ovpn` files for security weaknesses, misconfigurations, and potential leak vectors.

## 📄 Anatomy of a Secure VPN Config

A standard OpenVPN (`.ovpn`) file is composed of several blocks. Here is what Fsociety looks for during a scan:

### 1. Connection Parameters
*   **`client`**: Tells OpenVPN to act as a client, not a server.
*   **`dev tun`**: Establishes a virtual tunnel (Layer 3). `tap` is used for bridging (Layer 2) but is less common for privacy.
*   **`proto udp`**: UDP is faster and harder to detect than TCP. Fsociety flags TCP usage as a performance alert.
*   **`remote [IP/Domain] [Port]`**: The destination server.

### 2. Security & Encryption
*   **`cipher AES-256-GCM`**: The gold standard. Fsociety will warn if `BF-CBC` (Blowfish) or `AES-128-CBC` is used.
*   **`auth SHA512`**: HMAC authentication for data integrity.
*   **`tls-auth ta.key 0`**: Provides an additional layer of HMAC signature to SSL/TLS handshake (prevents DoS).

### 3. Leak Prevention (Critical)
*   **`block-outside-dns`**: Prevents Windows from leaking DNS requests outside the tunnel. **Fsociety scores this highly.**
*   **`redirect-gateway def1`**: Forces all traffic through the VPN.

---

## 🧪 Testing the Analyzer

You can test Fsociety's VPN auditer without having a real VPN server. Use these test cases in the **VPN Tools** section.

### Test Case A: The "Weak" Config (Medium/High Risk)
Use this content to see Fsociety trigger security warnings:
```bash
client
dev tun
proto tcp
remote 1.2.3.4 1194
cipher BF-CBC
auth MD5
verb 3
```
**Expected Findings:**
- ⚠️ **Weak Cipher**: Blowfish (BF-CBC) is deprecated.
- ⚠️ **Weak Auth**: MD5 is cryptographically broken.
- ℹ️ **Performance**: TCP detected instead of UDP.

### Test Case B: The "Hardened" Config (Low Risk)
```bash
client
dev tun
proto udp
remote vpn.fsociety.com 443
cipher AES-256-GCM
auth SHA512
tls-version-min 1.2
block-outside-dns
redirect-gateway def1
<ca>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</ca>
```
**Expected Findings:**
- ✅ **GCM Encryption**: Modern and efficient.
- ✅ **Leak Protection**: DNS blocking detected.
- ✅ **Perfect Forward Secrecy**: Minimum TLS 1.2 enforced.

---

## 🔄 Technical Flow

1.  **Parsing**: The backend `VPN_Service` strips comments and identifies keywords.
2.  **Signature Matching**: We compare the config against a database of "Insecure Directives" (e.g., `comp-lzo` which is vulnerable to VORACLE attacks).
3.  **Risk Synthesis**: A final score is calculated based on:
    *   Encryption Strength (40%)
    *   Leak Prevention (40%)
    *   Protocol Optimization (20%)

---

## 🌎 Fsociety VPN Service Access

In addition to auditing existing configs, Fsociety now provides **On-Demand VPN Provisioning**. 

### How it works:
1.  **Select Node**: Choose from our global network of high-speed exit nodes (New York, Frankfurt, Tokyo, Mumbai).
2.  **Generate & Download**: Our backend dynamically generates a specialized `.ovpn` profile for your user account.
3.  **Cross-Platform Usage**: 
    - **Laptops (Windows/Mac/Linux)**: Download the `.ovpn` file and import it into the **OpenVPN GUI** or **Tunnelblick**.
    - **Mobile (iOS/Android)**: Transfer the file and open it with the **OpenVPN Connect** app.

### Technical Security Features:
*   **Unique Credentials**: Every download contains a unique client certificate/key pair (simulated in this environment).
*   **Optimized Protocol**: Defaults to **UDP 1194** for maximum throughput and lower latency.
*   **No Logs**: Configurations are generated on the fly and discarded after the user session (stateless provisioning).

## 💼 Use Cases
*   **Bypassing Censorship**: Connect to nodes in different regions to access geo-blocked content.
*   **Public Wi-Fi Security**: Protect your traffic in cafes or airports using our hardened profiles.
*   **Remote Work Audit**: Ensure employees' private VPN configs meet corporate security standards.
*   **Privacy Verification**: Check if your "No-Log" VPN provider is actually using obsolete encryption.
*   **Troubleshooting**: Identify why a connection might be dropping or leaking data.
