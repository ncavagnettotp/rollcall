"""Serve the production React build and existing API for the desktop rehearsal."""

import argparse
import ipaddress
import os
from pathlib import Path
from urllib.parse import urlsplit

from fastapi.responses import FileResponse
from starlette.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.applications import Starlette
from starlette.routing import Mount, Route
import uvicorn


def build_app(dist: Path):
    from app.main import app as api

    index = dist / 'index.html'
    if not index.is_file():
        raise FileNotFoundError('Build the frontend before starting the desktop proof.')

    async def home(_request):
        return FileResponse(index, headers={'Cache-Control': 'no-cache'})

    return Starlette(routes=[
        Route('/', home),
        Mount('/assets', app=StaticFiles(directory=dist / 'assets')),
        Mount('/', app=api),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--key', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True, help='Synthetic PDF archive')
    parser.add_argument('--port', type=int, default=8443)
    parser.add_argument('--lan-host', type=ipaddress.IPv4Address)
    parser.add_argument('--lan-client', type=ipaddress.IPv4Address)
    args = parser.parse_args()
    if bool(args.lan_host) != bool(args.lan_client):
        parser.error('Supply both the LAN host and the single allowed client.')
    if args.lan_host and not all(address in ipaddress.IPv4Network('192.168.0.0/16')
                                 for address in (args.lan_host, args.lan_client)):
        parser.error('The home rehearsal requires private 192.168.x.x addresses.')

    # Require a deliberately supplied loopback database before app.main reads .env.
    url = urlsplit(os.environ.get('ROLLCALL_PROOF_DATABASE_URL', ''))
    try:
        local_database = url.hostname and ipaddress.ip_address(url.hostname).is_loopback
    except ValueError:
        local_database = False
    if url.scheme not in ('postgres', 'postgresql') or not local_database or not url.path.strip('/'):
        parser.error('Set ROLLCALL_PROOF_DATABASE_URL to a disposable loopback database.')
    archive = args.archive.resolve()
    dist = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
    if archive.is_relative_to(dist) or dist.is_relative_to(archive):
        parser.error('The archive must be separate from the frontend build.')
    os.environ['DATABASE_URL'] = url.geturl()
    os.environ['DOCUMENT_ARCHIVE_DIR'] = str(archive)
    app = build_app(dist)
    if args.lan_host:
        allowed = {str(args.lan_host), str(args.lan_client)}
        upstream = app

        async def app(scope, receive, send):
            if scope['type'] == 'http' and (scope.get('client') or ('',))[0] not in allowed:
                await PlainTextResponse('Forbidden', status_code=403)(scope, receive, send)
                return
            await upstream(scope, receive, send)

    uvicorn.run(app, host=str(args.lan_host or '127.0.0.1'), port=args.port,
                ssl_certfile=args.certificate, ssl_keyfile=args.key, access_log=False,
                proxy_headers=False)


if __name__ == '__main__':
    main()
