#!/usr/bin/env python3
"""
Get OAuth2 configuration from the automation API.

Usage:
    python scripts/get_oauth_config.py --system-name <name> --url <url> --redirect-uris <uris> --employee-id <id>

Examples:
    python scripts/get_oauth_config.py \\
        --system-name "My System" \\
        --url "http://192.168.1.100:3000" \\
        --redirect-uris "http://192.168.1.100:3000/callback" \\
        --employee-id 99999999
"""

import sys
import json
import argparse
import requests
from typing import Dict, Optional
from urllib.parse import urlparse


OAUTH_CONFIG_API = "https://loginpass-bff-qa.tap4fun.com/application/automation/add"


def parse_url(url: str) -> Dict[str, str]:
    """Parse URL to extract host, port, and path."""
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "",
        "port": str(parsed.port) if parsed.port else ("443" if parsed.scheme == "https" else "80"),
        "scheme": parsed.scheme or "http",
        "path": parsed.path or "/"
    }


def get_oauth_config(
    system_name: str,
    url: str,
    redirect_uris: str,
    employee_id: int,
    third_party: bool = True,
    access_company_ids: list = None
) -> Optional[Dict]:
    """
    Get OAuth2 configuration from the automation API.
    
    Args:
        system_name: System name
        url: System URL
        redirect_uris: Redirect URIs
        employee_id: Employee ID
        third_party: Whether it's a third-party system (default: True)
        access_company_ids: List of company IDs (default: [1])
    
    Returns:
        Dict with OAuth2 configuration or None if failed
    """
    if access_company_ids is None:
        access_company_ids = [1]
    
    payload = {
        "systemName": system_name,
        "url": url,
        "redirectUris": redirect_uris,
        "employeeId": employee_id,
        "thirdParty": third_party,
        "accessCompanyIds": access_company_ids
    }
    
    try:
        response = requests.put(
            OAUTH_CONFIG_API,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and data.get("data"):
            return {
                "success": True,
                "client_id": data["data"]["id"],
                "client_secret": data["data"]["secret"],
                "redirect_uri": data["data"]["redirectUris"],
                "url": data["data"]["url"],
                "system_name": data["data"]["systemName"],
                "parsed_url": parse_url(data["data"]["url"]),
                "parsed_redirect": parse_url(data["data"]["redirectUris"])
            }
        else:
            return {
                "success": False,
                "error": data.get("message", "Unknown error"),
                "data": data
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def format_config_output(config: Dict) -> str:
    """Format configuration output for display."""
    if not config.get("success"):
        return f"❌ Error: {config.get('error', 'Unknown error')}"
    
    output = []
    output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    output.append("✅ OAuth2配置获取成功！")
    output.append("")
    output.append("📋 OAuth2配置信息：")
    output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    output.append(f"CLIENT_ID: {config['client_id']}")
    output.append(f"CLIENT_SECRET: {config['client_secret']}")
    output.append(f"REDIRECT_URI: {config['redirect_uri']}")
    output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    output.append("")
    output.append("📌 系统信息：")
    output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    output.append(f"系统URL: {config['url']}")
    output.append(f"IP地址/域名: {config['parsed_url']['host']}")
    output.append(f"端口号: {config['parsed_url']['port']}")
    output.append(f"重定向路径: {config['parsed_redirect']['path']}")
    output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Get OAuth2 configuration from automation API')
    parser.add_argument('--system-name', type=str, required=True, help='System name')
    parser.add_argument('--url', type=str, required=True, help='System URL')
    parser.add_argument('--redirect-uris', type=str, required=True, help='Redirect URIs')
    parser.add_argument('--employee-id', type=int, required=True, help='Employee ID')
    parser.add_argument('--third-party', type=bool, default=True, help='Third party system (default: True)')
    parser.add_argument('--access-company-ids', type=int, nargs='+', default=[1], help='Access company IDs (default: [1])')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    config = get_oauth_config(
        system_name=args.system_name,
        url=args.url,
        redirect_uris=args.redirect_uris,
        employee_id=args.employee_id,
        third_party=args.third_party,
        access_company_ids=args.access_company_ids
    )
    
    if args.json:
        print(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        print(format_config_output(config))
    
    sys.exit(0 if config.get("success") else 1)


if __name__ == "__main__":
    main()
