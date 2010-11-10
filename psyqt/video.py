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
import os

# Import Qt modules
from PyQt4.QtCore import QTimer,Qt,QState
from PyQt4.QtGui import QWidget,QGraphicsScene,QGraphicsView,QPainter
from PyQt4.QtGui import QGraphicsSimpleTextItem,QFont
from PyQt4.QtOpenGL import QGLWidget,QGLFormat

# OpenGL modules
from OpenGL.GL import glDrawBuffer,GL_BACK,glColor4f
from OpenGL.GL import glBegin,GL_POINTS,glVertex2i
from OpenGL.GL import glEnd,glFinish,glPointSize

# import local modules
from experiment import exp,ExpState
from experiment import Parallel,Serial,wait,now

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

        # set the screen sync
        val = "1"
        # Set for nVidia linux
        os.environ["__GL_SYNC_TO_VBLANK"] = val
        # Set for recent linux Mesa DRI Radeon
        os.environ["LIBGL_SYNC_REFRESH"] = val

        qglf = QGLFormat()
        qglf.setSampleBuffers(True)
        #qglf.setSwapInterval(1)
        self.glw = QGLWidget(qglf)
        self.glw.setAutoBufferSwap(False)
        self.view.setViewport(self.glw)
        
        QTimer.singleShot(0,self.glw.swapBuffers)

    def swapBuffers(self):
        # first call the swap on the QGLWidget
        self.glw.swapBuffers()

        self.glw.makeCurrent()

        # The following is taken from the PsychToolbox
        # Draw a single pixel in left-top area of back-buffer. 
        # This will wait/stall the rendering pipeline
        # until the buffer flip has happened, aka immediately after the VBL has started.
        # We need the pixel as "synchronization token", so the following glFinish() really
        # waits for VBL instead of just "falling through" due to the asynchronous nature of
        # OpenGL:
        glDrawBuffer(GL_BACK)
        # We draw our single pixel with an alpha-value of zero - so effectively it doesn't
        # change the color buffer - just the z-buffer if z-writes are enabled...
        glColor4f(0.0,0.0,0.0,0.0)
        glBegin(GL_POINTS)
        glVertex2i(10,10)
        glEnd()
        # This glFinish() will wait until point drawing is finished, ergo backbuffer was ready
        # for drawing, ergo buffer swap in sync with start of VBL has happened.
        glFinish()

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
    def __init__(self, items, parent=None, event_time=None):
        if not isinstance(items,list):
            items = [items]
        self.items = items
        ExpState.__init__(self, parent=parent, event_time=event_time)

    def _run(self):
        # add the items
        print "Show:", long(now()*1000)
        for i in self.items:
            vid.scene.addItem(i)
        self._finalize()

class HideState(ExpState):
    def __init__(self, items, parent=None, event_time=None):
        if not isinstance(items,list):
            items = [items]
        self.items = items
        ExpState.__init__(self, parent=parent, event_time=event_time)

    def _run(self):
        # add the items
        print "Hide:", long(now()*1000)
        for i in self.items:
            vid.scene.removeItem(i)
        self._finalize()

class SwapState(ExpState):
    def _run(self):
        start = long(now()*1000)
        vid.swapBuffers()
        print "Swap:", start, long(now()*1000)-start
        # record when the swap returns indicating the vertical retrace
        # just happened.
        
        # essentially, we need to know when the vertical retrace
        # actually happened

        self._finalize()

class PreprocState(Parallel):
    pass

class DummyState(ExpState):
    def _run(self):
        self._finalize()

def show(items,duration=0):
    # set the current parent
    parent = exp._current_parent

    # See if there is already a swap state
    add_swap_state = True
    if parent.timeline.events.has_key(parent.cur_event_time):
        # see if there is a swap state at that time
        states = parent.timeline.events[parent.cur_event_time]
        for s in states:
            if isinstance(s,SwapState):
                # no need to add a swap state
                add_swap_state = False

                # get the preproc state for that swap
                # it will have the same parent
                preproc = None
                for c in s.parent.children():
                    if isinstance(c,PreprocState):
                        preproc = c
                        break
                if preproc is None:
                    raise AssertionError("Proprocessing state was not found.")
                # no need to keep looking
                break

    if add_swap_state:
        # create the preproc and swap with the same serial parent
        with Serial():
            with PreprocState():
                # add the show to it with lag
                ShowState(items, event_time=exp._current_parent.cur_event_time-LAG)
            # append swap state
            s = SwapState()
            exp._add_transition_if_needed(s)
    else:
        print "Appending to existing swap"
        # add the show to existing preproc (found above)
        ShowState(items, parent=preproc, 
                  event_time=preproc.cur_event_time-LAG)

        # add a new dummy state in the current flow
        s = DummyState()
        exp._add_transition_if_needed(s)

    # if we have a specified duration, wait and call hide
    if duration > 0:
        if exp._current_parent.childMode() == QState.ExclusiveStates:
            wait(duration)
            hide(items)
        else:
            with Serial():
                wait(duration)
                hide(items)
    return items


def hide(items):
    # set the current parent
    parent = exp._current_parent

    # See if there is already a swap state
    add_swap_state = True
    if parent.timeline.events.has_key(parent.cur_event_time):
        # see if there is a swap state at that time
        states = parent.timeline.events[parent.cur_event_time]
        for s in states:
            if isinstance(s,SwapState):
                # no need to add a swap state
                add_swap_state = False

                # get the preproc state for that swap
                # it will have the same parent
                for c in s.parent.children():
                    if isinstance(c,PreprocState):
                        preproc = c
                        break
                # no need to keep looking
                break

    if add_swap_state:
        # create the preproc and swap with the same serial parent
        with Serial():
            with PreprocState():
                # add the hide to it
                HideState(items, event_time=exp._current_parent.cur_event_time-LAG)
            # append swap state
            s = SwapState(parent=exp._current_parent)
            exp._add_transition_if_needed(s)
    else:
        # add the show to existing preproc (found above)
        HideState(items, parent=preproc, 
                  event_time=preproc.cur_event_time-LAG)

        # add a new dummy state in the current flow
        s = DummyState()
        exp._add_transition_if_needed(s)

    return items


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

    from experiment import run

    show(Text("+",loc=(400,300)),duration=1005)
    wait(1005)
    with Parallel():
        show(Text("Jubba",loc=(400,300)),duration=1005)
        show(Text("Jubba2",loc=(200,100)),duration=2010)
        with Serial():
            wait(1005)
            show(Text("Wubba",loc=(300,200)),duration=1005)
            show(Text("Wubba2",loc=(300,200)),duration=2010)
        with Serial():
            wait(2010)
            show(Text("Lubba",loc=(500,400)),duration=2010)

    # for i in range(10):
    #     show(Text(str(i),loc=(400,300)),duration=10)

    # run the experiment
    run()






### Scratch

# class ShowState(ExpState):
#     def __init__(self, items, duration=None,
#                  update_screen=True, parent=None):
#         if not isinstance(items,list):
#             items = [items]
#         self.items = items
#         self.duration = duration
#         self.update_screen = update_screen
#         ExpState.__init__(self, parent=parent)

#     def onEntry(self, ev):
#         self._last_time = now()
#         # add the items
#         for i in self.items:
#             vid.scene.addItem(i)

#         exp.processEvents()
        
#         if self.update_screen:
#             # schedule the update
#             QTimer.singleShot(0,self._updateScreen)

#         if not self.duration is None:
#             # schedule the removal
#             QTimer.singleShot(self.duration-LAG,self._removeItems)
#             QTimer.singleShot(self.duration,self._updateScreen)
#             QTimer.singleShot(self.duration,self._finalize)
#         else:
#             QTimer.singleShot(0,self._finalize)

#     def _removeItems(self):
#         for i in self.items:
#             vid.scene.removeItem(i)
            
#     def _updateScreen(self):
#         vid.glw.swapBuffers()
#         new_time = now()
#         print self.items[0].text(), new_time, new_time - self._last_time
#         self._last_time = new_time 





# class HideState(ExpState):
#     def __init__(self, items, update_screen=True, parent=None):
#         if not isinstance(items,list):
#             items = [items]
#         self.items = items
#         self.update_screen = update_screen
#         ExpState.__init__(self, parent=parent)

#     def onEntry(self, ev):
#         self._last_time = now()
#         # add the items
#         for i in self.items:
#             vid.scene.removeItem(i)

#         if self.update_screen:
#             # schedule the update
#             QTimer.singleShot(0,self._updateScreen)

#         QTimer.singleShot(0,self._finalize)
            
#     def _updateScreen(self):
#         vid.glw.swapBuffers()
#         new_time = now()
#         print self.items[0].text(), new_time, new_time - self._last_time
#         self._last_time = new_time 

# class UpdateScreenState(ExpState):
#     def __init__(self, parent=None):
#         ExpState.__init__(self, parent=parent)

#     def onEntry(self, ev):
#         self._last_time = now()
#         vid.glw.swapBuffers()
#         new_time = now()
#         print "update_screen", new_time, new_time - self._last_time
#         self._last_time = new_time 


    # # now for alternate timing methods
    # show(Text("+",loc=(400,300)),duration=1000)
    # wait(1000)
    # jw = [Text("Jubba",loc=(400,300)),
    #       Text("Wubba",loc=(300,200))]
    # with Parallel():
    #     show(jw[0])
    #     with Serial():
    #         wait(1000)
    #         show(jw[1],update_screen=False)
    #         update_screen()
    #     with Serial():
    #         wait(1995)
    #         hide(jw,update_screen=False)
    #     wait(2000)
    # update_screen()
    
