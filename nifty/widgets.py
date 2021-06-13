import enum
import re

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from . import animations


class LayoutDirection(enum.Enum):

    horizontal = 0
    vertical = 1
    diagonal = 2


class _AnimatedMixin_(object):
    """"""

    shown = QtCore.Signal()

    def __init__(
        self,
        in_width: int,
        in_height: int,
        in_layout_direction: LayoutDirection = LayoutDirection.horizontal,
    ):

        object.__init__(self)

        self._width = in_width
        self._height = in_height
        self._layout_direction = in_layout_direction

        self.set_layout_direction(self._layout_direction)

    # Slots:
    @QtCore.Slot()
    def _on_shown_(self) -> None:

        self.shown.emit()

    # Public Methods:
    def set_layout_direction(self, in_layout_direction: LayoutDirection) -> None:
        """Set the growth direction of the widgets layout.

        Args:
            in_layout_direction (LayoutDirection): Enum with valid directions to
                animate the widget growth.

        Returns:
            None
        """

        self._layout_direction = in_layout_direction
        if in_layout_direction == LayoutDirection.horizontal:

            self._show_animation = animations.create_combined_property_animation(
                self, ("size",), (QtCore.QSize(0, self._height), QtCore.QSize(self._width, self._height))
            )

        elif in_layout_direction == LayoutDirection.vertical:

            self._show_animation = animations.create_combined_property_animation(
                self, ("size",), (QtCore.QSize(self._width, 0), QtCore.QSize(self._width, self._height))
            )

        self._show_animation.finished.connect(self._on_shown_)

    def set_height(self, in_height: int):

        resize_animation = animations.PropertyAnimation(
            self, "size", (QtCore.QSize(self._width, self.height()), QtCore.QSize(self._width, in_height))
        )
        return resize_animation.start()

    def reset_size(self) -> bool:

        if self._layout_direction == LayoutDirection.horizontal:

            return self.resize(1, self._height)

        elif self._layout_direction == LayoutDirection.vertical:

            return self.resize(self._width, 1)

    # Qt Methods:
    def show(self, animate: bool = True, delay_animation: int = 50) -> bool:

        self.reset_size()
        if animate:

            QtCore.QTimer.singleShot(delay_animation, self._show_animation.start)

        return super().show()

    # Magic Methods:
    def __getattr__(self, in_attribute_name: str):
        """This is a custom get attribute method for handling both Qt and
        python style snake case attribute access.

        It will convert setShowAnimationDirection to set_show_animation_direction
        or convert set_maximum_height to setMaximumHeight.
        The former being a nifty widgets method, the latter being a Qt method.

        The intention is to provide both Qt style syntax or the pythonic snake case.
        The emphasis is on the user to choose which style to use,
        and maintain it across their code base.

        Using both is not recommended, though you can obviously do as you choose!

        Args:
            in_attribute_name (str): The name of the attribute.

        Returns:
            object: The attribute object, if it exists.
            Raises an AttributeError if attribute not found.
        """

        if "_" in in_attribute_name:

            split = in_attribute_name.split("_")
            pascal_case_attribute_name = "".join((word.title() for word in split[1:]))
            pascal_case_attribute_name = f"{split[0]}{pascal_case_attribute_name}"

            return Widget.__getattribute__(self, pascal_case_attribute_name)

        split = re.sub(r"([A-Z])", r" \1", in_attribute_name).split()
        snake_case_attribute_name = "_".join(split).lower()

        return Widget.__getattribute__(self, snake_case_attribute_name)


class Widget(_AnimatedMixin_, QtWidgets.QWidget):
    def __init__(self, *args, in_layout=None, **kwargs):

        QtWidgets.QWidget.__init__(self)
        _AnimatedMixin_.__init__(self, *args, **kwargs)

        QtWidgets.QVBoxLayout(self) if in_layout is None else in_layout(self)

    def addWidget(self, *args, **kwargs):

        return self.layout().addWidget(*args, **kwargs)

    def show(self, animate: bool = True, delay_animation: int = 50, show_children: bool = False) -> bool:

        result = super().show(animate=animate, delay_animation=delay_animation)
        if show_children:
            for child in self.children():
                try:
                    child.show()
                except: pass

        return result

class MainWindow(_AnimatedMixin_, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):

        QtWidgets.QMainWindow.__init__(self)
        _AnimatedMixin_.__init__(self, *args, **kwargs)


class PushButton(_AnimatedMixin_, QtWidgets.QPushButton):

    mouse_enter = QtCore.Signal()
    mouse_press = QtCore.Signal()
    mouse_release = QtCore.Signal()
    mouse_leave = QtCore.Signal()

    def __init__(self, in_text, *args, in_icon: QtGui.QIcon = None, **kwargs):

        if in_icon:

            QtWidgets.QPushButton.__init__(self, in_icon, in_text)

        else:

            QtWidgets.QPushButton.__init__(self, in_text)

        _AnimatedMixin_.__init__(self, *args, **kwargs)

        # Mouse colors:
        self._mouse_enter_pulse_end_color = QtGui.QColor("#00B0FF")
        self._mouse_enter_pulse_end_color.setAlpha(75)
        self._mouse_enter_pulse_start_color = self._mouse_enter_pulse_end_color.lighter()
        self._mouse_enter_pulse_start_color.setAlpha(50)
        self._mouse_enter_pulse_color = self._mouse_enter_pulse_start_color

        self._mouse_leave_pulse_start_color = self._mouse_enter_pulse_end_color
        self._mouse_leave_pulse_end_color = self._mouse_enter_pulse_start_color
        # self._mouse_leave_pulse_end_color.setAlpha(50)
        self._mouse_leave_pulse_color = self._mouse_leave_pulse_start_color

        self._mouse_press_pulse_start_color = QtGui.QColor("#00B0FF")
        self._mouse_press_pulse_start_color.setAlpha(75)
        self._mouse_press_pulse_end_color = self._mouse_press_pulse_start_color.lighter()
        self._mouse_press_pulse_end_color.setAlpha(250)
        self._mouse_press_pulse_color = self._mouse_press_pulse_start_color

        self._mouse_release_pulse_end_color = QtGui.QColor("#00B0FF")
        self._mouse_release_pulse_end_color.setAlpha(75)
        self._mouse_release_pulse_start_color = self._mouse_release_pulse_end_color.lighter()
        self._mouse_release_pulse_start_color.setAlpha(250)
        self._mouse_release_pulse_color = self._mouse_release_pulse_end_color

        self._mouse_enter_pulse_brush = QtGui.QBrush(self._mouse_enter_pulse_color)

        self._border_show_time = 0
        self._mouse_enter_pulse_radius = 0
        self._mouse_press_pulse_radius = 0
        self._mouse_release_pulse_radius = 0
        self._mouse_leave_pulse_radius = 0

        self._mouse_enter_location = QtCore.QPoint(0, 0)
        self._mouse_press_location = self._mouse_enter_location
        self._mouse_release_location = self._mouse_enter_location
        self._mouse_leave_location = self._mouse_enter_location

        self._mouse_currently_pressed = False
        self._rendered = False

        self._setup_animation()

    # Qt Properties:
    @QtCore.Property(float)
    def border_show_time(self):

        return self._border_show_time

    @border_show_time.setter
    def border_show_time(self, value):

        self._border_show_time = value
        self.update()

    @QtCore.Property(float)
    def mouse_enter_pulse_radius(self):

        return self._mouse_enter_pulse_radius

    @mouse_enter_pulse_radius.setter
    def mouse_enter_pulse_radius(self, value):

        self._mouse_enter_pulse_radius = value
        self.update()

    @QtCore.Property(QtGui.QColor)
    def mouse_enter_pulse_color(self):

        return self._mouse_enter_pulse_color

    @mouse_enter_pulse_color.setter
    def mouse_enter_pulse_color(self, value):

        self._mouse_enter_pulse_color = value
        self.update()

    @QtCore.Property(float)
    def mouse_press_pulse_radius(self):

        return self._mouse_press_pulse_radius

    @mouse_press_pulse_radius.setter
    def mouse_press_pulse_radius(self, value):

        self._mouse_press_pulse_radius = value
        self.update()

    @QtCore.Property(QtGui.QColor)
    def mouse_press_pulse_color(self):

        return self._mouse_press_pulse_color

    @mouse_press_pulse_color.setter
    def mouse_press_pulse_color(self, value):

        self._mouse_press_pulse_color = value
        self.update()

    @QtCore.Property(float)
    def mouse_release_pulse_radius(self):

        return self._mouse_release_pulse_radius

    @mouse_release_pulse_radius.setter
    def mouse_release_pulse_radius(self, value):

        self._mouse_release_pulse_radius = value
        self.update()

    @QtCore.Property(QtGui.QColor)
    def mouse_release_pulse_color(self):

        return self._mouse_release_pulse_color

    @mouse_release_pulse_color.setter
    def mouse_release_pulse_color(self, value):

        self._mouse_release_pulse_color = value
        self.update()

    @QtCore.Property(float)
    def mouse_leave_pulse_radius(self):

        return self._mouse_leave_pulse_radius

    @mouse_leave_pulse_radius.setter
    def mouse_leave_pulse_radius(self, value):

        self._mouse_leave_pulse_radius = value
        self.update()

    @QtCore.Property(QtGui.QColor)
    def mouse_leave_pulse_color(self):

        return self._mouse_leave_pulse_color

    @mouse_leave_pulse_color.setter
    def mouse_leave_pulse_color(self, value):

        self._mouse_leave_pulse_color = value
        self.update()

    # Private Methods:
    def _setup_animation(self):

        animation_duration = 250

        def _create_pulse_animation_(in_name, in_radius_range, in_color_range, in_signal, in_duration):

            radius_animation = animations.PropertyAnimation(
                self, f"{in_name}_pulse_radius", in_radius_range, in_duration=in_duration
            )

            color_animation = animations.PropertyAnimation(
                self, f"{in_name}_pulse_color", in_color_range, in_duration=in_duration
            )

            animation_group = QtCore.QParallelAnimationGroup()
            animation_group.addAnimation(radius_animation)
            animation_group.addAnimation(color_animation)

            # in_signal.connect(animation_group.start)

            return radius_animation, color_animation, animation_group

        (
            self._mouse_enter_pulse_radius_animation,
            self._mouse_enter_pulse_color_animation,
            self._mouse_enter_pulse_animation_group,
        ) = _create_pulse_animation_(
            "mouse_enter",
            (0, 1),
            (self._mouse_enter_pulse_start_color, self._mouse_enter_pulse_end_color),
            self.mouse_enter,
            animation_duration
        )
        (
            self._mouse_press_pulse_radius_animation,
            self._mouse_press_pulse_color_animation,
            self._mouse_press_pulse_animation_group,
        ) = _create_pulse_animation_(
            "mouse_press",
            (0, 1),
            (self._mouse_press_pulse_start_color, self._mouse_press_pulse_end_color),
            self.mouse_press,
            animation_duration * 0.75
        )
        (
            self._mouse_release_pulse_radius_animation,
            self._mouse_release_pulse_color_animation,
            self._mouse_release_pulse_animation_group,
        ) = _create_pulse_animation_(
            "mouse_release",
            (1, 0),
            (self._mouse_release_pulse_start_color, self._mouse_release_pulse_end_color),
            self.mouse_release,
            animation_duration * 0.75
        )
        self._boarder_show_animation = animations.PropertyAnimation(
            self, "border_show_time", (0.0, 1.0), in_duration=200
        )
        self.shown.connect(self._on_shown2_)
        # (
        #     self._mouse_leave_pulse_radius_animation,
        #     self._mouse_leave_pulse_color_animation,
        #     self._mouse_leave_pulse_animation_group,
        # ) = _create_pulse_animation_(
        #     "mouse_leave",
        #     (1, 0),
        #     (self._mouse_leave_pulse_start_color, self._mouse_leave_pulse_end_color),
        #     self.mouse_leave,
        # )
        # _create_pulse_animation_("_mouse_press", b"mouse_press_pulse_radius", b"mouse_press_pulse_color")

    def _play_mouse_enter_animation_(self):

        self._mouse_enter_pulse_animation_group.stop()
        diameter = max(self.contentsRect().height(), self.contentsRect().width()) * 1.5
        self._mouse_enter_pulse_radius_animation.setStartValue(0)
        self._mouse_enter_pulse_radius_animation.setEndValue(diameter)
        self._mouse_enter_pulse_color_animation.setStartValue(self._mouse_enter_pulse_start_color)
        self._mouse_enter_pulse_color_animation.setEndValue(self._mouse_enter_pulse_end_color)
        self._mouse_enter_pulse_animation_group.start()

    def _play_mouse_leave_animation_(self):

        self._mouse_enter_pulse_animation_group.stop()
        self._mouse_enter_location = self._mouse_leave_location
        diameter = max(self.contentsRect().height(), self.contentsRect().width()) * 1.5
        self._mouse_enter_pulse_radius_animation.setStartValue(diameter)
        self._mouse_enter_pulse_radius_animation.setEndValue(0)
        self._mouse_enter_pulse_color_animation.setStartValue(self._mouse_enter_pulse_end_color)
        self._mouse_enter_pulse_color_animation.setEndValue(self._mouse_enter_pulse_start_color)
        self._mouse_enter_pulse_animation_group.start()

    def _play_mouse_press_animation_(self):

        self._mouse_press_pulse_animation_group.stop()
        diameter = max(self.contentsRect().height(), self.contentsRect().width()) * 1.5
        self._mouse_press_pulse_radius_animation.setEndValue(diameter)
        self._mouse_press_pulse_animation_group.start()

    def _play_mouse_release_animation_(self):

        self._mouse_release_pulse_animation_group.stop()
        diameter = max(self.contentsRect().height(), self.contentsRect().width()) * 1.5
        self._mouse_release_pulse_radius_animation.setStartValue(diameter)
        self._mouse_release_pulse_animation_group.start()

    @QtCore.Slot()
    def _on_shown2_(self):

        self._boarder_show_animation.start()

    # Qt Methods:
    def enterEvent(self, event):

        self._mouse_enter_location = event.pos()
        self._play_mouse_enter_animation_()
        self.mouse_enter.emit()

        return super().enterEvent(event)

    def leaveEvent(self, event):

        self._mouse_leave_location = self.mapFromGlobal(QtGui.QCursor.pos())
        self.mouse_leave.emit()
        if self._mouse_enter_pulse_radius_animation.state() == animations.PropertyAnimation.Running:

            @QtCore.Slot()
            def _finished_():

                QtCore.QTimer.singleShot(0, self._play_mouse_leave_animation_)
                self._mouse_enter_pulse_radius_animation.finished.disconnect(_finished_)

            self._mouse_enter_pulse_radius_animation.finished.connect(_finished_)

        else:

            self._play_mouse_leave_animation_()

        return super().leaveEvent(event)

    def mousePressEvent(self, event):

        self._mouse_press_location = event.pos()
        self.mouse_press.emit()
        self._mouse_currently_pressed = True
        self._play_mouse_press_animation_()

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        self._mouse_release_location = event.pos()
        self.mouse_release.emit()
        self._mouse_currently_pressed = False

        if self._mouse_press_pulse_radius_animation.state() == animations.PropertyAnimation.Running:

            @QtCore.Slot()
            def _finished_():

                QtCore.QTimer.singleShot(0, self._play_mouse_release_animation_)
                self._mouse_press_pulse_radius_animation.finished.disconnect(_finished_)

            self._mouse_press_pulse_radius_animation.finished.connect(_finished_)

        else:

            self._play_mouse_release_animation_()

        return super().mousePressEvent(event)

    def paintEvent(self, event):

        contents_rect = self.contentsRect()
        if not self._rendered:
            QtCore.QTimer.singleShot(200, self._on_shown2_)
            self._rendered = True

        # super().paintEvent(event)

        running = animations.PropertyAnimation.Running
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(QtCore.Qt.transparent)
        painter.setBrush(self._mouse_enter_pulse_brush)
        self._mouse_enter_pulse_brush.setColor(self.mouse_enter_pulse_color)
        painter.drawEllipse(
            self._mouse_enter_location, self.mouse_enter_pulse_radius, self.mouse_enter_pulse_radius
        )

        if self._mouse_press_pulse_animation_group.state() == running or self._mouse_currently_pressed:

            brush = QtGui.QBrush(self.mouse_press_pulse_color)
            painter.setBrush(brush)
            painter.drawEllipse(
                self._mouse_press_location, self.mouse_press_pulse_radius, self.mouse_press_pulse_radius
            )

        if self._mouse_release_pulse_animation_group.state() == running:

            brush = QtGui.QBrush(self.mouse_release_pulse_color)
            painter.setBrush(brush)
            painter.drawEllipse(
                self._mouse_release_location, self.mouse_release_pulse_radius, self.mouse_release_pulse_radius
            )

        # if self._mouse_leave_pulse_animation_group.state() == running:

        #     brush = QtGui.QBrush(self.mouse_leave_pulse_color)
        #     painter.setBrush(brush)
        #     painter.drawEllipse(
        #         self._mouse_leave_location, self.mouse_leave_pulse_radius, self.mouse_leave_pulse_radius
        #     )

        if self.border_show_time > 0.0:
            painter.setBrush(QtCore.Qt.transparent)
            painter.setPen("black")
            border_left = animations.lerp(contents_rect.center().x(), contents_rect.left(), self.border_show_time)
            border_width = animations.lerp(0.0, contents_rect.width(), self.border_show_time)
            border_rect = QtCore.QRectF(border_left, 0, border_width, contents_rect.height())
            painter.drawRect(border_rect)
        painter.end()
