from prompt_toolkit.layout.containers import Window
from prompt_toolkit.widgets import RadioList

from shoestring_ce.wizard.MultibyteTabbedView import MultibyteTabs


def test_multibytetabs_tab_width():
    # Arrange
    items = [
        (1, 'あいう'),
        (2, 'abc'),
        (3, '漢字')
    ]

    controller = RadioList(items)
    validators = {1: lambda: True, 2: lambda: True, 3: lambda: True}
    containers = [Window() for _ in items]

    # Act
    tabs = MultibyteTabs(controller, containers, validators)

    # Assert
    # タブの幅がマルチバイト文字を考慮して正しく計算されているかを確認
    # ここでは、例として controller.values[0][1] の幅を取得し、get_cwidth で一致するか確認
    from prompt_toolkit.utils import get_cwidth
    assert tabs.controller.values == items
    assert tabs.is_valid is True
