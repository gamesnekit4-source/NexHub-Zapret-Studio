"""
NexHub Proxy & VPN Protocol Parser
Supports VLESS (TCP, WS, gRPC, Reality), VMess, Shadowsocks, Trojan, Socks5, HTTP,
Clash YAML proxies, and Base64 subscription decoders.
"""

import json
import base64
import urllib.parse
import re
import uuid

def safe_b64decode(s: str) -> str:
    s = s.strip()
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(s).decode('utf-8', errors='ignore')
    except Exception:
        try:
            return base64.urlsafe_b64decode(s).decode('utf-8', errors='ignore')
        except Exception:
            return ""

def clean_name(raw_name: str, fallback: str) -> str:
    if not raw_name:
        return fallback
    try:
        unquoted = urllib.parse.unquote(raw_name, encoding='utf-8', errors='ignore')
        return unquoted.strip()
    except Exception:
        return fallback

def parse_link(raw_link: str) -> dict | None:
    raw_link = raw_link.strip()
    if not raw_link:
        return None

    if raw_link.startswith("vless://"):
        return parse_vless(raw_link)
    elif raw_link.startswith("vmess://"):
        return parse_vmess(raw_link)
    elif raw_link.startswith("ss://"):
        return parse_ss(raw_link)
    elif raw_link.startswith("trojan://"):
        return parse_trojan(raw_link)
    elif raw_link.startswith("socks5://") or raw_link.startswith("socks://"):
        return parse_socks(raw_link)
    elif raw_link.startswith("http://") or raw_link.startswith("https://"):
        return parse_http_proxy(raw_link)
    return None

def parse_vless(url_str: str) -> dict | None:
    try:
        parsed = urllib.parse.urlparse(url_str)
        user_info = parsed.netloc.split('@')[0]
        host_port = parsed.netloc.split('@')[1]

        if ':' in host_port:
            host, port_str = host_port.rsplit(':', 1)
            port = int(port_str)
        else:
            host = host_port
            port = 443

        params = dict(urllib.parse.parse_qsl(parsed.query))
        name = clean_name(parsed.fragment, f"VLESS-{host}")

        security = params.get('security', 'none').lower()
        net = params.get('type', 'tcp').lower()

        return {
            'id': str(uuid.uuid4())[:8],
            'type': 'vless',
            'name': name,
            'host': host,
            'port': port,
            'uuid': user_info,
            'security': security,
            'network': net,
            'flow': params.get('flow', ''),
            'sni': params.get('sni', host),
            'fingerprint': params.get('fp', 'chrome'),
            'publicKey': params.get('pbk', ''),
            'shortId': params.get('sid', ''),
            'spiderX': params.get('spx', ''),
            'path': params.get('path', '/'),
            'headerType': params.get('headerType', 'none'),
            'serviceName': params.get('serviceName', ''),
            'raw': url_str,
            'ping': -1
        }
    except Exception as e:
        print(f"Error parsing VLESS: {e}")
        return None

def parse_vmess(url_str: str) -> dict | None:
    try:
        b64_content = url_str[8:]
        decoded = safe_b64decode(b64_content)
        data = json.loads(decoded)

        name = data.get('ps', f"VMess-{data.get('add', 'Server')}")
        host = data.get('add', '')
        port = int(data.get('port', 443))
        uid = data.get('id', '')
        net = data.get('net', 'tcp')
        tls = data.get('tls', '')
        security = 'tls' if tls == 'tls' else 'none'

        return {
            'id': str(uuid.uuid4())[:8],
            'type': 'vmess',
            'name': name,
            'host': host,
            'port': port,
            'uuid': uid,
            'alterId': int(data.get('aid', 0)),
            'security': security,
            'network': net,
            'sni': data.get('sni', data.get('host', host)),
            'path': data.get('path', '/'),
            'cipher': data.get('scy', 'auto'),
            'raw': url_str,
            'ping': -1
        }
    except Exception as e:
        print(f"Error parsing VMess: {e}")
        return None

def parse_ss(url_str: str) -> dict | None:
    try:
        parsed = urllib.parse.urlparse(url_str)
        name = clean_name(parsed.fragment, "Shadowsocks")
        netloc = parsed.netloc

        if '@' in netloc:
            user_b64, host_port = netloc.split('@', 1)
            decoded_user = safe_b64decode(user_b64)
            if ':' in decoded_user:
                method, password = decoded_user.split(':', 1)
            else:
                method = decoded_user
                password = ""
            host, port_str = host_port.rsplit(':', 1)
            port = int(port_str)
        else:
            decoded = safe_b64decode(netloc)
            if '@' in decoded:
                method_pass, host_port = decoded.split('@', 1)
                method, password = method_pass.split(':', 1)
                host, port_str = host_port.rsplit(':', 1)
                port = int(port_str)
            else:
                return None

        return {
            'id': str(uuid.uuid4())[:8],
            'type': 'shadowsocks',
            'name': name,
            'host': host,
            'port': port,
            'method': method,
            'password': password,
            'raw': url_str,
            'ping': -1
        }
    except Exception as e:
        print(f"Error parsing SS: {e}")
        return None

def parse_trojan(url_str: str) -> dict | None:
    try:
        parsed = urllib.parse.urlparse(url_str)
        password = parsed.netloc.split('@')[0]
        host_port = parsed.netloc.split('@')[1]

        if ':' in host_port:
            host, port_str = host_port.rsplit(':', 1)
            port = int(port_str)
        else:
            host = host_port
            port = 443

        params = dict(urllib.parse.parse_qsl(parsed.query))
        name = clean_name(parsed.fragment, f"Trojan-{host}")

        return {
            'id': str(uuid.uuid4())[:8],
            'type': 'trojan',
            'name': name,
            'host': host,
            'port': port,
            'password': password,
            'sni': params.get('sni', host),
            'security': params.get('security', 'tls'),
            'network': params.get('type', 'tcp'),
            'raw': url_str,
            'ping': -1
        }
    except Exception as e:
        print(f"Error parsing Trojan: {e}")
        return None

def parse_socks(url_str: str) -> dict | None:
    try:
        parsed = urllib.parse.urlparse(url_str)
        name = clean_name(parsed.fragment, "SOCKS5 Proxy")
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 1080
        user = parsed.username or ""
        pwd = parsed.password or ""
        return {
            'id': str(uuid.uuid4())[:8],
            'type': 'socks',
            'name': name,
            'host': host,
            'port': port,
            'user': user,
            'password': pwd,
            'raw': url_str,
            'ping': -1
        }
    except Exception:
        return None

def parse_http_proxy(url_str: str) -> dict | None:
    try:
        parsed = urllib.parse.urlparse(url_str)
        name = clean_name(parsed.fragment, "HTTP Proxy")
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        user = parsed.username or ""
        pwd = parsed.password or ""
        if not host:
            return None
        return {
            'id': str(uuid.uuid4())[:8],
            'type': 'http',
            'name': name,
            'host': host,
            'port': port,
            'user': user,
            'password': pwd,
            'raw': url_str,
            'ping': -1
        }
    except Exception:
        return None

def parse_clash_yaml_proxies(content: str) -> list[dict]:
    """Lightweight regex parser for Clash YAML proxy lists."""
    nodes = []
    # Find proxies: block
    if "proxies:" not in content:
        return nodes
    try:
        lines = content.splitlines()
        in_proxies = False
        current_proxy = {}

        for line in lines:
            line_strip = line.strip()
            if line_strip == "proxies:":
                in_proxies = True
                continue
            if in_proxies and line_strip.startswith("proxy-groups:"):
                in_proxies = False
                if current_proxy:
                    nodes.append(current_proxy)
                break

            if in_proxies:
                if line_strip.startswith("- "):
                    if current_proxy and "server" in current_proxy:
                        nodes.append(current_proxy)
                    current_proxy = {}
                    line_strip = line_strip[2:]

                if ":" in line_strip:
                    k, v = line_strip.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"')
                    if k in ("name", "server", "type", "port", "uuid", "password", "network", "tls", "sni"):
                        if k == "port":
                            try: v = int(v)
                            except: v = 443
                        current_proxy[k] = v

        if current_proxy and "server" in current_proxy:
            nodes.append(current_proxy)

        # Convert to NexHub nodes
        parsed_nodes = []
        for p in nodes:
            server_host = p.get("server", "")
            if not server_host or server_host == "0.0.0.0":
                continue
            ptype = p.get("type", "vless").lower()
            name = p.get("name", f"{ptype.upper()}-{server_host}")
            parsed_nodes.append({
                'id': str(uuid.uuid4())[:8],
                'type': ptype,
                'name': name,
                'host': server_host,
                'port': int(p.get("port", 443)),
                'uuid': p.get("uuid", ""),
                'password': p.get("password", ""),
                'security': 'tls' if p.get('tls') == 'true' else 'none',
                'network': p.get('network', 'tcp'),
                'sni': p.get('sni', server_host),
                'ping': -1
            })
        return parsed_nodes
    except Exception as e:
        print("Clash YAML parse error:", e)
        return []

def parse_subscription_text(content: str) -> list[dict]:
    # Check for Clash YAML first
    if "proxies:" in content:
        clash_nodes = parse_clash_yaml_proxies(content)
        if clash_nodes:
            return clash_nodes

    decoded = safe_b64decode(content)
    if decoded and ("vless://" in decoded or "vmess://" in decoded or "ss://" in decoded or "trojan://" in decoded or "proxies:" in decoded):
        content = decoded

    if "proxies:" in content:
        clash_nodes = parse_clash_yaml_proxies(content)
        if clash_nodes:
            return clash_nodes

    nodes = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        node = parse_link(line)
        if node:
            # Filter out obvious invalid dummy entries
            if node.get("host") != "0.0.0.0":
                nodes.append(node)
    return nodes

def build_xray_config(node: dict, socks_port: int = 10808, http_port: int = 10809) -> dict:
    outbound = {}
    ntype = node.get('type')

    if ntype == 'vless':
        vnext = [{
            "address": node['host'],
            "port": node['port'],
            "users": [{
                "id": node['uuid'],
                "encryption": "none",
                "flow": node.get('flow', '')
            }]
        }]
        stream_settings = {
            "network": node.get('network', 'tcp'),
            "security": node.get('security', 'none')
        }

        if node.get('security') == 'reality':
            stream_settings['realitySettings'] = {
                "show": False,
                "fingerprint": node.get('fingerprint', 'chrome'),
                "serverName": node.get('sni', node['host']),
                "publicKey": node.get('publicKey', ''),
                "shortId": node.get('shortId', ''),
                "spiderX": node.get('spiderX', '')
            }
        elif node.get('security') == 'tls':
            stream_settings['tlsSettings'] = {
                "serverName": node.get('sni', node['host']),
                "fingerprint": node.get('fingerprint', 'chrome')
            }

        if node.get('network') == 'ws':
            stream_settings['wsSettings'] = {
                "path": node.get('path', '/'),
                "headers": {"Host": node.get('sni', node['host'])}
            }
        elif node.get('network') == 'grpc':
            stream_settings['grpcSettings'] = {
                "serviceName": node.get('serviceName', '')
            }

        outbound = {
            "tag": "proxy",
            "protocol": "vless",
            "settings": {"vnext": vnext},
            "streamSettings": stream_settings
        }

    elif ntype == 'vmess':
        vnext = [{
            "address": node['host'],
            "port": node['port'],
            "users": [{
                "id": node['uuid'],
                "alterId": node.get('alterId', 0),
                "security": node.get('cipher', 'auto')
            }]
        }]
        stream_settings = {
            "network": node.get('network', 'tcp'),
            "security": node.get('security', 'none')
        }
        if node.get('security') == 'tls':
            stream_settings['tlsSettings'] = {
                "serverName": node.get('sni', node['host'])
            }
        if node.get('network') == 'ws':
            stream_settings['wsSettings'] = {
                "path": node.get('path', '/'),
                "headers": {"Host": node.get('sni', node['host'])}
            }
        outbound = {
            "tag": "proxy",
            "protocol": "vmess",
            "settings": {"vnext": vnext},
            "streamSettings": stream_settings
        }

    elif ntype == 'shadowsocks':
        servers = [{
            "address": node['host'],
            "port": node['port'],
            "method": node.get('method', 'aes-256-gcm'),
            "password": node.get('password', '')
        }]
        outbound = {
            "tag": "proxy",
            "protocol": "shadowsocks",
            "settings": {"servers": servers}
        }

    elif ntype == 'trojan':
        servers = [{
            "address": node['host'],
            "port": node['port'],
            "password": node.get('password', '')
        }]
        outbound = {
            "tag": "proxy",
            "protocol": "trojan",
            "settings": {"servers": servers},
            "streamSettings": {
                "network": node.get('network', 'tcp'),
                "security": "tls",
                "tlsSettings": {
                    "serverName": node.get('sni', node['host'])
                }
            }
        }

    elif ntype == 'socks':
        servers = [{
            "address": node['host'],
            "port": node['port']
        }]
        if node.get('user'):
            servers[0]["users"] = [{
                "user": node['user'],
                "pass": node.get('password', '')
            }]
        outbound = {
            "tag": "proxy",
            "protocol": "socks",
            "settings": {"servers": servers}
        }
    else:
        outbound = {"tag": "proxy", "protocol": "freedom"}

    return {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "tag": "socks-in",
                "port": socks_port,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "settings": {"auth": "noauth", "udp": True},
                "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"]}
            },
            {
                "tag": "http-in",
                "port": http_port,
                "listen": "127.0.0.1",
                "protocol": "http",
                "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"]}
            }
        ],
        "outbounds": [
            outbound,
            {"tag": "direct", "protocol": "freedom"},
            {"tag": "block", "protocol": "blackhole"}
        ]
    }
