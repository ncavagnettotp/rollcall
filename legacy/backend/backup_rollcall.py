"""Create and restore coordinated Rollcall PostgreSQL and PDF backup sets."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import mkdtemp
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo


DUMP = 'database.dump'
MANIFEST = 'manifest.json'
DIGEST = re.compile(r'[0-9a-f]{64}')


def file_hash(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


@contextmanager
def staging(parent):
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(mkdtemp(prefix='.rollcall-incomplete-', dir=parent))
    try:
        yield folder
    finally:
        if folder.exists():
            shutil.rmtree(folder)


def run_postgres(bin_dir, tool, connection_string, *args):
    env = os.environ.copy()
    options = conninfo_to_dict(connection_string)
    password = options.pop('password', None)
    if password is not None:
        env['PGPASSWORD'] = password
    executable = bin_dir / (tool + ('.exe' if os.name == 'nt' else ''))
    command = [str(executable), '--no-password', '--dbname', make_conninfo(**options), *map(str, args)]
    result = subprocess.run(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        raise RuntimeError(f'{tool} failed (exit {result.returncode}). Check database access and PostgreSQL tool version.')


def document_digests(connection, schema):
    query = sql.SQL('SELECT sha256 FROM {}.storage_documents ORDER BY sha256').format(sql.Identifier(schema))
    digests = [row[0] for row in connection.execute(query)]
    if any(not isinstance(value, str) or not DIGEST.fullmatch(value) for value in digests):
        raise ValueError('Invalid document hash in database.')
    return digests


def copy_pdfs(source, destination, digests):
    destination.mkdir()
    for digest in digests:
        filename = digest + '.pdf'
        original = source / filename
        if not original.is_file():
            raise ValueError(f'Missing original PDF for SHA-256 {digest}.')
        copied = destination / filename
        shutil.copyfile(original, copied)
        if file_hash(copied) != digest:
            raise ValueError(f'PDF checksum mismatch for SHA-256 {digest}.')


def create_backup(connection_string, archive, destination, bin_dir):
    archive, destination = archive.resolve(), destination.resolve()
    if destination.is_relative_to(archive) or archive.is_relative_to(destination):
        raise ValueError('The backup destination and live PDF archive must be separate.')
    now = datetime.now(timezone.utc)
    completed = destination / f'rollcall-{now:%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}'
    with staging(destination) as folder:
        with psycopg.connect(connection_string) as connection:
            connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            snapshot, schema = connection.execute('SELECT pg_export_snapshot(), current_schema()').fetchone()
            digests = document_digests(connection, schema)
            run_postgres(bin_dir, 'pg_dump', connection_string, '--format=custom',
                         '--snapshot', snapshot, '--file', folder / DUMP)
        # Archive originals are immutable. Copy only files referenced by the dump snapshot.
        copy_pdfs(archive, folder / 'pdfs', digests)
        metadata = {'format': 1, 'created_utc': now.isoformat(), 'schema': schema,
                    'database_sha256': file_hash(folder / DUMP), 'pdfs': digests}
        (folder / MANIFEST).write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        folder.rename(completed)
    return completed


def read_manifest(bundle):
    manifest = json.loads((bundle / MANIFEST).read_text(encoding='utf-8'))
    if (not isinstance(manifest, dict) or manifest.get('format') != 1
            or not isinstance(manifest.get('schema'), str)
            or not isinstance(manifest.get('pdfs'), list)
            or any(not isinstance(value, str) or not DIGEST.fullmatch(value) for value in manifest['pdfs'])
            or manifest['pdfs'] != sorted(set(manifest['pdfs']))):
        raise ValueError('Invalid Rollcall backup manifest.')
    return manifest


def verify_backup(bundle):
    manifest = read_manifest(bundle)
    if file_hash(bundle / DUMP) != manifest.get('database_sha256'):
        raise ValueError('Database dump checksum mismatch.')
    for digest in manifest['pdfs']:
        if file_hash(bundle / 'pdfs' / (digest + '.pdf')) != digest:
            raise ValueError(f'PDF checksum mismatch for SHA-256 {digest}.')


def restore_backup(maintenance_connection, new_database, bundle, archive, bin_dir):
    if not re.fullmatch(r'[a-z][a-z0-9_]{0,62}', new_database):
        raise ValueError('Use a new database name with lowercase letters, digits and underscores.')
    archive, bundle = archive.resolve(), bundle.resolve()
    if archive.exists() or archive.is_relative_to(bundle) or bundle.is_relative_to(archive):
        raise ValueError('The restored PDF archive must be a new path outside the backup.')
    manifest = read_manifest(bundle)
    digests = manifest['pdfs']
    with staging(archive.parent) as folder:
        # Restore the verified staged bytes, including when a backup lives on removable media.
        dump = folder / DUMP
        shutil.copyfile(bundle / DUMP, dump)
        if file_hash(dump) != manifest.get('database_sha256'):
            raise ValueError('Database dump checksum mismatch.')
        copy_pdfs(bundle / 'pdfs', folder / 'pdfs', digests)
        with psycopg.connect(maintenance_connection, autocommit=True) as administrator:
            administrator.execute(sql.SQL('CREATE DATABASE {} TEMPLATE template0').format(sql.Identifier(new_database)))
        restored = make_conninfo(maintenance_connection, dbname=new_database)
        run_postgres(bin_dir, 'pg_restore', restored, '--exit-on-error', '--single-transaction',
                     '--no-owner', '--no-privileges', dump)
        with psycopg.connect(restored) as connection:
            if document_digests(connection, manifest['schema']) != digests:
                raise ValueError('Restored document references differ from the backup manifest.')
        (folder / 'pdfs').rename(archive)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--postgres-bin', type=Path)
    modes = parser.add_subparsers(dest='mode', required=True)
    backup = modes.add_parser('backup')
    backup.add_argument('--archive', type=Path, required=True)
    backup.add_argument('--destination', type=Path, required=True)
    restore = modes.add_parser('restore')
    restore.add_argument('--bundle', type=Path, required=True)
    restore.add_argument('--new-database', required=True)
    restore.add_argument('--archive', type=Path, required=True)
    verify = modes.add_parser('verify')
    verify.add_argument('--bundle', type=Path, required=True)
    args = parser.parse_args()
    variable = 'ROLLCALL_BACKUP_DATABASE' if args.mode == 'backup' else 'ROLLCALL_RESTORE_MAINTENANCE_DATABASE'
    connection = os.environ.get(variable)
    try:
        if args.mode == 'verify':
            verify_backup(args.bundle)
            print('Backup checksums verified.')
            return
        if args.postgres_bin is None:
            parser.error('Provide --postgres-bin before the backup or restore command.')
        if not connection or not conninfo_to_dict(connection).get('dbname'):
            parser.error(f'Set {variable} with an explicit database name.')
        if args.mode == 'backup':
            print(f'Backup completed: {create_backup(connection, args.archive, args.destination, args.postgres_bin)}')
        else:
            restore_backup(connection, args.new_database, args.bundle, args.archive, args.postgres_bin)
            print(f'Restore verified: {args.new_database}')
    except (OSError, ValueError, RuntimeError, psycopg.Error) as error:
        detail = str(error) if isinstance(error, (ValueError, RuntimeError)) else type(error).__name__
        parser.exit(1, f'Rollcall {args.mode} failed: {detail}\n')


if __name__ == '__main__':
    main()
