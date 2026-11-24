"""Create a source-only checkpoint, excluding configuration secrets and customer data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import argparse
import os

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--name', default='stage1-2026-10-30')
args = parser.parse_args()
if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.name):
    raise SystemExit('Checkpoint name must contain only letters, numbers, hyphens, or underscores.')

root = Path(__file__).resolve().parents[1]
destination = root / 'checkpoints'
destination.mkdir(exist_ok=True)
archive = destination / (args.name + '.zip')
if archive.exists():
    raise SystemExit('Checkpoint already exists; use a new version rather than overwrite it.')
allowed_suffixes = {'.md', '.py', '.jsx', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.css', '.html', '.json', '.yaml', '.txt'}
excluded_directories = {'node_modules', 'dist', '__pycache__', '.pytest_cache', '.venv', '.git', 'data', 'archive', 'stage2-private'}
files = [p for p in root.iterdir() if p.is_file() and (p.suffix == '.md' or p.name in {'.gitignore', '.env.example', 'compose.yaml'})]
for directory in ['backend', 'frontend', 'docs', 'work']:
    for folder, folders, filenames in os.walk(root / directory):
        # Prune before descent: walking the entire dependency store is unnecessary.
        folders[:] = [name for name in folders if name not in excluded_directories]
        for filename in filenames:
            file = Path(folder) / filename
            if file.name == '.env' or file.name.startswith('.env.') and file.name != '.env.example':
                continue
            if file.suffix in allowed_suffixes or file.name == '.env.example':
                files.append(file)
files += list((root / 'output' / 'playwright').glob('stage1-*.png'))
with ZipFile(archive, 'x', compression=ZIP_DEFLATED) as output:
    for file in sorted(files):
        output.write(file, file.relative_to(root).as_posix())
with ZipFile(archive) as output:
    assert output.testzip() is None
    names = output.namelist()
    assert not any(Path(name).name == '.env' for name in names)
    assert not any('isolated-postgres/' in name or 'node_modules/' in name for name in names)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
manifest = {'archive': archive.name, 'sha256': digest, 'file_count': len(names), 'files': names,
            'scope': 'source, project documents, credential-free evidence summary, screenshots; excludes secrets, dependencies, build output, database files'}
(destination / (args.name + '.manifest.json')).write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f'PASS: checkpoint ZIP verified, {len(names)} files, SHA256 {digest}')
