from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

# print(QtCore.Qt.red)


class AnimatedToggle(QtWidgets.QCheckBox):

    _transparent_pen = QtGui.QPen(QtCore.Qt.transparent)
    _light_grey_pen = QtGui.QPen(QtCore.Qt.lightGray)

    def __init__(
        self,
        parent=None,
        bar_color=QtCore.Qt.gray,
        checked_color="#00B0FF",
        handle_color=QtCore.Qt.white,
        pulse_unchecked_color="#44999999",
        pulse_checked_color="#4400B0EE",
    ):
        super().__init__(parent)

        # Save our properties on the object via self, so we can access them later
        # in the paintEvent.
        self._checked_color = QtGui.QColor(checked_color)
        self._checked_bar_color = self._checked_color.lighter()
        self._pulse_colour = QtGui.QColor(self._checked_bar_color)
        self._pulse_colour.setAlpha(75)

        self._bar_brush = QtGui.QBrush(bar_color)
        self._bar_checked_brush = QtGui.QBrush(self._checked_bar_color)

        self._handle_brush = QtGui.QBrush(handle_color)
        self._handle_checked_brush = QtGui.QBrush(self._checked_color)

        self._pulse_unchecked_brush = QtGui.QBrush(QtGui.QColor(pulse_unchecked_color))
        self._pulse_checked_brush = QtGui.QBrush(self._pulse_colour)

        # Setup the rest of the widget.

        self.setContentsMargins(0, 0, 8, 0)
        self._handle_position = 0
        self._handle_color = QtGui.QColor(handle_color)

        self._pulse_radius = 0

        animation_duration = 250

        self._handle_position_animation = QtCore.QPropertyAnimation(self, b"handle_position", self)
        self._handle_position_animation.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self._handle_position_animation.setDuration(animation_duration)

        self._handle_colour_animation = QtCore.QPropertyAnimation(self, b"handle_color", self)
        self._handle_colour_animation.setEasingCurve(QtCore.QEasingCurve.InCubic)
        self._handle_colour_animation.setDuration(animation_duration)

        self._pulse_animation = QtCore.QPropertyAnimation(self, b"pulse_radius", self)
        self._pulse_animation.setDuration(animation_duration * 1.2)  # time in ms
        self._pulse_animation.setStartValue(10)
        self._pulse_animation.setEndValue(20)

        self._animation_group = QtCore.QParallelAnimationGroup()
        self._animation_group.addAnimation(self._handle_position_animation)
        self._animation_group.addAnimation(self._pulse_animation)
        self._animation_group.addAnimation(self._handle_colour_animation)

        self.stateChanged.connect(self._on_StateChanged)

    # def sizeHint(self):
    #     return QtCore.QSize(120, 45)

    def hitButton(self, pos: QtCore.QPoint):
        return self.contentsRect().contains(pos)

    @QtCore.Slot(int)
    def _on_StateChanged(self, value):

        self._animation_group.stop()
        if value:

            self._handle_colour_animation.setStartValue(QtGui.QColor(QtCore.Qt.white))
            self._handle_colour_animation.setEndValue(self._checked_color)
            self._handle_position_animation.setEndValue(1)

        else:

            self._handle_colour_animation.setStartValue(self._checked_color)
            self._handle_colour_animation.setEndValue(QtGui.QColor(QtCore.Qt.white))
            self._handle_position_animation.setEndValue(0)

        self._animation_group.start()

    def paintEvent(self, e: QtGui.QPaintEvent):

        contents_rect = self.contentsRect()
        handle_radius = round(0.24 * contents_rect.height())

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(self._transparent_pen)
        bar_height = 0.35 * contents_rect.height()
        bar_rect = QtCore.QRectF(0, 0, contents_rect.width() - handle_radius, bar_height)
        bar_rect.moveCenter(contents_rect.center())
        rounding = bar_rect.height() / 2

        # the handle will move along this line
        trailLength = contents_rect.width() - 2 * handle_radius

        x_position = contents_rect.x() + handle_radius + trailLength * self._handle_position

        if self._pulse_animation.state() == QtCore.QPropertyAnimation.Running:
            brush = self._pulse_checked_brush if self.isChecked() else self._pulse_unchecked_brush
            painter.setBrush(brush)
            painter.drawEllipse(
                QtCore.QPointF(x_position, bar_rect.center().y()),
                self._pulse_radius,
                self._pulse_radius,
            )

        # Bar drawing:
        painter.setBrush(self._bar_brush)
        painter.drawRoundedRect(bar_rect, rounding, rounding)
        painter.setPen(self._light_grey_pen)

        bar_overlay = QtCore.QRectF(0, 0, x_position, bar_height)
        # bar_overlay.moveCenter(contents_rect.center())
        bar_overlay.moveBottomLeft(bar_rect.bottomLeft())
        painter.setBrush(self._bar_checked_brush)
        painter.drawRoundedRect(bar_overlay, rounding, rounding)

        self._handle_brush.setColor(self._handle_color)
        painter.setBrush(self._handle_brush)

        # Handle drawing:
        painter.drawEllipse(QtCore.QPointF(x_position, bar_rect.center().y()), handle_radius, handle_radius)
        # handle_rect = QtCore.QRectF(x_position - 7.0, bar_rect.center().y() * 0.5, handle_radius * 1.5, contents_rect.height() * 0.5)
        # painter.drawRoundedRect(handle_rect, 0.1, 0.1)

        painter.end()

    @QtCore.Property(QtGui.QColor)
    def handle_color(self):

        return self._handle_color

    @handle_color.setter
    def handle_color(self, color):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QtCore.QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_color = color
        self.update()

    @QtCore.Property(float)
    def handle_position(self):

        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QtCore.QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    @QtCore.Property(float)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()
