"""One HTTPS POST per case. No redirects, proxies, retries, or body logging."""
import http.client
import json
import multiprocessing
import os
import ssl
import time
from .core import number, require, strict_json, ValidationError

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MAX_RESPONSE_BYTES = 1048576
MAX_REQUEST_BYTES = 65536
MIN_TIMEOUT_SECONDS = 0.001


def exchange(payload, timeout):
    # Credential comes only from environment, never arguments or a settings file.
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        return {"status": "missing_key"}
    conn = None
    try:
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(body) > MAX_REQUEST_BYTES:
            return {"status": "request_too_large"}
        conn = http.client.HTTPSConnection("api.typesafe.ai", timeout=timeout,
                                           context=ssl.create_default_context())
        conn.request("POST", "/v1/systemone", body=body,
                     headers={"Authorization": "Bearer " + key,
                              "Content-Type": "application/json", "Accept": "application/json"})
        response = conn.getresponse()
        if response.status != 200:
            # Deliberately never read error bodies, Location, or arbitrary headers.
            return {"status": "http_error", "http_status": response.status}
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            return {"status": "response_too_large"}
        parsed = strict_json(raw)
        # Reject even successful echoes of the credential, including JSON escapes.
        if key in json.dumps(parsed, ensure_ascii=False):
            return {"status": "invalid_response"}
        return {"status": "ok", "response": parsed}
    except ValidationError:
        return {"status": "invalid_response"}
    except Exception:
        # Do not include exception text, which can contain keys, URLs, or bodies.
        return {"status": "network_error"}
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _worker(pipe, payload, timeout):
    try:
        pipe.send(exchange(payload, timeout))
    except Exception:
        pass
    finally:
        pipe.close()


def bounded_request(payload, timeout, worker=None):
    number(timeout, MIN_TIMEOUT_SECONDS, 120)
    context = multiprocessing.get_context("spawn")
    reader, writer = context.Pipe(duplex=False)
    proc = context.Process(target=worker or _worker, args=(writer, payload, timeout), daemon=True)
    deadline = time.monotonic() + timeout
    try:
        proc.start()
        writer.close()
        if not reader.poll(max(0, deadline - time.monotonic())):
            return {"status": "timeout"}
        try:
            return reader.recv()
        except (EOFError, OSError):
            return {"status": "network_error"}
    finally:
        if proc.pid is not None:
            if proc.is_alive():
                proc.terminate()
            proc.join(timeout=0.1)
            if proc.is_alive():
                proc.kill()
                proc.join(timeout=0.1)
            proc.close()
        reader.close()
        writer.close()
