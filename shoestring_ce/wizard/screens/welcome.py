import shoestring.wizard.screens.welcome as original_welcome
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.utils import get_cwidth
from prompt_toolkit.widgets import Box, Shadow
from shoestring.wizard.Screen import Screen
from shoestring.wizard.screens.welcome import ButtonWithOperation, WelcomeSettings
from shoestring.wizard.ShoestringOperation import ShoestringOperation


def create(_screens):
    values = [
        (ShoestringOperation.SETUP, _('wizard-welcome-setup')),  # type: ignore
        (ShoestringOperation.IMPORT_BOOTSTRAP, _('wizard-welcome-import-bootstrap')),  # type: ignore
        (ShoestringOperation.UPGRADE, _('wizard-welcome-upgrade')),  # type: ignore
        (ShoestringOperation.RESET_DATA, _('wizard-welcome-reset-data')),  # type: ignore
        (ShoestringOperation.RENEW_CERTIFICATES, _('wizard-welcome-renew-certificates')),  # type: ignore
        (ShoestringOperation.RENEW_VOTING_KEYS, _('wizard-welcome-renew-voting-keys'))  # type: ignore
    ]
    # [CE]Calculate the maximum button width
    max_label = max(get_cwidth(label) for (_, label) in values)
    buttons = [
        ButtonWithOperation(operation, label, width=max_label + 4)
        for (operation, label) in values
    ]
    return Screen(
        'welcome',
        Box(
            Shadow(
                HSplit([
                    Window(
                        FormattedTextControl(_('wizard-welcome-title')),  # type: ignore
                        align=WindowAlign.CENTER
                    ),
                    Box(
                        HSplit([
                            Box(button, padding_top=1, padding_bottom=0) for button in buttons
                        ]),
                        style='class:navigation'
                    )
                ], style='class:dialog.body')
            )
        ),
        accessor=WelcomeSettings(buttons),
        hide_navbar=True
    )


def patch_welcome_screen():
    original_welcome.create = create
