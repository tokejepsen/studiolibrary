# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import studioqt

from studioqt import QtCore
from studioqt import QtWidgets


class StatusWidget(QtWidgets.QFrame):

    DEFAULT_DISPLAY_TIME = 10000  # Milliseconds, 10 secs

    INFO_CSS = """"""

    ERROR_CSS = """
        color: rgb(240, 240, 240);
        background-color: rgb(220, 40, 40);
        selection-color: rgb(220, 40, 40);
        selection-background-color: rgb(240, 240, 240);
    """

    WARNING_CSS = """
        color: rgb(240, 240, 240);
        background-color: rgb(240, 170, 0);
    """

    def __init__(self, parent):
        QtWidgets.QFrame.__init__(self, parent)

        self.setObjectName("statusWidget")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._moveIn = None
        self._fadeIn = None
        self._fadeOut = None
        self._blocking = False
        self._expanded = False
        self._timer = QtCore.QTimer(self)

        parent.installEventFilter(self)

        self._button = QtWidgets.QPushButton(self)
        self._button.setMaximumSize(QtCore.QSize(17, 17))
        self._button.setIconSize(QtCore.QSize(17, 17))

        self._label = QtWidgets.QLabel("", self)
        self._label.setCursor(QtCore.Qt.IBeamCursor)
        self._label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Preferred)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(1, 0, 0, 0)
        layout.addWidget(self._button)
        layout.addWidget(self._label)

        self.setLayout(layout)
        self.setFixedHeight(19)
        self.setMinimumWidth(5)

        QtCore.QObject.connect(
            self._timer,
            QtCore.SIGNAL("timeout()"),
            self.collapse,
        )

    def reset(self):
        """
        Called when the current animation has finished.

        :rtype: None 
        """
        self._moveIn = None
        self._fadeIn = None
        self._fadeOut = None
        self._expanded = False
        self._blocking = False

    def setDpi(self, dpi):
        """
        Set the dpi resolution for the widget.
        
        :type dpi: int 
        :rtype: None 
        """
        self.setFixedHeight(20 * dpi)

    def isBlocking(self):
        """
        Return true if the status widget is blocking, otherwise return false.

        :rtype: bool 
        """
        return self._blocking

    def isExpanded(self):
        """
        Return true if the status widget is expanded, otherwise return false.

        :rtype: bool 
        """
        return self._expanded

    def eventFilter(self, widget, event):
        """
        Update the geometry when the parent widget changes size.

        :type widget: QtWidget.QWidget
        :type event: QtCore.QEvent 
        :rtype: bool 
        """
        if event.type() == QtCore.QEvent.Resize:
            self.updateGeometry()
        return super(StatusWidget, self).eventFilter(widget, event)

    def updateGeometry(self):
        """
        Called when the parent geometry resize event is triggered.

        :rtype: None
        """
        if self.isExpanded():
            geometry = self.expandedGeometry()
        else:
            geometry = self.collapsedGeometry()

        self.setGeometry(geometry)

    def expandedGeometry(self):
        """
        Return the geometry when expanded.
        
        :rtype: QtCore.QRect 
        """
        dst = QtCore.QRect(self.geometry())
        dst.setX(0)
        dst.setY(self.parent().geometry().height() - dst.height())
        dst.setWidth(self.parent().geometry().width())

        return dst

    def collapsedGeometry(self):
        """
        Return the geometry when collapsed.

        :rtype: QtCore.QRect 
        """
        src = QtCore.QRect(self.geometry())
        src.setX(0)
        src.setY(self.parent().geometry().bottom())
        src.setWidth(self.parent().geometry().width())

        return src

    def showInfoMessage(self, message, msecs=None, blocking=False):
        """
        Set an info message to be displayed in the status widget.

        :type message: str
        :type msecs: int
        :type blocking: bool
        :rtype: None 
        """
        if self.isBlocking():
            return

        icon = studioqt.resource.icon("info")
        self.setStyleSheet(self.INFO_CSS)
        self.showMessage(message, icon, msecs=msecs, blocking=blocking)

    def showErrorMessage(self, message, msecs=None, blocking=True):
        """
        Set an error to be displayed in the status widget.
        
        :type message: str
        :type msecs: int
        :type blocking: bool
        :rtype: None 
        """
        icon = studioqt.resource.icon("error")
        self.setStyleSheet(self.ERROR_CSS)
        self.showMessage(message, icon, msecs=msecs, blocking=blocking)

    def showWarningMessage(self, message, msecs=None, blocking=False):
        """
        Set a warning to be displayed in the status widget.

        :type message: str
        :type msecs: int
        :type blocking: bool
        :rtype: None 
        """
        if self.isBlocking():
            return

        icon = studioqt.resource.icon("warning")
        self.setStyleSheet(self.WARNING_CSS)
        self.showMessage(message, icon, msecs=msecs, blocking=blocking)

    def showMessage(
            self,
            message,
            icon=None,
            msecs=None,
            blocking=False,
    ):
        """
        Set the given text to be displayed in the status widget.

        :type message: str
        :type icon: icon
        :type msecs: int
        :type blocking: bool
        :rtype: None 
        """
        self._blocking = blocking

        msecs = msecs or self.DEFAULT_DISPLAY_TIME
        message = unicode(message)

        if icon:
            self._button.setIcon(icon)
            self._button.show()
        else:
            self._button.hide()

        if message:
            self._label.setText(message)
            self.expand(msecs)
        else:
            self.collapse()

        self.update()

    def expand(self, msecs):
        """
        Expand the widget to its expanded geometry.
        
        :type msecs: int
        :rtype: None 
        """
        self._expanded = True

        self.fadeIn()
        self.moveIn()

        if msecs is not None:
            self._timer.stop()
            self._timer.start(msecs)

    def collapse(self):
        """
        Collapse the widget to its collapsed geometry.

        :rtype: None 
        """
        self._expanded = False

        self.fadeOut()

    def fadeOut(self):
        """
        Fade out the widget.

        :rtype: None 
        """
        self._timer.stop()
        self._fadeOut = studioqt.fadeOut(self, 500, onFinished=self.reset)

    def fadeIn(self):
        """
        Fade in the widget.
        
        :rtype: None 
        """
        if self._fadeOut:
            self._fadeOut.stop()
            self._fadeOut.setCurrentTime(0)

        if not self._fadeIn:
            self._fadeIn = studioqt.fadeIn(self, 200)

    def moveIn(self):
        """
        Move the widget to it's expanded geometry.

        :rtype: None 
        """
        if not self._moveIn:
            src = self.collapsedGeometry()
            dst = self.expandedGeometry()

            self._moveIn = QtCore.QPropertyAnimation(self, "geometry")
            self._moveIn.setDuration(200)
            self._moveIn.setStartValue(src)
            self._moveIn.setEndValue(dst)
            self._moveIn.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
            self._moveIn.start()
