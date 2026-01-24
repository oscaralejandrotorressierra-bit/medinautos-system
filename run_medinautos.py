import os
import sys
import threading
import time
import webbrowser
from http.client import HTTPConnection

import uvicorn


def _wait_for_server(host: str, port: int, timeout_s: int = 10) -> bool:
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            conn = HTTPConnection(host, port, timeout=1)
            conn.request("GET", "/login")
            conn.getresponse()
            conn.close()
            return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_dir)

    url = "http://127.0.0.1:8000/login"
    threading.Thread(
        target=lambda: (_wait_for_server("127.0.0.1", 8000), webbrowser.open(url)),
        daemon=True,
    ).start()

    config = uvicorn.Config(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
