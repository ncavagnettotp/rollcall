"""Verify restart durability using a disposable, manually started PostgreSQL cluster.

Never touches backend/.env or an installed Windows service. Run with the project's
Python environment. Cluster files/logs are local test artifacts, not checkpoints.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import io

import psycopg


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin-dir', type=Path,
                        default=Path('C:/Program Files/PostgreSQL/18/bin'))
    parser.add_argument('--port', type=int, default=55432)
    args = parser.parse_args()
    backend = Path(__file__).resolve().parent
    project = backend.parent
    artifact_root = project / 'output' / 'isolated-postgres'
    run = artifact_root / ('run-' + secrets.token_hex(6))
    data = run / 'data'
    pwfile = run / 'init-password.txt'
    evidence = {'scope': 'isolated test cluster only; configured database not restarted',
                'utc_started': datetime.now(timezone.utc).isoformat(),
                'port': args.port, 'checks': [], 'result': 'FAIL'}
    initialized = False

    def record(check: str) -> None:
        evidence['checks'].append(check)
        print('PASS:', check, flush=True)

    def command(argv: list[str], log: str, env=None, timeout=60) -> None:
        with (run / log).open('a', encoding='utf-8') as output:
            result = subprocess.run(argv, cwd=backend, env=env, stdout=output,
                                    stderr=subprocess.STDOUT, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f'{Path(argv[0]).name} failed; see {log}')

    pg_ctl = args.bin_dir / 'pg_ctl.exe'
    initdb = args.bin_dir / 'initdb.exe'
    for binary in (pg_ctl, initdb):
        if not binary.is_file():
            raise SystemExit(f'Required PostgreSQL binary missing: {binary.name}')
    # Reserve-check the dedicated loopback port before initializing any files.
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', args.port))
    run.mkdir(parents=True)
    password = secrets.token_hex(24)
    env = os.environ.copy()
    env['DATABASE_URL'] = f'postgresql://foundation_verifier:{password}@127.0.0.1:{args.port}/foundation_verification'
    env['TEST_DATABASE_URL'] = env['DATABASE_URL']
    env['TEST_DOCUMENT_DATABASE_URL'] = env['DATABASE_URL']
    env['TEST_POSTGRES_BIN'] = str(args.bin_dir.resolve())

    def ctl(action: str) -> None:
        argv = [str(pg_ctl), '-D', str(data), '-w', '-t', '30']
        if action == 'start':
            argv += ['-l', str(run / 'postgres.log'), '-o', f'-h 127.0.0.1 -p {args.port}', 'start']
        else:
            argv += ['-m', 'fast', 'stop']
        command(argv, 'lifecycle.log')

    try:
        pwfile.write_text(password + '\n', encoding='utf-8')
        try:
            command([str(initdb), '-D', str(data), '-U', 'foundation_verifier',
                     '--pwfile', str(pwfile), '--auth', 'scram-sha-256',
                     '--encoding', 'UTF8', '--no-locale'], 'initdb.log')
            initialized = True
        finally:
            pwfile.unlink(missing_ok=True)
        ctl('start')
        with psycopg.connect(host='127.0.0.1', port=args.port,
                             user='foundation_verifier', password=password,
                             dbname='postgres', connect_timeout=3,
                             autocommit=True) as connection:
            connection.execute('CREATE DATABASE foundation_verification')
            evidence['server_version'] = connection.info.server_version
        record('dedicated cluster initialized and started manually on loopback')
        command([sys.executable, str(backend / 'check_persistence.py'), 'write'],
                'probe.log', env=env)
        command([sys.executable, str(backend / 'check_persistence.py'), 'read'],
                'probe.log', env=env)
        record('existing persistence probe write/read succeeded')

        # Loading the application may load the normal .env; override explicitly
        # before requests so only this test cluster is contacted by readiness.
        from fastapi.testclient import TestClient
        from app.main import app
        previous_url = os.environ.get('DATABASE_URL')
        previous_archive = os.environ.get('DOCUMENT_ARCHIVE_DIR')
        os.environ['DATABASE_URL'] = env['DATABASE_URL']
        os.environ['DOCUMENT_ARCHIVE_DIR'] = str(run / 'document-archive')
        try:
            from app.document_store import connect, SCHEMA
            from pypdf import PdfWriter
            with connect() as connection:
                connection.execute(SCHEMA)
            buffer = io.BytesIO()
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            writer.write(buffer)
            source_pdf = buffer.getvalue()
            with TestClient(app) as client:
                assert client.get('/api/health/db').status_code == 200
                upload = client.post('/api/documents', content=source_pdf,
                                     headers={'Content-Type': 'application/pdf', 'X-Filename': 'restart-probe.pdf'})
                assert upload.status_code == 200
                document = upload.json()
                endpoint = '/api/documents/' + document['id']
                saved = client.patch(endpoint, json={'version': document['version'],
                                     'fields': {'notes': 'Restart durability probe'}, 'status': 'reviewed'})
                assert saved.status_code == 200
                record('Stage 2 original PDF and corrected review saved before restart')
                ctl('stop')
                assert client.get('/api/health/db').status_code == 503
                assert client.get('/api/health').status_code == 200
                record('stopped cluster: database readiness 503 and API liveness 200')
                ctl('start')
                command([sys.executable, str(backend / 'check_persistence.py'), 'read'],
                        'probe.log', env=env)
                assert client.get('/api/health/db').status_code == 200
                record('cluster restarted: durable marker read and database readiness 200')
                reopened = client.get(endpoint)
                assert reopened.status_code == 200
                assert reopened.json()['fields']['notes'] == 'Restart durability probe'
                assert reopened.json()['extracted'] == document['extracted']
                assert reopened.json()['version'] == saved.json()['version']
                assert client.get(document['pdf_url']).content == source_pdf
                record('Stage 2 original bytes, extracted evidence, corrected review and revision survived database restart')
        finally:
            if previous_url is None:
                os.environ.pop('DATABASE_URL', None)
            else:
                os.environ['DATABASE_URL'] = previous_url
            if previous_archive is None:
                os.environ.pop('DOCUMENT_ARCHIVE_DIR', None)
            else:
                os.environ['DOCUMENT_ARCHIVE_DIR'] = previous_archive
        command([sys.executable, '-m', 'pytest', '-q'], 'pytest.log', env=env)
        record('full backend suite including real PostgreSQL integration passed')
        evidence['result'] = 'PASS'
    except Exception as error:
        # Avoid emitting connection details, secrets, or environment values.
        evidence['failure_type'] = type(error).__name__
        print('FAIL:', type(error).__name__, '(inspect local test logs)', flush=True)
    finally:
        if initialized:
            try:
                status = subprocess.run([str(pg_ctl), '-D', str(data), 'status'],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL, timeout=10)
                if status.returncode == 0:
                    ctl('stop')
                record('dedicated cluster is stopped; installed service untouched')
            except Exception as error:
                evidence['result'] = 'FAIL'
                evidence['cleanup_failure_type'] = type(error).__name__
        evidence['utc_finished'] = datetime.now(timezone.utc).isoformat()
        (run / 'evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
        print('Evidence:', run / 'evidence.json', flush=True)
    return 0 if evidence['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
