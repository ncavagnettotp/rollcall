"""Build the versioned Windows rehearsal ZIP from the verified Electron distribution."""

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile


DESKTOP = Path(__file__).resolve().parent
ELECTRON_SHA256 = '2ba6223afa9121f42831fefe92c434334907540165294fc56697449d12e7cfe9'


def sha256(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runtime_zip', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if sha256(args.runtime_zip) != ELECTRON_SHA256:
        parser.error('Electron runtime does not match the pinned Windows x64 checksum.')

    version = json.loads((DESKTOP / 'package.json').read_text(encoding='utf-8'))['version']
    args.output.mkdir(parents=True, exist_ok=True)
    result = args.output / f'Rollcall-{version}-win-x64-rehearsal.zip'
    with TemporaryDirectory(dir=args.output) as folder:
        staged = Path(folder) / result.name
        with ZipFile(args.runtime_zip) as electron, ZipFile(staged, 'w', ZIP_DEFLATED) as package:
            for entry in electron.infolist():
                if entry.is_dir() or entry.filename == 'resources/default_app.asar':
                    continue
                filename = 'Rollcall.exe' if entry.filename == 'electron.exe' else entry.filename
                package.writestr('client/' + filename, electron.read(entry))
            for filename in ('package.json', 'main.cjs', 'policy.cjs'):
                package.write(DESKTOP / filename, 'client/resources/app/' + filename)
            package.write(DESKTOP / 'Install-Rollcall.ps1', 'Install-Rollcall.ps1')
        staged.replace(result)
    result.with_suffix('.zip.sha256').write_text(f'{sha256(result)}  {result.name}\n', encoding='ascii')
    print(result)


if __name__ == '__main__':
    main()
