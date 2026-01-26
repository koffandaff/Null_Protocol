# 📝 Changelog

All notable changes to the Fsociety Cybersecurity Platform will be documented in this file.

## [Unreleased]

### Added
- **Frontend (Phase 2)**:
  - Created Glassmorphism Design System with CSS variables and animations.
  - Implemented Single Page Application (SPA) architecture with custom Router.
  - Added Authentication Views (Login/Signup) with JWT handling.
  - Added Dashboard with real-time stats integration.
  - Added Scanning Tools UI for DNS, WHOIS, IP, and Port scanning.
  - Added Admin Panel for user management.
  - Added VPN Configuration generator UI.
- **VPN Config Generator (Phase 5.1)**:
  - Added `VPN_Model` for config schemas.
  - Added `VPN_Service` for generating OpenVPN and WireGuard configurations.
  - Added `vpn_tools` using `cryptography` library for key generation.
  - Added `VPN_Router` with endpoints `/api/vpn/openvpn` and `/api/vpn/wireguard`.
- Created `changelog.md` to track project progress.
- Created `understood.md` to document project understanding.
- Created `README.md` for project documentation.
