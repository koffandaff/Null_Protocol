from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class VPNConfigRequest(BaseModel):
    server_address: str = Field(..., description="VPN Server IP or Hostname")
    port: int = Field(1194, description="VPN Server Port")
    protocol: str = Field("udp", description="Protocol (udp/tcp)")
    cipher: Optional[str] = Field("AES-256-CBC", description="Encryption Cipher")
    auth: Optional[str] = Field("SHA256", description="Auth Algorithm")
    use_compression: bool = True
    dns_servers: List[str] = ["8.8.8.8", "1.1.1.1"]
    routes: List[str] = ["0.0.0.0/0"]

class WireGuardRequest(BaseModel):
    server_public_key: str = Field(..., description="Server Public Key")
    server_endpoint: str = Field(..., description="Server Endpoint (IP:Port)")
    client_private_key: Optional[str] = Field(None, description="Client Private Key (Generated if empty)")
    allowed_ips: str = Field("0.0.0.0/0", description="Allowed IPs")
    persistent_keepalive: int = 25
    dns_servers: List[str] = ["1.1.1.1", "8.8.8.8"]

class VPNConfigResponse(BaseModel):
    id: str
    user_id: str
    type: str  # openvpn or wireguard
    name: str
    config_content: str
    created_at: datetime

class VPNKeys(BaseModel):
    private_key: str
    public_key: str
    preshared_key: Optional[str] = None
