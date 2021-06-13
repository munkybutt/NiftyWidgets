import os
import site
import sys

from Qt import QtCore
from Qt import QtWidgets


def __setup__():

    nifty_package_path = os.path.normpath(
        os.path.join(__file__, os.path.pardir, os.path.pardir)
    )
    site.addsitedir(nifty_package_path)


if __name__ == "__main__":

    __setup__()

    import nifty.widgets as nifty
    import nifty.utilities as nifty_utils
    import nifty.animations as nifty_anim

    app = QtWidgets.QApplication(sys.argv)
    # widget = nifty_utils.time_execution(
    #     nifty.Widget, 40, 500, in_loop_count=1, in_layout_direction=nifty.LayoutDirection.vertical
    #     # nifty.MainWindow, 400, 500, in_loop_count=1, in_layout_direction=nifty.LayoutDirection.vertical
    # )

    # print(nifty_anim.lerp(2.0, 10.0, 0.5))
    widget = nifty.Widget(500, 200, in_layout_direction=nifty.LayoutDirection.vertical)
    for num in range(4):

        sub_widget = nifty.Widget(500, 500, in_layout=QtWidgets.QHBoxLayout)
        for sub_num in range(4):
            button = nifty.PushButton("BUTTON", 100, 100, in_layout_direction=nifty.LayoutDirection.vertical)
            button.setMinimumHeight(30)
            sub_widget.addWidget(button)
        widget.addWidget(sub_widget)

    widget.show(animate=True)
    app.exec_()
