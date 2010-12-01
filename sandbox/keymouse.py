
import sys
from PyQt4 import QtGui, QtCore
import time

# get time
now = time.time

# obtain time range for events
def time_range():
    return (last_time, current_time)

# create a generic widget
class Icon(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(100, 100, 250, 150)
        self.resize(800, 400)
        self.setWindowTitle('Events Timing Testing')
        self.setWindowIcon(QtGui.QIcon('icons/web.png'))
        self.xcoor = 0
        self.ycoor = 0
        self.pencolor = QtCore.Qt.transparent

    # define key press events
    # print time range to the terminal of a key press
    def keyPressEvent (self, event):
        if (event.key() == QtCore.Qt.Key_Escape):
            sys.exit()
        print event.text(), "press"
        print time_range()

    # define key release events
    # print time range to the terminal of a key release
    def keyReleaseEvent (self, event):
        print event.text(), "release"
        print time_range(), "\n"

    # define mouse press events
    # print time range to the terminal of a mouse press
    def mousePressEvent (self, event):
        self.setMouseTracking(not(self.hasMouseTracking()))
        print "mouse press at", "(" + str(event.x()) + "," + str(event.y()) + ")",
        print "relative position,", "(" + str(event.globalX()) + "," + str(event.globalY()) + ")",
        print "global position"
        print time_range()
        if (self.hasMouseTracking()):
            self.pencolor = QtCore.Qt.darkCyan

    # define mouse release events
    # print time range to the terminal of a mouse release
    def mouseReleaseEvent (self, event):
        print "mouse release at", "(" + str(event.x()) + "," + str(event.y()) + ")",
        print "relative position,", "(" + str(event.globalX()) + "," + str(event.globalY()) + ")",
        print "global position"
        print time_range(), "\n"
        if (not(self.hasMouseTracking())):
            self.pencolor = QtCore.Qt.transparent
        self.update()

    # define mouse movement events
    # print time range to the terminal of a mouse movement
    def mouseMoveEvent (self, event):
        self.xcoor = event.x()
        self.ycoor = event.y()
        print "mouse move at", "(" + str(event.x()) + "," + str(event.y()) + ")",
        print "relative position,", "(" + str(event.globalX()) + "," + str(event.globalY()) + ")",
        print "global position"
        print time_range(), "\n"
        self.repaint(QtGui.QRegion(self.xcoor, self.ycoor, 2, 2))

    # draw trajectory of mouse movements
    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setPen(self.pencolor)
        paint.drawRect(self.xcoor, self.ycoor, 2, 2)
        paint.end()


app = QtGui.QApplication(sys.argv)
f = bool(0)
t = bool(1)

# icon widget
icon = Icon()
# allow for keyboard input when widget is activated
icon.setFocusPolicy(QtCore.Qt.StrongFocus)
# enable widget to accept keyboard input
icon.setEnabled(t)
# set mouse tracking to false when widget is initialized
icon.setMouseTracking(f)

# show icon
icon.show()

# process events
while True:
    current_time = now()
    app.processEvents()
    last_time = current_time
    QtCore.QThread.usleep(100)


