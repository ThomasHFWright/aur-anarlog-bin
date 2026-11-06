#!/usr/bin/env python3
"""Follow upstream packaging metadata; never import changed build instructions."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

BASE = 'https://api.github.com/repos/fastrepl/anarlog'
FIELDS = {
    'pkgver': r'\d+\.\d+\.\d+',
    'pkgrel': r'\d+',
    'sha256sums': r"\('[a-f0-9]{64}'\)",
    'sha256sums_x86_64': r"\('[a-f0-9]{64}'\)",
    'sha256sums_aarch64': r"\('[a-f0-9]{64}'\)",
}


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'aur-anarlog-bin-updater'})
    return urllib.request.urlopen(request, timeout=120)


def metadata(recipe):
    values = {}
    for key, pattern in FIELDS.items():
        matches = re.findall(rf'^{key}=({pattern})$', recipe, re.M)
        if len(matches) != 1:
            raise ValueError(f'Invalid or duplicate {key}')
        values[key] = matches[0]
    return values


def skeleton(recipe):
    for key, pattern in FIELDS.items():
        recipe = re.sub(rf'^{key}={pattern}$', key + '=METADATA', recipe, flags=re.M)
    return '\n'.join(line for line in recipe.splitlines() if not line.startswith('#'))


def update_recipe(current, upstream):
    values = metadata(upstream)
    metadata(current)
    if skeleton(current) != skeleton(upstream):
        raise ValueError('Upstream build instructions changed; review required')
    for key, value in values.items():
        current = re.sub(rf'^{key}={FIELDS[key]}$', key + '=' + value, current, flags=re.M)
    return current


def self_test():
    current = Path('PKGBUILD').read_text()
    upstream = current.replace('pkgver=' + metadata(current)['pkgver'], 'pkgver=99.0.0')
    assert metadata(update_recipe(current, upstream))['pkgver'] == '99.0.0'
    for bad in [upstream + '\necho unreviewed\n', upstream.replace('pkgver=99.0.0', 'pkgver=$(id)'),
                upstream + '\npkgrel=1\n', upstream.replace("options=('!strip')", "options=('strip')")]:
        try:
            update_recipe(current, bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Accepted unexpected upstream instructions')
    print('PASS metadata-only updates and rejection of changed build instructions')


def verify_arm64():
    values = metadata(Path('PKGBUILD').read_text())
    url = f'https://github.com/fastrepl/anarlog/releases/download/desktop_v{values["pkgver"]}/anarlog-linux-aarch64.deb'
    digest = hashlib.sha256()
    with fetch(url) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
    if digest.hexdigest() != values['sha256sums_aarch64'][2:-2]:
        raise ValueError('ARM64 release checksum mismatch')
    print('PASS ARM64 release checksum')


def main():
    if sys.argv[1:] == ['--self-test']:
        return self_test()
    if sys.argv[1:] == ['--verify-arm64']:
        return verify_arm64()
    with fetch(BASE + '/commits?path=packaging/aur/anarlog-bin/PKGBUILD&per_page=1') as response:
        commit = json.load(response)[0]['sha']
    if not re.fullmatch('[a-f0-9]{40}', commit):
        raise ValueError('Invalid upstream commit')
    with fetch(f'https://raw.githubusercontent.com/fastrepl/anarlog/{commit}/packaging/aur/anarlog-bin/PKGBUILD') as response:
        upstream = response.read().decode()
    path = Path('PKGBUILD')
    current = path.read_text()
    updated = update_recipe(current, upstream)
    values = metadata(updated)
    with fetch(BASE + '/releases/tags/desktop_v' + values['pkgver']) as response:
        release = json.load(response)
    if release['draft'] or release['prerelease']:
        raise ValueError('Expected a published stable release')
    old = metadata(current)
    before = f'{old["pkgver"]}-{old["pkgrel"]}'
    after = f'{values["pkgver"]}-{values["pkgrel"]}'
    comparison = int(subprocess.check_output(['vercmp', after, before]))
    if comparison < 0:
        raise ValueError('Refusing an upstream downgrade')
    if comparison == 0 and updated != current:
        raise ValueError('Checksums changed without a version bump; review required')
    path.write_text(updated)
    Path('.SRCINFO').write_bytes(subprocess.check_output(['makepkg', '--printsrcinfo']))
    print(f'Upstream {commit[:12]}: {after}; build must pass before publication')


if __name__ == '__main__':
    main()
