"""Offline maintenance. Stop Mahrukh before backup or personal-data redaction."""
import argparse
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sqlite3
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent


def backup(instance):
    """SQLite backup API makes a consistent database copy; assets/config accompany it."""
    folder = instance / 'backups'
    folder.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = folder / f'mahrukh-{stamp}.tar.gz'
    with tempfile.TemporaryDirectory(dir=instance) as tmp:
        copy = Path(tmp) / 'mahrukh.sqlite3'
        with sqlite3.connect(instance / 'mahrukh.sqlite3') as source, sqlite3.connect(copy) as dest:
            source.backup(dest)
        with tarfile.open(target, 'w:gz') as archive:
            archive.add(copy, arcname='mahrukh.sqlite3')
            for name in ('config.json', 'uploads'):
                if (instance / name).exists(): archive.add(instance / name, arcname=name)
    target.chmod(0o600)
    return target


def redact(instance, days, apply=False):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec='seconds')
    with sqlite3.connect(instance / 'mahrukh.sqlite3') as db:
        clause = "status IN ('completed','cancelled') AND payment_status != 'paid' AND updated_at < ? AND name != '[redacted]'"
        # Completed paid orders can be retained for accounting; explicitly review them separately.
        count = db.execute('SELECT count(*) FROM orders WHERE ' + clause, (cutoff,)).fetchone()[0]
        if apply:
            db.execute("UPDATE orders SET name='[redacted]',contact='',address='',city='',owner='',source_hash='',payment_reference='',tracking='',payment_url='',version=version+1 WHERE " + clause, (cutoff,))
    return count


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('backup','redact'))
    parser.add_argument('--days',type=int,default=365,help='Only redact eligible records older than this many days (default 365).')
    parser.add_argument('--apply',action='store_true',help='Actually redact; without this flag only count matching records.')
    args = parser.parse_args()
    instance = Path(os.environ.get('MAHRUKH_INSTANCE',str(ROOT / 'instance'))).resolve()
    if not (instance / 'mahrukh.sqlite3').is_file(): parser.error('No Mahrukh database found. Run setup first.')
    if args.action == 'backup': print('Private backup saved:', backup(instance))
    else:
        if args.days < 1: parser.error('--days must be at least 1')
        count = redact(instance,args.days,args.apply)
        print(f'{count} eligible closed records ' + ('redacted.' if args.apply else 'would be redacted. No data changed.'))
        print('Paid records are excluded. Review accounting obligations, disputes, backups and provider records separately.')

if __name__ == '__main__': main()
