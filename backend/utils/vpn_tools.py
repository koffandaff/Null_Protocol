import os
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import x25519

class VPNTools:
    
    @staticmethod
    def generate_wireguard_keys():
        """
        Generate a WireGuard private and public key pair.
        WireGuard uses Curve25519.
        """
        # Generate private key
        private_key = x25519.X25519PrivateKey.generate()
        
        # Generate public key
        public_key = private_key.public_key()
        
        # Serialize to bytes
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # WireGuard keys are base64 encoded
        return {
            "private_key": base64.b64encode(private_bytes).decode('utf-8'),
            "public_key": base64.b64encode(public_bytes).decode('utf-8')
        }

    @staticmethod
    def generate_openvpn_config(server_ip, port, protocol, ca_cert, client_cert, client_key):
        """
        Generate an OpenVPN client configuration string.
        """
        config = f"""client
dev tun
proto {protocol}
remote {server_ip} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
verb 3

<ca>
{ca_cert}
</ca>

<cert>
{client_cert}
</cert>

<key>
{client_key}
</key>
"""
        return config

    @staticmethod
    def generate_wireguard_config(private_key, address, server_public_key, server_endpoint, allowed_ips):
        """
        Generate a WireGuard client configuration string.
        """
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
DNS = 1.1.1.1

[Peer]
PublicKey = {server_public_key}
AllowedIPs = {allowed_ips}
Endpoint = {server_endpoint}
PersistentKeepalive = 25
"""
        return config

vpn_tools = VPNTools()
