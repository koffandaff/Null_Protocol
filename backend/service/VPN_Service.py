from datetime import datetime
import uuid
from typing import List, Optional
from model.VPN_Model import VPNConfigRequest, WireGuardRequest, VPNConfigResponse, VPNKeys
from utils.vpn_tools import vpn_tools
from model.Auth_Model import db  # Using the shared TempDb instance

class VPNService:
    
    def __init__(self):
        # In a real app, we would store these in a database
        # For now, we'll use the in-memory db from Auth_Model or a local dict
        if not hasattr(db, 'vpn_configs'):
            db.vpn_configs = {} # dynamically add vpn_configs dict to the db instance

    def generate_openvpn_config(self, request: VPNConfigRequest, user_id: str) -> VPNConfigResponse:
        """
        Generate an OpenVPN configuration.
        """
        # Mocking CA and Client cert generation for this example
        # In production, this would interact with a PKI system
        mock_ca = "-----BEGIN CERTIFICATE-----\nMOCK_CA_CERT\n-----END CERTIFICATE-----"
        mock_cert = "-----BEGIN CERTIFICATE-----\nMOCK_CLIENT_CERT\n-----END CERTIFICATE-----"
        mock_key = "-----BEGIN PRIVATE KEY-----\nMOCK_PRIVATE_KEY\n-----END PRIVATE KEY-----"
        
        config_content = vpn_tools.generate_openvpn_config(
            server_ip=request.server_address,
            port=request.port,
            protocol=request.protocol,
            ca_cert=mock_ca,
            client_cert=mock_cert,
            client_key=mock_key
        )
        
        config_id = str(uuid.uuid4())
        
        config = VPNConfigResponse(
            id=config_id,
            user_id=user_id,
            type="openvpn",
            name=f"OpenVPN-{request.server_address}",
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
