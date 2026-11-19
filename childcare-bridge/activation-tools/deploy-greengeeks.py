"""Deploy only the verified runtime through a fixed FTPS subfolder boundary.

No shell access, remote deletion, recursive sync, private settings or cPanel edits.
"""
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import ssl
import sys
import urllib.request

HOST = 'mtl203.greengeeks.net'
TARGET = '/home/purewat1/public_html/childcare-harbour'
FILES = tuple(sorted(['server.cjs', 'server.mjs', 'package.json', '.htaccess',
    'src/file-store.js', 'src/live-search.js', 'src/live-accounts.js', 'src/live-backups.js', 'src/live-launch.mjs', 'dist/transactional-mail.js', 'dist/mail-NOTICE.txt', 'src/early-access.js', 'src/accounts.js', 'src/hosted-ai.js', 'src/domain.js', 'src/seed.js',
    'dist/assets.js', 'dist/worker.js', 'dist/domain.js', 'dist/seed.js', 'dist/demo-assistant.js']))
STAGE = '.harbour-deploy'

class ChildcareFolder:
    """Translate every FTP operation into the fixed Childcare Harbour subfolder.

    Supports the existing account without reading or writing the parent website.
    """
    def __init__(self, ftp, remote_root='/'):
        root = remote_root.rstrip('/')
        if root not in ('', '/public_html', '/home/purewat1/public_html'):
            raise ValueError('Unrecognized existing FTP root')
        self.ftp = ftp
        self.root = root + '/childcare-harbour'
        ftp.cwd(self.root)
        if ftp.pwd().rstrip('/') != self.root:
            raise ValueError('Childcare directory could not be verified')
    def path(self, path):
        if path == '/': return self.root
        if not path or path.startswith('/') or any(p in ('', '.', '..') for p in path.split('/')) or '\\' in path or any(ord(c) < 32 for c in path):
            raise ValueError('Unsafe deployment path')
        return self.root + '/' + path
    def pwd(self):
        if self.ftp.pwd().rstrip('/') != self.root:
            raise ValueError('FTP directory changed unexpectedly')
        return '/'
    def cwd(self, path): return self.ftp.cwd(self.path(path))
    def mkd(self, path): return self.ftp.mkd(self.path(path))
    def rmd(self, path): return self.ftp.rmd(self.path(path))
    def rename(self, source, target): return self.ftp.rename(self.path(source), self.path(target))
    def retrbinary(self, command, write):
        if not command.startswith('RETR '): raise ValueError('Unexpected FTP command')
        return self.ftp.retrbinary('RETR ' + self.path(command[5:]), write)
    def storbinary(self, command, stream):
        if not command.startswith('STOR '): raise ValueError('Unexpected FTP command')
        return self.ftp.storbinary('STOR ' + self.path(command[5:]), stream)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def release_files(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Invalid release directory')
    entries = list(root.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Release symlink')
    files = {p.relative_to(root).as_posix(): p.read_bytes() for p in entries if p.is_file()}
    if set(files) != set(FILES) | {'release-manifest.json'}:
        raise ValueError('Release allowlist mismatch')
    manifest = json.loads(files['release-manifest.json'])
    if manifest.get('schema') != 1 or manifest.get('entry') != 'server.cjs' or manifest.get('basePath') != '/childcare-harbour':
        raise ValueError('Invalid release manifest')
    if [r['path'] for r in manifest['files']] != list(FILES):
        raise ValueError('Manifest paths mismatch')
    for record in manifest['files']:
        data = files[record['path']]
        if record['bytes'] != len(data) or record['sha256'] != digest(data):
            raise ValueError('Release integrity mismatch')
    if json.loads(files['package.json']).get('name') != 'childcare-harbour':
        raise ValueError('Wrong application')
    return files

def read(ftp, path, optional=False):
    data = io.BytesIO()
    try:
        ftp.retrbinary('RETR ' + path, data.write)
    except ftplib.error_perm as error:
        if optional and str(error).startswith('550'):
            return None
        raise
    return data.getvalue()

def mkdir(ftp, path):
    try:
        ftp.mkd(path)
    except ftplib.error_perm:
        # Verify an existing directory instead of interpreting every error as existence.
        ftp.cwd(path)
        ftp.cwd('/')

def put(ftp, path, data):
    parent = path.rsplit('/', 1)[0] if '/' in path else ''
    current = ''
    for part in parent.split('/') if parent else []:
        current = part if not current else current + '/' + part
        mkdir(ftp, current)
    ftp.storbinary('STOR ' + path, io.BytesIO(data))
    if read(ftp, path) != data:
        raise ValueError('Remote verification failed')

def deploy(ftp, files, revision):
    if set(files) != set(FILES) | {'release-manifest.json'}:
        raise ValueError('Unexpected deployment paths')
    if not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('Invalid revision')
    if ftp.pwd() != '/':
        raise ValueError('Deployment account must start at its restricted root')
    if json.loads(read(ftp, 'package.json')).get('name') != 'childcare-harbour':
        raise ValueError('Remote root is not Childcare Harbour')
    rules = read(ftp, '.htaccess').decode()
    required = [line.strip() for line in files['.htaccess'].decode().splitlines() if line.strip() and not line.startswith('#')]
    if any(line not in [r.strip() for r in rules.splitlines()] for line in required):
        raise ValueError('Existing hosting protections require review')
    mkdir(ftp, STAGE)
    put(ftp, STAGE + '/.htaccess', b'Require all denied\n')
    # A failed lock must fail closed. Never remove another deployment's lock.
    ftp.mkd(STAGE + '/lock')
    changed = []
    backup = {}
    unlock = True
    stage = STAGE + '/releases/' + revision
    try:
        names = sorted(set(files) - {'.htaccess'})
        for name in names:
            backup[name] = read(ftp, name, optional=True)
            if backup[name] is not None:
                put(ftp, stage + '/previous/' + name, backup[name])
            put(ftp, stage + '/next/' + name, files[name])
        # No removals or writes to private files, var, .htaccess or parent paths.
        for name in names:
            changed.append(name)
            ftp.rename(stage + '/next/' + name, name)
        for name in names:
            if read(ftp, name) != files[name]:
                raise ValueError('Published bytes differ')
        put(ftp, 'tmp/restart.txt', (revision + '\n').encode())
    except Exception:
        # Restore every prior runtime byte; newly added allowlisted files are inert
        # under the previous runtime and are retained (never delete remotely).
        try:
            for name in reversed(changed):
                if backup.get(name) is not None:
                    put(ftp, name, backup[name])
            if changed:
                put(ftp, 'tmp/restart.txt', b'rollback\n')
        except Exception:
            unlock = False  # Retain the lock when recovery cannot be verified.
            raise
        raise
    finally:
        # This is our own empty directory lock only, not application data locks.
        if unlock:
            ftp.rmd(STAGE + '/lock')

def verify_http(files, revision):
    text = files['dist/assets.js'].decode()
    expected = re.search(r'app\.js\?v=([a-f0-9]{16})', text)
    if not expected:
        raise ValueError('Missing asset version')
    url = 'https://www.purewaterpros.ca/childcare-harbour/?deployment=' + revision
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read(2_000_000).decode()
        if response.status != 200 or not any(asset + '?v=' + expected[1] in body for asset in ('app.js', 'join.js')):
            raise ValueError('Hosted version not verified')

def main():
    files = release_files('.local/greengeeks-release')
    revision = os.environ.get('GITHUB_SHA', '')
    username = os.environ.get('GREENGEEKS_FTP_USERNAME')
    password = os.environ.get('GREENGEEKS_FTP_PASSWORD')
    if not username or not password:
        raise ValueError('Existing deployment credentials are not configured')
    with ftplib.FTP_TLS(context=ssl.create_default_context(), timeout=60) as ftp:
        ftp.connect(HOST, 21)
        ftp.login(username, password)
        ftp.prot_p()
        deploy(ChildcareFolder(ftp, os.environ.get('GREENGEEKS_REMOTE_ROOT', '/')), files, revision)
    verify_http(files, revision)
    print('Verified runtime published to Childcare Harbour; private settings and records preserved.')

if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Server errors and connection exceptions can contain account details.
        print('Deployment failed. Check access, target protections and retained staging backups; hosted success is not established.', file=sys.stderr)
        sys.exit(1)
