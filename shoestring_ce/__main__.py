import argparse
import asyncio
import gettext
import os
import sys
from pathlib import Path

import argcomplete
import shoestring.__main__
from shoestring.__main__ import register_subcommand

from .internal.CertificateV3Factory import patch_certificate_factory


def parse_args(args):
    parser = argparse.ArgumentParser(description=_('main-title'))  # type: ignore
    subparsers = parser.add_subparsers(title='subcommands', help=_('main-subcommands-help'))  # type: ignore

    register_subcommand(subparsers, 'announce-transaction', _('main-announce-transaction-help'))  # type: ignore
    register_subcommand(subparsers, 'health', _('main-health-help'))  # type: ignore
    register_subcommand(subparsers, 'import-bootstrap', _('main-import-bootstrap-help'))  # type: ignore
    register_subcommand(subparsers, 'import-harvesters', _('main-import-harvesters-help'))  # type: ignore
    register_subcommand(subparsers, 'init', _('main-init-help'))  # type: ignore
    register_subcommand(subparsers, 'min-cosignatures-count', _('main-min-cosignatures-count-help'))  # type: ignore
    register_subcommand(subparsers, 'pemtool', _('main-pemtool-help'))  # type: ignore
    register_subcommand(subparsers, 'renew-certificates', _('main-renew-certificates-help'))  # type: ignore
    register_subcommand(subparsers, 'renew-voting-keys', _('main-renew-voting-keys-help'))  # type: ignore
    register_subcommand(subparsers, 'reset-data', _('main-reset-data-help'))  # type: ignore
    register_subcommand(subparsers, 'setup', _('main-setup-help'))  # type: ignore
    register_subcommand(subparsers, 'signer', _('main-signer-help'))  # type: ignore
    register_subcommand(subparsers, 'upgrade', _('main-upgrade-help'))  # type: ignore

    argcomplete.autocomplete(parser)
    args = parser.parse_args(args)
    if not hasattr(args, 'func'):
        parser.print_help()
        raise SystemExit()

    return args


async def shoestring_main_wrapper(args):
    # Skip language setup and execute only from parse_args onward
    args = parse_args(args)
    possible_task = args.func(args)
    if possible_task:
        await possible_task


def entry_point():
    # Prioritize shoestring-ce language files
    ce_lang_directory = Path(__file__).resolve().parent / 'lang'
    if ce_lang_directory.exists():
        lang = gettext.translation(
            'messages',
            localedir=ce_lang_directory, languages=(os.environ.get('LC_MESSAGES', 'en'), 'en'), fallback=True
        )
        lang.install()

    # Node certificate x509 v3 support
    patch_certificate_factory()

    # Replace and execute wizard main
    shoestring.__main__.main = shoestring_main_wrapper
    asyncio.run(shoestring.__main__.main(sys.argv[1:]))


if __name__ == '__main__':
    entry_point()
