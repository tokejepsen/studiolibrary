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

import mutils.gui

import studioqt

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

__all__ = [
    "ThumbnailCaptureMenu",
    "testThumbnailCaptureMenu"
]


class ThumbnailCaptureMenu(QtWidgets.QMenu):

    thumbnailCaptured = QtCore.Signal(str)

    def __init__(self, filename, *args):
        QtWidgets.QMenu.__init__(self, *args)

        self._filename = filename

        changeImageAction = QtWidgets.QAction('Capture new image', self)
        changeImageAction.triggered.connect(self.capture)
        self.addAction(changeImageAction)

        changeImageAction = QtWidgets.QAction('Show Capture window', self)
        changeImageAction.triggered.connect(self.showCaptureWindow)
        self.addAction(changeImageAction)

        loadImageAction = QtWidgets.QAction('Load image from disk', self)
        loadImageAction.triggered.connect(self.loadIconFromDisk)
        self.addAction(loadImageAction)

    def showWarningDialog(self):

        title = "Override Thumbnail"
        text = u"This action will delete the previous thumbnail. The " \
               u"previous image cannot be backed up. Do you want to " \
               u"confirm the action to take a new image and delete " \
               u"the previous one?"

        clickedButton = studioqt.MessageBox.warning(
            self.parent(),
            title=title,
            text=text,
            enableDontShowCheckBox=True,
        )

        if clickedButton != QtWidgets.QDialogButtonBox.StandardButton.Yes:
            raise Exception("Override thumbnail was canceled!")

    def showCaptureWindow(self):
        self.capture(show=True)

    def capture(self, show=False):

        self.showWarningDialog()

        filename = self._filename

        mutils.gui.thumbnailCapture(
            show=show,
            path=filename,
            captured=self.thumbnailCaptured.emit
        )

    def loadIconFromDisk(self):

        self.showWarningDialog()

        filter_ = "Image Files (*.png *.jpg *.bmp)"

        fileDialog = QtWidgets.QFileDialog(self, caption="Open Image", filter=filter_)
        fileDialog.fileSelected.connect(self.handleFileDialogResult)
        fileDialog.exec_()

    def handleFileDialogResult(self, filename):
        mutils.copyFile(filename, self._filename)
        self.thumbnailCaptured.emit(self._filename)


def testThumbnailCaptureMenu():
    """
    A method for testing the thumbnail capture menu.

    :rtype: None 
    """

    def thumbnailCapturedCallback(path):
        print "Captured thumbnail to:", path

    path = "c:/tmp/test.png"

    menu = ThumbnailCaptureMenu(path, True)
    menu.thumbnailCaptured.connect(thumbnailCapturedCallback)
    menu.exec_(QtGui.QCursor.pos())
