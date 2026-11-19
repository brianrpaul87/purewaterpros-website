"""One-time isolated live launch. Credentials, codes and passwords never leave runner memory.

Requires the existing scoped FTPS bridge and explicit receipt acknowledgements encrypted
for this runner's one-time public key. No mailbox, DNS or parent-site configuration edits.
"""
import base64
import datetime
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from importlib.util import spec_from_file_location, module_from_spec

ORIGIN = 'https://www.purewaterpros.ca'
BASE = ORIGIN + '/childcare-harbour'
CONTACT = 'info@purewaterpros.ca'
BRANCH = 'codex/childcare-deployment-bridge'
REPO = 'brianrpaul87/purewaterpros-website'
CONFIG = 'harbour-private.json'


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load_deployer():
    spec = spec_from_file_location('childcare_deployer', Path(__file__).with_name('deploy-greengeeks.py'))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_settings(prior):
    settings = dict(prior)
    for key in ('dataDirectory', 'liveBackupDirectory'):
        value = settings.get(key)
        if value and not (value == '/home/purewat1/public_html/childcare-harbour/var' or value.startswith('/home/purewat1/public_html/childcare-harbour/var/')):
            raise ValueError('Review application data directory')
        if value and ('..' in value.split('/') or '\\' in value):
            raise ValueError('Review application data directory')
    if settings.get('publicOrigin') not in (None, ORIGIN):
        raise ValueError('Unexpected public origin')
    if settings.get('liveAccountsEnabled') is True:
        raise ValueError('Live accounts are already active; do not replace setup')
    existing = settings.get('livePolicy')
    expected = dict(controllerName='Brian Paul (Childcare Harbour)', contactEmail=CONTACT,
                    retentionDays=90, backupRetentionDays=7, storageReviewed=True, backupsReviewed=True)
    if existing and existing != expected:
        raise ValueError('Existing policy requires review')
    wanted_mail=dict(enabled=True, transport='sendmail', path='/usr/sbin/sendmail', **{'from': CONTACT})
    if settings.get('liveSmtp') and settings['liveSmtp'] != wanted_mail:
        raise ValueError('Existing mail setup requires review')
    settings.update(publicOrigin=ORIGIN, basePath='/childcare-harbour', liveAccountsEnabled=False,
                    liveAuthSecret=settings.get('liveAuthSecret') or secrets.token_urlsafe(32),
                    liveBackupKey=settings.get('liveBackupKey') or secrets.token_hex(32),
                    livePolicy=expected, liveSmtp=dict(enabled=True, transport='sendmail',
                    path='/usr/sbin/sendmail', **{'from': CONTACT}))
    if len(settings['liveAuthSecret']) < 32 or not re.fullmatch('[a-fA-F0-9]{64}', settings['liveBackupKey']):
        raise ValueError('Invalid existing private keys')
    return settings


class Host:
    def __init__(self):
        self.deployer = load_deployer()
        self.expected = None

    def connect(self):
        ftp = ftplib.FTP_TLS(context=ssl.create_default_context(), timeout=45)
        ftp.connect('mtl203.greengeeks.net', 21)
        ftp.login(os.environ['GREENGEEKS_FTP_USERNAME'], os.environ['GREENGEEKS_FTP_PASSWORD'])
        ftp.prot_p()
        folder = self.deployer.ChildcareFolder(ftp, os.environ.get('GREENGEEKS_REMOTE_ROOT', '/'))
        if json.loads(self.deployer.read(folder, 'package.json')).get('name') != 'childcare-harbour':
            ftp.close()
            raise ValueError('Wrong app')
        return ftp, folder

    def read_settings(self):
        ftp, folder = self.connect()
        try:
            value = self.deployer.read(folder, CONFIG)
            if len(value) > 65536:
                raise ValueError('Unexpected config size')
            settings = json.loads(value)
            self.expected = json.loads(json.dumps(settings))
            return settings
        finally:
            ftp.close()

    def write_settings(self, settings):
        ftp, folder = self.connect()
        temporary = 'var/live-config-' + uuid.uuid4().hex + '.json'
        data = (json.dumps(settings, indent=2) + '\n').encode()
        locked = False
        try:
            folder.mkd('.harbour-deploy/live-setup-lock')
            locked = True
            current = json.loads(self.deployer.read(folder, CONFIG))
            if self.expected is None or current != self.expected:
                raise ValueError('Private settings changed; preserve the newer configuration')
            # The temporary file is inside protected var; permissions are set before secrets.
            folder.storbinary('STOR ' + temporary, io.BytesIO(b''))
            ftp.sendcmd('SITE CHMOD 600 ' + folder.path(temporary))
            folder.storbinary('STOR ' + temporary, io.BytesIO(data))
            if self.deployer.read(folder, temporary) != data:
                raise ValueError('Private settings readback failed')
            folder.rename(temporary, CONFIG)
            ftp.sendcmd('SITE CHMOD 600 ' + folder.path(CONFIG))
            if self.deployer.read(folder, CONFIG) != data:
                raise ValueError('Private settings promotion failed')
            self.deployer.put(folder, 'tmp/restart.txt', ('live-launch-' + uuid.uuid4().hex + '\n').encode())
            self.expected = json.loads(json.dumps(settings))
        finally:
            if locked:
                folder.rmd('.harbour-deploy/live-setup-lock')
            ftp.close()


def api(path, body=None, secret=None, cookie=None, expected=200):
    headers = {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
    if body is not None:
        headers.update({'Content-Type': 'application/json', 'Origin': ORIGIN})
    if secret:
        headers['Authorization'] = 'Bearer ' + secret
    if cookie:
        headers['Cookie'] = cookie
    request = urllib.request.Request(BASE + '/api/live' + path,
               data=json.dumps(body).encode() if body is not None else None, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=45)
    except urllib.error.HTTPError as error:
        if error.code != expected:
            raise RuntimeError('Hosted request failed') from None
        response = error
    with response:
        if response.code != expected:
            raise RuntimeError('Unexpected hosted response')
        result = json.loads(response.read(65536))
        session = (response.headers.get('Set-Cookie') or '').split(';')[0]
        return result, session


def wait_status(enabled):
    for _ in range(35):
        try:
            status, _ = api('/status')
            if status.get('accountsAvailable') is True and status.get('enabled') is enabled:
                return status
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError('App restart did not reach the expected state')


class Exchange:
    def __init__(self, prefix):
        if not re.fullmatch('[a-z0-9-]{8,70}', prefix):
            raise ValueError('Invalid one-time launch prefix')
        self.prefix = prefix
        self.directory = tempfile.TemporaryDirectory(prefix='childcare-launch-')
        self.key = Path(self.directory.name) / 'private.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:3072',
                       '-out', str(self.key)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        public = subprocess.check_output(['openssl', 'pkey', '-in', str(self.key), '-pubout'])
        self.publish('mail-public.pem', public)

    def url(self, suffix):
        return 'https://api.github.com/repos/' + REPO + '/contents/childcare-bridge/' + self.prefix + '-' + suffix

    def request(self, url, data=None, method=None):
        request = urllib.request.Request(url, data=data, method=method,
                    headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                             'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
        return urllib.request.urlopen(request, timeout=25)

    def publish(self, suffix, content):
        payload = dict(message='Publish one-time Childcare launch progress',
                       content=base64.b64encode(content).decode(), branch=BRANCH)
        try:
            with self.request(self.url(suffix) + '?ref=codex%2Fchildcare-deployment-bridge') as response:
                payload['sha'] = json.load(response)['sha']
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
        with self.request(self.url(suffix), json.dumps(payload).encode(), 'PUT') as response:
            if response.status not in (200, 201):
                raise RuntimeError('Progress publication failed')

    def wait(self, phase):
        self.publish('progress.json', json.dumps({'phase': phase, 'startedAt': stamp()}).encode())
        for _ in range(100):
            try:
                with self.request(self.url(phase + '.json') + '?ref=codex%2Fchildcare-deployment-bridge') as response:
                    value = json.loads(base64.b64decode(json.load(response)['content']))
                encrypted = base64.b64decode(value['ciphertext'], validate=True)
                result = subprocess.run(['openssl', 'pkeyutl', '-decrypt', '-inkey', str(self.key),
                         '-pkeyopt', 'rsa_padding_mode:oaep', '-pkeyopt', 'rsa_oaep_md:sha256'],
                         input=encrypted, capture_output=True, check=True)
                reply = json.loads(result.stdout)
                if phase == 'delivery' and reply == {'received': True}:
                    return reply
                if phase in ('verification', 'reset') and set(reply) == {'code'} and re.fullmatch('[0-9]{8}', reply['code']):
                    return reply['code']
                raise ValueError('Invalid encrypted launch response')
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
            time.sleep(3)
        raise TimeoutError('Inbox acknowledgement did not arrive')

    def close(self):
        self.directory.cleanup()


def main():
    host = Host()
    exchange = None
    configured = False
    completed = False
    cookie = None
    password = None
    try:
        settings = prepare_settings(host.read_settings())
        host.write_settings(settings)
        configured = True
        wait_status(False)
        result, _ = api('/admin/mail-test', {'confirmSend': True, 'contactEmail': CONTACT}, secret=settings['liveAuthSecret'])
        if result.get('queued') is not True or result.get('backupVerified') is not True:
            raise RuntimeError('Private mail/backup test failed')
        print('PASS: private settings prepared, encrypted backup verified and setup email queued. Awaiting actual inbox receipt.', flush=True)
        exchange = Exchange(os.environ['LAUNCH_PREFIX'])
        exchange.wait('delivery')
        evidence = {'mailReceiptConfirmedAt': stamp()}
        settings['liveAccountsEnabled'] = True
        host.write_settings(settings)
        status = wait_status(True)
        password = secrets.token_urlsafe(32)
        signup, _ = api('/signup', dict(email=CONTACT, role='parent', displayName='Childcare Harbour launch check',
                         password=password, consent=True, noticeVersion=status['notice']['version']))
        code = exchange.wait('verification')
        api('/verify', {'requestId': signup['requestId'], 'code': code})
        login, cookie = api('/login', {'email': CONTACT, 'role': 'parent', 'password': password})
        if login['account']['displayName'] != 'Childcare Harbour launch check':
            raise RuntimeError('Unexpected test identity')
        identity_id = login['account']['id']
        evidence['signupVerifiedAt'] = stamp()
        search_id = str(uuid.uuid4())
        saved, _ = api('/saved-searches', dict(operation='save', id=search_id, label='Launch check',
                     query={'area': 'Westshore', 'days': ['Mon'], 'start': '09:00', 'end': '16:00'},
                     expectedRevision=0), cookie=cookie)
        if saved.get('backupPending'):
            raise RuntimeError('Backup check failed')
        api('/logout', {}, cookie=cookie)
        login, cookie = api('/login', {'email': CONTACT, 'role': 'parent', 'password': password})
        if login['account']['savedSearches'][0]['id'] != search_id:
            raise RuntimeError('Saved search did not survive login')
        reset, _ = api('/recover', {'email': CONTACT, 'role': 'parent'})
        code = exchange.wait('reset')
        new_password = secrets.token_urlsafe(32)
        api('/reset', {'requestId': reset['requestId'], 'code': code, 'password': new_password})
        if api('/account', cookie=cookie)[0].get('account') is not None:
            raise RuntimeError('Old session survived recovery')
        api('/login', {'email': CONTACT, 'role': 'parent', 'password': password}, expected=401)
        password = new_password
        login, cookie = api('/login', {'email': CONTACT, 'role': 'parent', 'password': password})
        if login['account']['id'] != identity_id:
            raise RuntimeError('Recovery selected another account')
        evidence['recoveryVerifiedAt'] = stamp()
        deleted, _ = api('/account/delete', {'password': password}, cookie=cookie)
        if deleted.get('ok') is not True or deleted.get('backupPending'):
            raise RuntimeError('Deletion or backup redaction failed')
        if api('/account', cookie=cookie)[0].get('account') is not None:
            raise RuntimeError('Deleted account remained available')
        cookie = None
        evidence.update(deletionVerifiedAt=stamp(), completedAt=stamp())
        settings['liveLaunchEvidence'] = evidence
        host.write_settings(settings)
        wait_status(True)
        exchange.publish('progress.json', json.dumps({'phase': 'complete', 'completedAt': stamp(),
                         'signup': True, 'recovery': True, 'savedSearch': True, 'testAccountDeleted': True}).encode())
        completed = True
        print('PASS: actual inbox delivery, hosted signup/verification/login, saved search persistence, password recovery/session revocation, account deletion and encrypted backup redaction. Public registration is active. The temporary test account was deleted.', flush=True)
    finally:
        if configured and not completed:
            try:
                if password:
                    try:
                        _, cleanup_cookie = api('/login', {'email': CONTACT, 'role': 'parent', 'password': password})
                        api('/account/delete', {'password': password}, cookie=cleanup_cookie)
                    except Exception:
                        pass
                latest = host.read_settings()
                if latest.get('liveAuthSecret') != settings['liveAuthSecret']:
                    raise RuntimeError('A newer launch configuration needs inspection')
                latest['liveAccountsEnabled'] = False
                host.write_settings(latest)
                wait_status(False)
                print('New registration closed; private setup and existing account access preserved.', flush=True)
            except Exception:
                print('Launch recovery needs inspection; activation is not established.', flush=True)
        if exchange:
            exchange.close()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Live launch did not finish. No credentials, passwords or email codes were printed.', flush=True)
        raise SystemExit(1)
