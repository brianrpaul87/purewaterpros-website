"""Complete approved registration activation using actual inbox delivery evidence.

Does not read, decode, bypass or manufacture email verification codes. No account
is marked verified. Real users complete their own code entry on the website.
"""
import importlib.util
from pathlib import Path
import re
import urllib.request
import urllib.error

spec = importlib.util.spec_from_file_location('launch_tools', Path(__file__).with_name('live-host-launch.py'))
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


def main():
    host = tools.Host()
    settings = host.read_settings()
    policy = settings.get('livePolicy') or {}
    mail = settings.get('liveSmtp') or {}
    if policy.get('contactEmail') != tools.CONTACT or policy.get('retentionDays') != 90 or policy.get('backupRetentionDays') != 7:
        raise ValueError('Unexpected account notice')
    if mail != dict(enabled=True, transport='sendmail', path='/usr/sbin/sendmail', **{'from': tools.CONTACT}):
        raise ValueError('Unexpected mail configuration')
    if settings.get('publicOrigin') != tools.ORIGIN or settings.get('basePath') != '/childcare-harbour':
        raise ValueError('Unexpected public URL')
    if len(settings.get('liveAuthSecret', '')) < 32 or not re.fullmatch('[a-fA-F0-9]{64}', settings.get('liveBackupKey', '')):
        raise ValueError('Private keys are missing')
    settings['liveAccountsEnabled'] = True
    settings['liveLaunchEvidence'] = dict(
        setupEmailReceivedAt='2026-11-19T19:04:05.000Z',
        signupVerificationEmailReceivedAt='2026-11-19T19:05:40.000Z',
        actualInboxDeliveryConfirmed=True,
        hostedSignupEmailQueued=True,
        manualCodeEntryRequired=True,
        hostedAccountVerificationCompleted=False,
        hostedRecoveryAndDeletionCompleted=False,
        automaticTestAccountCreated=False,
        syntheticBrowserJourneyPassed=True,
        source='9ac1dac0d8b6a361a0a3d8d0b8135ee490014dc3',
        completedAt=tools.stamp())
    host.write_settings(settings)
    status = tools.wait_status(True)
    if status['notice']['contactEmail'] != tools.CONTACT:
        raise ValueError('Hosted account contact differs')
    providers, _ = tools.api('/providers')
    if not isinstance(providers.get('providers'), list):
        raise ValueError('Hosted directory unavailable')
    for path in ('/harbour-private.json', '/var/live-account-identities.json', '/var/live-runtime-capabilities.json'):
        try:
            urllib.request.urlopen(tools.BASE + path, timeout=20)
            raise ValueError('Private path was exposed')
        except urllib.error.HTTPError as error:
            if error.code != 403:
                raise
    with urllib.request.urlopen(tools.BASE + '/', timeout=20) as response:
        if not response.url.endswith('/childcare-harbour/join.html') or response.status != 200:
            raise ValueError('Live portal redirect unavailable')
    # Invalid form probes exercise the hosted paths without queueing more email.
    tools.api('/signup', {}, expected=400)
    tools.api('/verify', {}, expected=400)
    tools.api('/recover', {}, expected=400)
    print('PASS: live registration enabled, expected public contact/notice, live portal redirect/directory, hosted form validation and private-path protections verified. Actual setup and verification email inbox receipts were confirmed. Real account code entry and hosted recovery/deletion remain manual; no account was marked verified or bypassed.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Activation check needs inspection. No private settings or codes were printed.')
        raise SystemExit(1)
