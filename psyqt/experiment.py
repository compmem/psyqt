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
import sys
import random

# Import Qt modules
from PyQt4.QtCore import QState,QFinalState,QStateMachine
from PyQt4.QtCore import QTimer,QThread
from PyQt4.QtGui import QApplication

# set up the basic timer
import time
if sys.platform == 'win32':
    now = time.clock
else:
    now = time.time

# Base class for Experimental States
class ExpState(QState):
    def __init__(self, parent=None):
        # can't have children other than those we define, so must be
        # set up as ExclusiveStates
        QState.__init__(self, QState.ExclusiveStates, parent=parent)
        # set up dummy child states
        self._iState = QState(parent=self)
        self._fState = QFinalState(parent=self)
        self.setInitialState(self._iState)
        self._iState.addTransition(self._iState.finished,self._fState)
    def _finalize(self):
        self._iState.finished.emit()

#default_font=QtGui.QFont("Helvetica")
#default_font.setPointSize(60)

# Create a class for our main window
class Experiment(QApplication):
    def __init__(self,argv):
        # init the widget
        QApplication.__init__(self,argv)

        # set up the state machine
        self._machine = QStateMachine()

        # Start with a top-level serial state
        self._exp_state = QState(QState.ExclusiveStates)
        self._current_parent = self._exp_state

        # Set as initial state of state machine
        self._machine.addState(self._exp_state)
        self._machine.setInitialState(self._exp_state)

        # set up timer
        self._last_time = now()
        self._new_time = now()

    def _add_transition_if_needed(self, state):
        # default to stored parent
        parent = self._current_parent
        children = parent.children()
        
        # if serial
        if parent.childMode() == QState.ExclusiveStates:
            # if no previous states, must set as initial state
            if len(children) > 1:
                # add transition to previons
                prev = children[-2]
                prev.addTransition(prev.finished, state)
            elif len(children) == 1 and parent.initialState() is None:
                # set the new state as the initial
                parent.setInitialState(state)

    def _event_time(self):
        """
        Return the time range (time, range) in which we are sure the
        latest set of events occurred.
        """
        return (self._last_time,self._new_time-self._last_time)

    def run(self):
        """
        Run the experiment made up of the State Machine.
        """
        # make sure toplevel _exp_state has initial state if necessary
        if len(self._exp_state.children())>0 and \
               self._exp_state.initialState() is None:
            self._exp_state.setInitialState(exp._exp_state.children()[0])
        # add the final state
        exp._add_transition_if_needed(QFinalState(parent=self._exp_state))
            
        # start the state machine
        self._machine.start()

        # enter event loop
        while True:
            self._new_time = now()
            self.processEvents()
            self._last_time = self._new_time
            QThread.usleep(100)
        #self.exec_()

# create global experiment instance
exp = Experiment(sys.argv)

def run():
    """
    Start the experiment.
    """
    sys.exit(exp.run())



# set up parallel and serial parent states
class parallel(QState):
    def __init__(self):
        self._saved_parent = exp._current_parent
        QState.__init__(self, QState.ParallelStates,
                        parent=self._saved_parent)        

        exp._add_transition_if_needed(self)

    def __enter__(self):
        # push self as current parent
        exp._current_parent = self

    def __exit__(self, type, value, tb):
        # pop the parent state
        exp._current_parent = self._saved_parent

class serial(QState):
    def __init__(self):
        self._saved_parent = exp._current_parent
        QState.__init__(self, QState.ExclusiveStates,
                        parent=self._saved_parent)        

        exp._add_transition_if_needed(self)

    def __enter__(self):
        # push a serial parent state
        exp._current_parent = self

    def __exit__(self, type, value, tb):
        # set initial state if necessary
        if len(exp._current_parent.children()) > 0:
            exp._current_parent.setInitialState(exp._current_parent.children()[0])
        # add the final state
        exp._add_transition_if_needed(QFinalState(parent=exp._current_parent))

        # pop the parent state
        exp._current_parent = self._saved_parent
    

# add some parallel and serial decorators
def parallel_group(fn):
    def new(*args):
        with parallel() as pgroup:
            fn(*args)
        return pgroup
    return new

def serial_group(fn):
    def new(*args):
        with serial() as sgroup:
            fn(*args)
        return sgroup
    return new


class WaitState(ExpState):
    def __init__(self, duration, jitter=None, parent = None):
        if jitter is None:
            jitter = 0
        else:
            if isinstance(jitter,list):
                # treat it as a range
                jitter = random.randint(jitter[0],jitter[1])
            else:
                # start range at zero
                jitter = random.randint(0,jitter)
        self.duration = duration + jitter
        ExpState.__init__(self, parent=parent)
    def onEntry(self, ev):
        QTimer.singleShot(self.duration,self._finalize)
def wait(duration, jitter=None):
    s = WaitState(duration, parent=exp._current_parent)
    exp._add_transition_if_needed(s)
    return s
    
class PrinterState(ExpState):
    def __init__(self, txt, parent = None):
        self.txt = txt
        ExpState.__init__(self, parent=parent)
    def onEntry(self, ev):
        self._start_time = now()
        print self.txt
        self._time = (self._start_time,now()-self._start_time)
        print self._time
        self._finalize()
def printer(txt):
    s = PrinterState(txt, parent=exp._current_parent)
    exp._add_transition_if_needed(s)
    return s

    
if __name__ == "__main__":

    with parallel():
        printer("Jubba")
        with serial():
            wait(1000)
            printer("Wubba")
        with serial():
            wait(1500)
            printer("Lubba")

    run()
