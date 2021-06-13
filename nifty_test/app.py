import os
import site

from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from Qt import QtCore
from animated_toggle import AnimatedToggle


def __setup__():

    nifty_package_path = os.path.normpath(
        os.path.join(__file__, os.path.pardir, os.path.pardir)
    )
    site.addsitedir(nifty_package_path)


__setup__()
app = QApplication([])

window = QWidget()

mainToggle = AnimatedToggle()
secondaryToggle = AnimatedToggle(
    checked_color="#FFB000", pulse_checked_color="#44FFB000"
)
tripToggle = AnimatedToggle(
    checked_color="green", pulse_checked_color="green"
)
mainToggle.resize(QtCore.QSize(120, 60))
mainToggle.setFixedHeight(50)
secondaryToggle.resize(QtCore.QSize(120, 60))
secondaryToggle.setFixedHeight(50)
tripToggle.resize(QtCore.QSize(120, 60))
tripToggle.setFixedHeight(50)

window.setLayout(QVBoxLayout())
# window.layout().addWidget(QLabel("Main Toggle"))
window.layout().addWidget(mainToggle)

# window.layout().addWidget(QLabel("Secondary Toggle"))
window.layout().addWidget(secondaryToggle)
window.layout().addWidget(tripToggle)

mainToggle.stateChanged.connect(secondaryToggle.setChecked)
mainToggle.stateChanged.connect(tripToggle.setChecked)

window.show()
app.exec_()
