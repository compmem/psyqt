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
from PyQt4.QtCore import QTimer,Qt
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
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
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

# Some basic states
class ShowState(ExpState):
    def __init__(self, items, duration=None,
                 update_screen=True, parent=None):
        if not isinstance(items,list):
            items = [items]
        self.items = items
        self.duration = duration
        self.update_screen = update_screen
        ExpState.__init__(self, parent=parent)

    def onEntry(self, ev):
        self._last_time = now()
        # add the items
        for i in self.items:
            vid.scene.addItem(i)

        exp.processEvents()
        
        if self.update_screen:
            # schedule the update
            QTimer.singleShot(0,self._updateScreen)

        if not self.duration is None:
            # schedule the removal
            QTimer.singleShot(self.duration-LAG,self._removeItems)
            QTimer.singleShot(self.duration,self._updateScreen)
            QTimer.singleShot(self.duration,self._finalize)
        else:
            QTimer.singleShot(0,self._finalize)

    def _removeItems(self):
        for i in self.items:
            vid.scene.removeItem(i)
            
    def _updateScreen(self):
        vid.glw.swapBuffers()
        new_time = now()
        print self.items[0].text(), new_time, new_time - self._last_time
        self._last_time = new_time 

def show(items,duration=None,update_screen=True,parent=None):
    s = ShowState(items, duration=duration, update_screen=update_screen,
                  parent=exp._current_parent)
    exp._add_transition_if_needed(s)
    return s


class HideState(ExpState):
    def __init__(self, items, update_screen=True, parent=None):
        if not isinstance(items,list):
            items = [items]
        self.items = items
        self.update_screen = update_screen
        ExpState.__init__(self, parent=parent)

    def onEntry(self, ev):
        self._last_time = now()
        # add the items
        for i in self.items:
            vid.scene.removeItem(i)

        if self.update_screen:
            # schedule the update
            QTimer.singleShot(0,self._updateScreen)

        QTimer.singleShot(0,self._finalize)
            
    def _updateScreen(self):
        vid.glw.swapBuffers()
        new_time = now()
        print self.items[0].text(), new_time, new_time - self._last_time
        self._last_time = new_time 

def hide(items,update_screen=True,parent=None):
    s = HideState(items, update_screen=update_screen,
                  parent=exp._current_parent)
    exp._add_transition_if_needed(s)
    return s


class UpdateScreenState(ExpState):
    def __init__(self, parent=None):
        ExpState.__init__(self, parent=parent)

    def onEntry(self, ev):
        self._last_time = now()
        vid.glw.swapBuffers()
        new_time = now()
        print "update_screen", new_time, new_time - self._last_time
        self._last_time = new_time 

def update_screen(parent=None):
    s = UpdateScreenState(parent=exp._current_parent)
    exp._add_transition_if_needed(s)
    return s

# Some graphics objects
class Text(QGraphicsSimpleTextItem):
    """
    Class to create a simple text object.
    """
    def __init__(self,txt,font=def_font,loc=(0,0)):
        QGraphicsSimpleTextItem.__init__(self,txt)
        self.setPos(*loc)
        self.setFont(font)



if __name__ == "__main__":

    from experiment import parallel,serial,WaitState,wait,now,run

    show(Text("+",loc=(400,300)),duration=1000)
    wait(1000)
    with parallel():
        show(Text("Jubba",loc=(400,300)),duration=1000)
        show(Text("Jubba2",loc=(200,100)),duration=2000)
        with serial():
            wait(1000)
            show(Text("Wubba",loc=(300,200)),duration=4000)
        with serial():
            wait(1500)
            show(Text("Lubba",loc=(500,400)),duration=3000)


    # now for alternate timing methods
    show(Text("+",loc=(400,300)),duration=1000)
    wait(1000)
    jw = [Text("Jubba",loc=(400,300)),
          Text("Wubba",loc=(300,200))]
    with parallel():
        show(jw[0])
        with serial():
            wait(1000)
            show(jw[1],update_screen=False)
            update_screen()
        with serial():
            wait(1995)
            hide(jw,update_screen=False)
        wait(2000)
    update_screen()
    
    run()
