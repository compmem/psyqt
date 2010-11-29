
import sys
from PySide import QtGui, QtCore
from PySide.QtCore import QThread
import time

# get time
# set up the basic timer
import time
if sys.platform == 'win32':
    now = time.clock
else:
    now = time.time
last_time = now()
new_time = now()
def get_event_time():
    """
    Return the time range (time, range) in which we are sure the
    latest set of events occurred.
    """
    return (last_time,new_time-last_time)

# create a generic widget
class Icon(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('icons/web.png'))

    # define key press events and event processing
    # print time to the terminal of a particular key press
    def keyPressEvent (self, event):
        if now() < timeLength:
            if event.key() == QtCore.Qt.Key_Y:
                print "y input"
                print "trange =", get_event_time()
                print "now =", now()
                print "time since start", now() - start, "\n"
            elif event.key() == QtCore.Qt.Key_N:
                print "n input"
                print "trange =", get_event_time()
                print "now =", now()
                print "time since start", now() - start, "\n"
        if event.key() == QtCore.Qt.Key_Escape:
            app.quit()
            sys.exit()

app = QtGui.QApplication(sys.argv)
x = bool(0)
y = bool(1)

# define key event (not used currently)
#f = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, 0, QtCore.Qt.KeypadModifier, QtCore.QString(), x, 1)

# icon widget
icon = Icon()
# allow for keyboard input when widget is activated
icon.setFocusPolicy(QtCore.Qt.StrongFocus)
# enable widget to accept keyboard input
icon.setEnabled(y)

# show icon
icon.show()

# allow user to enter input for 'interval' seconds
interval = 10
timeLength = now() + interval
start = now()
print "now =", start
print "input allowed until", timeLength, "\n"

while True:
    new_time = now()
    app.processEvents()
    last_time = new_time
    QThread.usleep(100)

#sys.exit(app.exec_())
