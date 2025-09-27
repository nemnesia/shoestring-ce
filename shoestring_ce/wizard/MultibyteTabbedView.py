from functools import partial

from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, VSplit, Window
from prompt_toolkit.utils import get_cwidth
from shoestring.wizard.TabbedView import Border, _create_condition


class MultibyteTabs(HSplit):
    def __init__(self, controller, items, validators):
        """
        Creates tabs around controller and items. Controller needs to be
        RadioList or something that exposes `.values` (list of tuples) and `.current_value`.
        """

        self.controller = controller
        self.items = items
        self.validators = validators

        fill = partial(Window, style='class:frame.border')

        # this builds either top of tab frame or fills with proper amount of whitespace
        # the tabs look like this (spaces are marked with '_' and :)
        #                 +-------+
        # :___xxx_:___yyy_|_*_zzz |___aaa_:___bbb_:
        #
        def frame(width, is_selected):
            return [
                ConditionalContainer(fill(width=1, height=1, char=Border.TOP_LEFT), filter=is_selected),
                ConditionalContainer(fill(width=width, char=Border.HORIZONTAL), filter=is_selected),
                ConditionalContainer(fill(width=1, height=1, char=Border.TOP_RIGHT), filter=is_selected),
                ConditionalContainer(fill(width=width + 1, height=1, char=' '), filter=~is_selected)
            ]

        frame_or_space = []
        for index, item in enumerate(controller.values):
            # [CE]Calculate the width considering the width of multibyte characters
            frame_or_space.extend(frame(get_cwidth(item[1]) + 4, _create_condition(controller, index)))

        tab_pages = []
        for index, item in enumerate(items):
            tab_pages.append(
                ConditionalContainer(
                    VSplit([
                        fill(width=1, char=Border.VERTICAL),
                        item,
                        fill(width=1, char=Border.VERTICAL)
                    ], padding=1),
                    filter=_create_condition(controller, index),
                ),
            )

        bottom_frame = VSplit([
            fill(width=1, height=1, char=Border.BOTTOM_LEFT),
            fill(char=Border.HORIZONTAL),
            fill(width=1, height=1, char=Border.BOTTOM_RIGHT)
        ])

        tab_view = [
            VSplit(frame_or_space),
            controller
        ] + tab_pages + [bottom_frame]

        super().__init__(tab_view)

    @property
    def is_valid(self):
        return self.validators[self.controller.current_value]()
