"""Health check (spec: Health check).

The app reaches the database through a small relay that the test can switch off and on, so the
"database down" and "database comes back" cases are real network failures without stopping the
shared test database.
"""

import contextlib
import dataclasses
import socket
import threading
import time
from urllib.parse import urlsplit, urlunsplit

import pytest
from fastapi.testclient import TestClient

from rollcall.main import create_app


class Relay:
    """Forwards TCP connections from a local port to the database; can be cut and restored."""

    def __init__(self, target_host: str, target_port: int):
        self.target = (target_host, target_port)
        probe = socket.create_server(("127.0.0.1", 0))
        self.port = probe.getsockname()[1]
        probe.close()
        self._sockets: list[socket.socket] = []
        self._listener: socket.socket | None = None
        self._lock = threading.Lock()

    def start(self):
        self._listener = socket.create_server(("127.0.0.1", self.port), reuse_port=True)
        threading.Thread(target=self._accept, args=(self._listener,), daemon=True).start()

    def stop(self):
        """Refuse new connections and cut every open one, like the database going away."""
        with self._lock:
            if self._listener:
                # On Linux, close() alone does not wake a thread blocked in accept();
                # shutdown() does, so no new connection slips through.
                with contextlib.suppress(OSError):
                    self._listener.shutdown(socket.SHUT_RDWR)
                self._listener.close()
                self._listener = None
            for sock in self._sockets:
                with contextlib.suppress(OSError):
                    sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            self._sockets.clear()

    def _accept(self, listener):
        while True:
            try:
                client, _ = listener.accept()
            except OSError:
                return
            upstream = socket.create_connection(self.target)
            with self._lock:
                self._sockets += [client, upstream]
            for source, dest in ((client, upstream), (upstream, client)):
                threading.Thread(target=self._pipe, args=(source, dest), daemon=True).start()

    @staticmethod
    def _pipe(source, dest):
        try:
            while data := source.recv(65536):
                dest.sendall(data)
        except OSError:
            pass
        finally:
            for sock in (source, dest):
                with contextlib.suppress(OSError):
                    sock.shutdown(socket.SHUT_RDWR)


@pytest.fixture
def relay(database_url):
    parts = urlsplit(database_url)
    relay = Relay(parts.hostname, parts.port)
    relay.start()
    yield relay
    relay.stop()


@pytest.fixture
def relayed_client(settings, relay):
    parts = urlsplit(settings.database_url)
    auth = parts.netloc.rpartition("@")[0]
    relayed_url = urlunsplit(parts._replace(netloc=f"{auth}@127.0.0.1:{relay.port}"))
    app = create_app(dataclasses.replace(settings, database_url=relayed_url))
    with TestClient(app) as test_client:
        yield test_client


def test_healthy_when_the_database_answers(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "ok"


def test_unhealthy_quickly_when_the_database_is_gone(relayed_client, relay):
    assert relayed_client.get("/health").status_code == 200
    relay.stop()

    started = time.monotonic()
    response = relayed_client.get("/health")
    assert time.monotonic() - started < 5
    assert response.status_code == 503
    assert response.text == "database unavailable"  # no address, user or error text


def test_healthy_again_when_the_database_comes_back_without_restarting(relayed_client, relay):
    relay.stop()
    assert relayed_client.get("/health").status_code == 503
    relay.start()

    deadline = time.monotonic() + 10
    while (status := relayed_client.get("/health").status_code) != 200:
        assert time.monotonic() < deadline, f"still {status} after the database came back"
        time.sleep(0.2)


def test_health_needs_no_sign_in_and_sets_no_cookies(client):
    response = client.get("/health")
    assert "set-cookie" not in response.headers
