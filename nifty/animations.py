from Qt import QtCore


class PropertyAnimation(QtCore.QPropertyAnimation):
	"""
	"""
	started = QtCore.Signal()

	def __init__(self, in_widget, in_property_name, in_range, in_duration=150, in_parent=None):

		super().__init__(in_widget, bytes(in_property_name, encoding="utf-8"), in_parent if in_parent else in_widget)

		_start_value, _end_value = in_range
		self.setStartValue(_start_value)
		self.setEndValue(_end_value)
		self.setDuration(in_duration)
		self.setEasingCurve(QtCore.QEasingCurve.InQuad)

	def start(self):

		self.started.emit()
		return super().start()


class ParallelAnimationGroup(QtCore.QParallelAnimationGroup):
	"""
	"""

	started = QtCore.Signal()

	def __init__(self, in_animations):

		super().__init__()
		for animation in in_animations:
			self.addAnimation(animation)

	def start(self):

		self.started.emit()
		return super().start()


class SequentialAnimationGroup(QtCore.QSequentialAnimationGroup):
	"""
	"""

	started = QtCore.Signal()

	def __init__(self, in_animations):

		super().__init__()

	def start(self):

		self.started.emit()
		return self._super.start()


class PropertyAnimationGroup(ParallelAnimationGroup):
	"""
	"""

	def __init__(self, in_property_names):

		super().__init__()

	def start(self):

		self.started.emit()
		return self._super.start()


def create_combined_property_animation(in_widget, in_property_names, in_range, in_duration=150):

	animations = (
		PropertyAnimation(
			in_widget, property_name, in_range, in_duration=in_duration
		) for property_name in in_property_names
	)

	return ParallelAnimationGroup(animations)


def lerp(in_start, in_end, in_value):

	return ((in_end - in_start) * in_value) + in_start
