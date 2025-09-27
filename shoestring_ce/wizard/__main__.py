import asyncio
import gettext
import os
from pathlib import Path

import prompt_toolkit.widgets
import shoestring.wizard.__main__
import shoestring.wizard.TabbedView

from ..internal.CertificateV3Factory import patch_certificate_factory
from .MultibyteButton import MultibyteButton
from .MultibyteTabbedView import MultibyteTabs
from .screens.end_screen import patch_end_screen
from .screens.welcome import patch_welcome_screen

_original_wizard_main = None


async def wizard_main_wrapper():
    global _original_wizard_main
    # Skip language settings and execute only the remaining logic of wizard main
    original_gettext_translation = gettext.translation

    def dummy_translation(*args, **kwargs):
        class DummyTranslation:
            def install(self): pass
            def gettext(self, message): return message
        return DummyTranslation()
    gettext.translation = dummy_translation
    result = await _original_wizard_main()
    gettext.translation = original_gettext_translation
    return result


def setup_multibyte_button_patches():
    """Apply patch to support multibyte characters in buttons"""
    prompt_toolkit.widgets.Button = MultibyteButton
    patch_welcome_screen()


def setup_multibyte_tabed_view_patches():
    """Apply patch to support multibyte characters in tabs"""
    shoestring.wizard.TabbedView.Tabs = MultibyteTabs


def entry_point():
    global _original_wizard_main

    # Prioritize the language files of shoestring-ce
    ce_lang_directory = Path(__file__).resolve().parent.parent / 'lang'
    if ce_lang_directory.exists():
        lang = gettext.translation(
            'messages',
            localedir=ce_lang_directory,
            languages=(os.environ.get('LC_MESSAGES', 'en'), 'en'), fallback=True
        )
        lang.install()

    # Multibyte support
    setup_multibyte_button_patches()
    setup_multibyte_tabed_view_patches()
    patch_end_screen()

    # Node certificate x509 v3 support
    patch_certificate_factory()

    # Save the original wizard main
    _original_wizard_main = shoestring.wizard.__main__.main

    # Replace and execute wizard main
    shoestring.wizard.__main__.main = wizard_main_wrapper
    asyncio.run(shoestring.wizard.__main__.main())


if __name__ == '__main__':
    entry_point()
