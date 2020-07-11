# backupcpy

`backupcpy` is a tiny and elegant backup archive assembler implemented in less than 300 lines of Python code. It is
designed to assemble lists of files and create archives. That is all it does.

- Simple YAML based configuration.
- Support for collections of files producing separate archives.
- Point-in-time tarballs (.tar.gz, tar.xz, tar.bz2).
- Support for uncompressed archives (plain tarballs).
- Ability to ignore files using Unix shell-style wildcards.

## Requirements

You should have Python3 and pip3 installed on your system. Python 2 is not supported and will not work.

## Installation

You can install `backupcpy` using pip - `sudo pip3 install backupcpy`

## Backup manifest

Backup manifest is a file that contains lists directory and file paths you want to archive - collections.
Each collection can have any number of files and directories attached to it and each collection produces a
 single backup archive.

By default, backupcpy will look for a file called `.backupcpy.yml` in your home directory. You can tell it to
use a different file using `--manifest` command line option.

Manifest entries will also have some basic placeholders available for you to use.

### Example manifest

```yaml
# Example configuration file for backupcpy
#
# Available placeholders:
# {{now}} - current datetime in format %Y%m%d-%H%M%S-%f
# {{cwd}} - current working directory
# {{home}} - home directory of the current user
# {{user}} - username of the current user

# Global ignore - matches in ALL collections
# The format is Unix shell-style wildcards.
# Ignore is matched against absolute resolved path of each file.
# This works slightly differently than .gitignore.
ignore:
  - '*node_modules*' # Anywhere in the path

# Collections of things to backup
collections:
  personal:
    # What compression to use 'none', 'gz', 'xz', 'bz2'
    compress: 'gz'
    # Where to store backup archives (absolute path)
    target: '/mnt/backup-drive'
    # Ignore for current collection
    ignore:
      - '*.git*'
      - '*.idea*'
    # Items to backup - files, directories.
    # Defined using glob format.
    # Tilde is ignored - use {{home}} instead.
    items:
      - '{{home}}/Documents/**'
      - '{{home}}/Images/**'
      - '{{home}}/My Projects/**'
```

## Usage

`backupcpy [-h] [--manifest MANIFEST] [--verbose] [--debug] [--quiet] collection [collection ...]`

To create backup archives you need to invoke the `backupcpy` command line tool and provide it with list of names of the
collections you want to create archives for.

You can optionally change status output modes and provide a different location for the backup manifest.

For example:

`backupcpy personal projects other`

## Why?

I needed a simple tool to assemble point-in-time backups. I use `backupcpy` to assemble backup archives which are
then automatically rsync'd to hot and cold networked storage.

If you are looking for a fully fledged backup system, you might want to look at [Borg](https://borgbackup.readthedocs.io),
[Bacula](https://www.bacula.org) or [git-annex](https://git-annex.branchable.com).

## License

Licensed under terms and conditions of Apache 2.0 license.
