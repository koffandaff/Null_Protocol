from datetime import datetime
import uuid
from typing import List, Optional, Dict
from model.VPN_Model import VPNConfigRequest, WireGuardRequest, VPNConfigResponse, VPNKeys
from utils.vpn_tools import vpn_tools
from model.Auth_Model import db  # Using the shared TempDb instance

class VPNService:
    
    def __init__(self):
        # In a real app, we would store these in a database
        if not hasattr(db, 'vpn_configs'):
            db.vpn_configs = {} 

        # Defined VPN Servers for our "Service"
        self.available_servers = [
            {"id": "us-east", "name": "USA - New York", "address": "us-east.fsociety.vpn", "region": "Americas", "load": "42%"},
            {"id": "eu-central", "name": "Germany - Frankfurt", "address": "de-fra.fsociety.vpn", "region": "Europe", "load": "18%"},
            {"id": "asia-east", "name": "Japan - Tokyo", "address": "jp-tk.fsociety.vpn", "region": "Asia", "load": "65%"},
            {"id": "in-west", "name": "India - Mumbai", "address": "in-mum.fsociety.vpn", "region": "Asia", "load": "20%"}
        ]

    def get_available_servers(self) -> List[Dict]:
        """Return list of available VPN servers"""
        return self.available_servers

    def generate_openvpn_config(self, request: VPNConfigRequest, user_id: str) -> VPNConfigResponse:
        """
        Generate an OpenVPN configuration.
        """
        import base64
        import secrets
        
        # If it's a server from our list, we could customize even more
        server_name = f"Fsociety-{request.server_address}"
        server_id = "custom"
        for s in self.available_servers:
            if s['address'] == request.server_address:
                server_name = s['name']
                server_id = s['id']
                break

        # Generate realistic-looking but simulated certificates
        # These are properly formatted PEM blocks with valid base64 content
        def generate_fake_pem(label: str, size: int = 256) -> str:
            random_bytes = secrets.token_bytes(size)
            b64_content = base64.b64encode(random_bytes).decode('ascii')
            # Split into 64-char lines for proper PEM format
            lines = [b64_content[i:i+64] for i in range(0, len(b64_content), 64)]
            return f"-----BEGIN {label}-----\n" + "\n".join(lines) + f"\n-----END {label}-----"

        mock_ca = generate_fake_pem("CERTIFICATE", 512)
        mock_cert = generate_fake_pem("CERTIFICATE", 384)
        mock_key = generate_fake_pem("PRIVATE KEY", 256)
        
        config_content = vpn_tools.generate_openvpn_config(
            server_ip=request.server_address,
            port=request.port,
            protocol=request.protocol,
            ca_cert=mock_ca,
            client_cert=mock_cert,
            client_key=mock_key
        )
        
        config_id = str(uuid.uuid4())
        
        # Create filename: username_fsociety_servername
        safe_server_name = server_id.replace("-", "_").replace(" ", "_")
        config_filename = f"{user_id}_fsociety_{safe_server_name}"
        
        config = VPNConfigResponse(
            id=config_id,
            user_id=user_id,
            type="openvpn",
            name=server_name,
            filename=config_filename,
            config_content=config_content,
            created_at=datetime.utcnow()
        )
        
        # Store in DB
        db.vpn_configs[config_id] = config.model_dump()
        
        return config

    def generate_wireguard_keys(self) -> VPNKeys:
        """
        Generate WireGuard keys.
        """
        keys = vpn_tools.generate_wireguard_keys()
        return VPNKeys(**keys)

    def generate_wireguard_config(self, request: WireGuardRequest, user_id: str) -> VPNConfigResponse:
        """
        Generate a WireGuard configuration.
        """
        # If client private key is not provided, generate one
        if not request.client_private_key:
            keys = vpn_tools.generate_wireguard_keys()
            client_private_key = keys['private_key']
        else:
            client_private_key = request.client_private_key
            
        # Mock client address allocation
        client_address = "10.100.0.2/32"
        
        config_content = vpn_tools.generate_wireguard_config(
            private_key=client_private_key,
            address=client_address,
            server_public_key=request.server_public_key,
            server_endpoint=request.server_endpoint,
            allowed_ips=request.allowed_ips
        )
        
        config_id = str(uuid.uuid4())
        
        config = VPNConfigResponse(
            id=config_id,
            user_id=user_id,
            type="wireguard",
            name=f"WG-{request.server_endpoint}",
            config_content=config_content,
            created_at=datetime.utcnow()
        )
        
        # Store in DB
        db.vpn_configs[config_id] = config.model_dump()
        
        return config

    def get_user_configs(self, user_id: str) -> List[VPNConfigResponse]:
        """
        Get all VPN configs for a user.
        """
        user_configs = []
        for config_data in db.vpn_configs.values():
            if config_data['user_id'] == user_id:
                user_configs.append(VPNConfigResponse(**config_data))
        return user_configs

vpn_service = VPNService()
