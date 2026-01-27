from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from model.VPN_Model import VPNConfigRequest, WireGuardRequest, VPNConfigResponse
from service.VPN_Service import vpn_service
from routers.dependencies import get_current_user

router = APIRouter()

@router.get("/servers")
async def get_available_servers(
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of available Fsociety VPN nodes.
    """
    return vpn_service.get_available_servers()

@router.post("/openvpn", response_model=VPNConfigResponse)
async def generate_openvpn_config(
    request: VPNConfigRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate an OpenVPN configuration file.
    """
    try:
        config = vpn_service.generate_openvpn_config(request, current_user['id'])
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OpenVPN configuration: {str(e)}"
        )

@router.post("/wireguard", response_model=VPNConfigResponse)
async def generate_wireguard_config(
    request: WireGuardRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a WireGuard configuration file.
    """
    try:
        config = vpn_service.generate_wireguard_config(request, current_user['id'])
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate WireGuard configuration: {str(e)}"
        )

@router.get("/configs", response_model=List[VPNConfigResponse])
async def list_user_configs(
    current_user: dict = Depends(get_current_user)
):
    """
    List all VPN configurations created by the current user.
    """
    try:
        configs = vpn_service.get_user_configs(current_user['id'])
        return configs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configurations: {str(e)}"
        )
