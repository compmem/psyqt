#emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See the COPYING file distributed along with the psyqt package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

# import main modules
from __future__ import with_statement
import random

# Import Qt modules
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QWidget,QGraphicsScene,QGraphicsView,QPainter
from PyQt4.QtGui import QGraphicsSimpleTextItem,QFont
from PyQt4.QtOpenGL import QGLWidget,QGLFormat

# import local modules
from experiment import exp,ExpState

# set some defaults
def_font = QFont("Helvetica")
def_font.setPointSize(60)

class Video(QWidget):
    def __init__(self):
        # init the widget
        QWidget.__init__(self)

        # set up the scene
        self.scene=QGraphicsScene()
        self.scene.setSceneRect(0,0,800,600)

        # add a view of that scene
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setFixedSize(800,600)
        
        qglf = QGLFormat()
        qglf.setSampleBuffers(True)
        self.glw = QGLWidget(qglf)
        self.glw.setAutoBufferSwap(False)
        self.view.setViewport(self.glw)

        QTimer.singleShot(0,self.glw.swapBuffers)

    def show(self):
        # shows the viewer widget
        self.view.show()


# make video instance
vid = Video()
vid.show()

# litte constants
LAG = 5

# Some important states
class ShowState(ExpState):
    def __init__(self, items, duration=None,
                 update_screen=True, parent=None):
        if not isinstance(items,list):
            items = [items]
        for i in range(len(items)):
            items[i] = QGraphicsSimpleTextItem(items[i])
            items[i].setPos(random.randint(300,500),
                            random.randint(200,400))
            items[i].setFont(def_font)

        self.items = items
        self.duration = duration
        self.update_screen = update_screen
        ExpState.__init__(self, parent=parent)

    def onEntry(self, ev):
        self._last_time = now()
        # add the items
        for i in self.items:
            vid.scene.addItem(i)

        if self.update_screen:
            # schedule the update
            QTimer.singleShot(0,self._updateScreen)

        if not self.duration is None:
            # schedule the removal
            QTimer.singleShot(self.duration-LAG,self._removeItems)
            QTimer.singleShot(self.duration,self._updateScreen)

        QTimer.singleShot(self.duration,self._finalize)

    def _removeItems(self):
        for i in self.items:
            vid.scene.removeItem(i)
            
    def _updateScreen(self):
        vid.glw.swapBuffers()
        new_time = now()
        print self.items[0].text(), new_time - self._last_time
        self._last_time = new_time 


def show(items,duration=None,update_screen=True,parent=None):
    s = ShowState(items, duration=duration, update_screen=update_screen,
                  parent=exp._current_parent)
    exp._add_transition_if_needed(s)
    return s


if __name__ == "__main__":

    from experiment import parallel,serial,WaitState,wait,now,run

    show("+",duration=1000)
    wait(1000)
    with parallel():
        show("Jubba",duration=1000)
        show("Jubba2",duration=2000)
        with serial():
            wait(1000)
            show("Wubba",duration=4000)
        with serial():
            wait(1500)
            show("Lubba",duration=3000)

    run()
