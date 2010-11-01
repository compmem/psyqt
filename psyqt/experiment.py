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

class Timeline():
    """
    Place states on a timeline.
    """
    def __init__(self):
        self.start_time = 0
        self.events = {}

    def add_state(self, state, event_time):
        """
        Add state to event list at current time
        """
        if self.events.has_key(event_time):
            self.events[event_time].append(state)
        else:
            # add new list
            self.events[event_time] = [state]

# Base class for Experimental States
class ExpState(QState):
    """
    Base experimental state.
    """
    def __init__(self, parent=None, event_time=None):
        if parent is None:
            # grab from current exp
            parent = exp._current_parent
        # can't have children other than those we define, so must be
        # set up as ExclusiveStates
        QState.__init__(self, QState.ExclusiveStates, parent=parent)
        # set up dummy child states
        self._iState = QState(parent=self)
        self._fState = QFinalState(parent=self)
        self.setInitialState(self._iState)
        self._iState.addTransition(self._iState.finished,self._fState)

        # add to a timeline and save time
        self.parent = parent
        if event_time is None:
            event_time = self.parent.cur_event_time
        self._event_time = event_time
        parent.timeline.add_state(self, self._event_time)
        
    def _finalize(self):
        self._iState.finished.emit()

    def _run(self):
        raise NotImplementedError("Subclasses must implement this.")

    def get_wait_time(self):
        # use the state parent's timeline and the specific offset to
        # determine the desired event time of the state
        desired_time = self.parent.timeline.start_time + self._event_time/1000.
        
        # compare that with now and return the wait_time in ms
        wait_time = long((desired_time - now())*1000)
        if wait_time < 0:
            wait_time = 0
        return wait_time
            
    def onEntry(self, ev):
        """
        Default onEntry for experiment states.  Schedules when it will
        run based on the timeline.
        """
        # figure out how long to wait
        wait_time = self.get_wait_time()

        # schedule the run
        QTimer.singleShot(wait_time,self._run)
        

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
        self._exp_state = Serial(new_timeline=True) #QState(QState.ExclusiveStates)
        self._current_parent = self._exp_state

        # Set as initial state of state machine
        self._machine.addState(self._exp_state)
        self._machine.setInitialState(self._exp_state)

        # set up timer
        self._last_time = now()
        self._new_time = now()

    def _add_transition_if_needed(self, state):
        # default to stored parent
        parent = state.parentState()
        if parent == 0:
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
        self.wait_until()
        #self.exec_()

    def wait_until(self, end_time = None):
        """
        Wait until the desired time, or infinitely if no end is
        specified.
        """
        if end_time is None:
            # no end time, so just loop
            while True:
                self._new_time = now()
                self.processEvents()
                self._last_time = self._new_time
                QThread.usleep(100)
        else:
            while self._new_time < end_time:
                self._new_time = now()
                self.processEvents()
                self._last_time = self._new_time
                QThread.usleep(100)

            
# set up Parallel and serial parent states
class Parent(QState):
    def __init__(self, ChildMode=QState.ExclusiveStates, new_timeline=False):
        try:
            exp
            no_exp = False
        except:
            no_exp = True

        if no_exp:
            self._saved_parent = None
        else:
            self._saved_parent = exp._current_parent
            
        QState.__init__(self, ChildMode,
                        parent=self._saved_parent)        

        # connect to previous state if needed
        if not no_exp:
            exp._add_transition_if_needed(self)

        # add in a timeline
        if new_timeline:
            self.timeline = Timeline()
        else:
            # grab from parent
            self.timeline = self._saved_parent.timeline

        # grab the starting offset for this child
        if no_exp:
            self.cur_event_time = 0
        else:
            self.cur_event_time = self._saved_parent.cur_event_time
        
    def advance_timeline(self, offset):
        if self.childMode() == QState.ExclusiveStates:
            self.cur_event_time += offset
        
    def __enter__(self):
        # push self as current parent
        exp._current_parent = self

    def __exit__(self, type, value, tb):
        # pop the parent state
        exp._current_parent = self._saved_parent

    def __exit__(self, type, value, tb):
        # set initial state if necessary
        if exp._current_parent.childMode() == QState.ExclusiveStates:
            if len(exp._current_parent.children()) > 0:
                exp._current_parent.setInitialState(exp._current_parent.children()[0])
            # add the final state
            exp._add_transition_if_needed(QFinalState(parent=exp._current_parent))

        # pop the parent state
        exp._current_parent = self._saved_parent
    
    def onEntry(self, ev):
        # set timeline start time
        if self.timeline.start_time == 0:
            self.timeline.start_time = now()
            print self.timeline.events
        
class Parallel(Parent):
    def __init__(self,new_timeline=False):
        Parent.__init__(self, QState.ParallelStates,
                        new_timeline=new_timeline)        

class Serial(Parent):
    def __init__(self,new_timeline=False):
        Parent.__init__(self, QState.ExclusiveStates,
                        new_timeline=new_timeline)        
    

# add some Parallel and Serial decorators
def Parallel_group(fn):
    def new(*args):
        with Parallel() as pgroup:
            fn(*args)
        return pgroup
    return new

def Serial_group(fn):
    def new(*args):
        with Serial() as sgroup:
            fn(*args)
        return sgroup
    return new


# create global experiment instance
exp = Experiment(sys.argv)

def run():
    """
    Start the experiment.
    """
    sys.exit(exp.run())



# Some sample states

# class WaitState(ExpState):
#     def __init__(self, duration, jitter=None, parent = None):
#         if jitter is None:
#             jitter = 0
#         else:
#             if isinstance(jitter,list):
#                 # treat it as a range
#                 jitter = random.randint(jitter[0],jitter[1])
#             else:
#                 # start range at zero
#                 jitter = random.randint(0,jitter)
#         self.duration = duration + jitter
#         ExpState.__init__(self, parent=parent)
#     def onEntry(self, ev):
#         QTimer.singleShot(self.duration,self._finalize)
# def wait(duration, jitter=None):
#     s = WaitState(duration, parent=exp._current_parent)
#     exp._add_transition_if_needed(s)
#     return s

def wait(duration, jitter=None):
    if jitter is None:
        jitter = 0
    else:
        if isinstance(jitter,list):
            # treat it as a range
            jitter = random.randint(jitter[0],jitter[1])
        else:
            # start range at zero
            jitter = random.randint(0,jitter)
    duration = duration + jitter
    exp._current_parent.advance_timeline(duration)
    
# class PrinterState(ExpState):
#     def __init__(self, txt, parent = None):
#         self.txt = txt
#         ExpState.__init__(self, parent=parent)
#     def onEntry(self, ev):
#         self._start_time = now()
#         print self.txt
#         self._time = (self._start_time,now()-self._start_time)
#         print self._time
#         self._finalize()

class PrinterState(ExpState):
    def __init__(self, txt, parent = None, event_time=None):
        self.txt = txt
        ExpState.__init__(self, parent=parent, event_time=event_time)
    def _run(self):
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

    printer("+")
    wait(500)
    with Parallel():
        printer("Jubba")
        with Serial():
            wait(1000)
            printer("Wubba")
        with Serial():
            wait(1500)
            printer("Lubba")

    run()
