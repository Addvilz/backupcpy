import argparse
import traceback

import yaml
import os
import re
import glob
import tarfile
import datetime
import fnmatch

start_time = datetime.datetime.utcnow()
start_time_str = start_time.strftime('%Y%m%d-%H%M%S-%f')

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

runtime_vars = {
    '{{now}}': start_time_str,
    '{{cwd}}': os.getcwd(),
    '{{home}}': os.path.expanduser('~'),
    '{{user}}': os.getlogin()
}

compression_profiles = {
    'none': {
        'ext': '.tar',
        'mode': 'w'
    },
    'gz': {
        'ext': '.tar.gz',
        'mode': 'w:gz'
    },
    'xz': {
        'ext': '.tar.xz',
        'mode': 'w:xz'
    },
    'bz2': {
        'ext': '.tar.bz2',
        'mode': 'w:bz2'
    }
}


class BackupError(Exception):
    pass


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def replace_vars(text):
    regex = re.compile('|'.join(map(re.escape, runtime_vars.keys())))
    return regex.sub(lambda match: runtime_vars[match.group(0)], text)


def ignore_list(manifest, col_manifest):
    global_ignore = [] if 'ignore' not in manifest else manifest['ignore']
    local_ignore = [] if 'ignore' not in col_manifest else col_manifest['ignore']
    return list(map(lambda it: replace_vars(it), set().union(global_ignore, local_ignore)))


def ignore_match(file, ignore):
    for ignored in ignore:
        if fnmatch.fnmatch(file, ignored):
            return True
    return False


def load_manifest(file):
    if not os.path.exists(file):
        raise BackupError('File does not exist - %s' % file)

    with open(file, mode='r', encoding='utf-8') as stream:
        return yaml.load(stream, Loader)


def process_collection(args, manifest, collection):
    col_manifest = manifest['collections'][collection]

    if 'items' not in col_manifest:
        raise BackupError('Invalid manifest - collection has no items')

    if 'target' not in col_manifest:
        raise BackupError('Invalid manifest - collection has no target')

    if 'compress' not in col_manifest:
        raise BackupError('Invalid manifest - collection has no compression preference')

    if col_manifest['compress'] not in compression_profiles:
        raise BackupError('Invalid manifest - unknown compression profile %s' % col_manifest['compress'])

    ignore = ignore_list(manifest, col_manifest)
    compression_profile = compression_profiles[col_manifest['compress']]

    items = col_manifest['items']
    target_path = replace_vars(col_manifest['target'])
    col_target_path = os.path.join(target_path, collection)

    if not args.quiet:
        print('Archive will be created in %s' % col_target_path)

    os.makedirs(col_target_path, mode=0o700, exist_ok=True)

    archive_file_path = os.path.join(
        col_target_path,
        '%s-%s%s' % (collection, start_time_str, compression_profile['ext'])
    )

    if args.verbose:
        print('Archive file is %s' % archive_file_path)

    archive = tarfile.open(archive_file_path, compression_profile['mode'])

    parsed_paths = map(
        lambda it: replace_vars(it),
        items
    )

    files_ignored = 0
    files_selected_size = 0
    files = []

    if not args.quiet:
        print('Collecting and resolving files - this might take a while...')

    for path in parsed_paths:
        if ignore_match(path, ignore):
            files_ignored += 1
            if args.debug:
                print('Ignoring %s' % path)

            continue

        globs = glob.glob(path, recursive=True)

        for file in globs:
            if os.path.isdir(file):
                continue

            if os.path.islink(file):
                # Broken link
                if not os.path.exists(file):
                    continue

            if ignore_match(file, ignore):
                files_ignored += 1
                if args.debug:
                    print('Ignoring %s' % file)
                continue

            file_size = os.path.getsize(file)

            files.append({
                'path': file,
                'size': file_size
            })
            files_selected_size += file_size

    files_selected = len(files)
    files_added = 0
    files_added_size = 0
    for file in files:
        if args.verbose:
            print('Adding %s' % file['path'])
        elif not args.quiet:
            print('Archived %d of %d files, total of %s of %s.'
                  % (files_added, files_selected, sizeof_fmt(files_added_size), sizeof_fmt(files_selected_size)),
                  end="\r")

        archive.add(file['path'], file['path'])
        files_added += 1
        files_added_size += file['size']

    archive.close()

    if not args.verbose and not args.quiet:
        print()

    archive_size = os.path.getsize(archive_file_path)

    if not args.quiet:
        print('%d files resolved, %d added, %d ignored.\nFile size %s. Archive size %s.'
              % (files_selected, files_added, files_ignored, sizeof_fmt(files_added_size), sizeof_fmt(archive_size)))


def backup_do(args):
    if not args.quiet:
        print('Loading manifest from %s' % args.manifest)

    manifest = load_manifest(args.manifest)

    if 'collections' not in manifest:
        raise BackupError('Invalid manifest - missing collections')

    for collection in args.collection:
        if collection not in manifest['collections']:
            raise BackupError('Unknown collection %s' % collection)

        if not args.quiet:
            print('Processing collection %s' % collection)

        process_collection(args, manifest, collection)

    if not args.quiet:
        print('Done')


def main():
    parser = argparse.ArgumentParser(description='Assemble backup archives')
    parser.add_argument(
        'collection',
        nargs='+',
        help='Collections to backup'
    )
    parser.add_argument(
        '--manifest',
        help='Manifest file (defaults to ~/.backupcpy.yml)',
        default=os.path.expanduser('~/.backupcpy.yml')
    )
    parser.add_argument('--verbose', action='store_true', help='Verbosely report what files are archived')
    parser.add_argument('--debug', action='store_true', help='Produce more verbose debug output')
    parser.add_argument('--quiet', action='store_true', help='Do not write progress and status')

    args = parser.parse_args()
    # noinspection PyBroadException
    try:
        backup_do(args)
    except BackupError as e:
        print('Error: %s' % e.__str__())
        exit(-1)
    except BaseException as e:
        traceback.print_exc()
        exit(-2)
