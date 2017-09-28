"""The Maya file item supports .ma and .mb file types."""

import os
import logging

try:
    import maya.cmds
except ImportError, e:
    logging.exception(e)

import studiolibrary
import studiolibrarymaya

import studioqt
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


class MayaFileItem(studiolibrary.LibraryItem):

    """An item to display jpg/png in the Studio Library."""

    @classmethod
    def isValidPath(cls, path):

        extensions = [".ma", ".mb"]

        if not os.path.isfile(path):
            return False

        for ext in extensions:
            if path.endswith(ext):
                return True

    def load(self):
        """ Trigged when the user double clicks or clicks the load button."""
        print "Loaded", self.path()

        maya.cmds.file(
            self.path(),
            i=True,
            ignoreVersion=True,
            renamingPrefix="",
            mergeNamespacesOnClash=False,
            options="v=0;"
        )

    def doubleClicked(self):
        """Overriding this method to load any data on double click."""
        self.load()

    def isMayaAscii(self):
        path = self.path()
        return os.path.isfile(path) and path.endswith(".ma")

    def isMayaBinary(self):
        path = self.path()
        return os.path.isfile(path) and path.endswith(".mb")

    def swatchesPath(self):
        name = self.name()
        return os.path.join(self.dirname(), ".mayaSwatches", name + ".swatch")

    def previewPath(self):
        name = self.name()
        return os.path.join(self.dirname(), ".mayaSwatches", name + ".preview")

    # Need to support the swatches and preview when renaming this item
    # def rename(self, dst):
    #     studiolibrary.LibraryItem.rename(self, dst)

    def thumbnailPath(self):
        """
        Return the thumbnail path to be displayed for the item.

        :rtype: str
        """
        path = self.swatchesPath()

        if not os.path.isfile(path):
            path = self.previewPath()

        if not os.path.isfile(path):

            if self.isMayaAscii():
                path = studiolibrarymaya.resource().get("icons", "maFileIcon.png")

            if self.isMayaBinary():
                path = studiolibrarymaya.resource().get("icons", "mbFileIcon.png")

        return path

    def imageSequencePath(self):
        """
        Return the image sequence location for playing the animation preview.

        :rtype: str
        """
        name = self.name()
        return self.dirname() + "/.mayaSwatches/" + name

    def previewWidget(self, libraryWidget):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: CreateWidget
        """
        return ImagePreviewWidget(self)


class ImagePreviewWidget(QtWidgets.QWidget):

    """The widget to be shown when the user clicks on an image item."""

    def __init__(self, item, *args):
        """
        :type item: ImageItem
        :type args: list
        """
        QtWidgets.QWidget.__init__(self, *args)

        self._item = item
        self._pixmap = QtGui.QPixmap(item.thumbnailPath())

        self._image = QtWidgets.QLabel(self)
        self._image.setAlignment(QtCore.Qt.AlignHCenter)

        self._loadButton = QtWidgets.QPushButton("Load")
        self._loadButton.setObjectName("acceptButton")
        self._loadButton.setFixedHeight(40)
        self._loadButton.clicked.connect(self.load)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._image)
        layout.addStretch(1)
        layout.addWidget(self._loadButton)

        self.setLayout(layout)

    def load(self):
        """Triggered when the user clicks the load button."""
        self._item.load()

    def resizeEvent(self, event):
        """
        Overriding to adjust the image size when the widget changes size.

        :type event: QtCore.QSizeEvent
        """
        width = self.width() / 1.2
        transformMode = QtCore.Qt.SmoothTransformation
        pixmap = self._pixmap.scaledToWidth(width, transformMode)
        self._image.setPixmap(pixmap)


studiolibrary.registerItem(MayaFileItem)


def main():
    """The main entry point for this example."""
    with studioqt.app():

        path = os.path.join(studiolibrary.DIRNAME, "examples", "data")

        studiolibrary.main(name="Example", path=path)


if __name__ == "__main__":
    main()
