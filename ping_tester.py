"""
NexHub High-Speed Concurrent Latency & Ping Tester
Skips invalid or dummy hosts immediately with safe short timeouts.
"""

import socket
import time
from concurrent.futures import ThreadPoolExecutor

def test_single_ping(host: str, port: int, timeout: float = 1.2) -> int:
    """Measures TCP handshake latency in ms. Returns -1 if unreachable."""
    if not host or host in ("0.0.0.0", "localhost", "127.0.0.1") or port <= 0 or port > 65535:
        return -1

    start = time.perf_counter()
    try:
        addr_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        if not addr_info:
            return -1
        family, socktype, proto, _, sockaddr = addr_info[0]

        sock = socket.socket(family, socktype, proto)
        sock.settimeout(timeout)
        sock.connect(sockaddr)
        sock.close()
        elapsed = (time.perf_counter() - start) * 1000.0
        return max(1, int(elapsed))
    except Exception:
        return -1

def test_all_pings(servers: list[dict], max_workers: int = 12) -> dict[str, int]:
    results = {}

    def _worker(node):
        nid = node.get('id')
        host = node.get('host')
        port = node.get('port')
        if not host or not port or host == "0.0.0.0":
            return nid, -1
        ping = test_single_ping(host, int(port))
        return nid, ping

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker, s) for s in servers]
        for f in futures:
            try:
                nid, latency = f.result()
                results[nid] = latency
            except Exception:
                pass
    return results
