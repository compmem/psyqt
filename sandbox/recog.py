
"""Sample recognition experiment"""

import sys,time

# Import Qt modules
from PyQt4 import QtCore,QtGui, QtOpenGL

def_font=QtGui.QFont("Helvetica")
def_font.setPointSize(60)

# Create a class for our main window
class Exp(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        # set up the scene
        self.scene=QtGui.QGraphicsScene()
        self.scene.setSceneRect(0,0,800,600)
        
        # add a view of that scene
        self.view = QtGui.QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)

        # make that view use OpenGL
        qglf = QtOpenGL.QGLFormat()
        qglf.setSampleBuffers(True)
        self.glw = QtOpenGL.QGLWidget(qglf)

        # turn off auto swapping of the buffer
        self.glw.setAutoBufferSwap(False)

        # use the GL widget for viewing
        self.view.setViewport(self.glw)
        
        # initialize the time
        self.last_time = time.time()

        # start some timers to draw things (it's frustrating we have
        # to do this with timers)
        QtCore.QTimer.singleShot(0,self.updateScreen)
        QtCore.QTimer.singleShot(1000,self.jubba)

    def show(self):
        # shows the viewer widget
        self.view.show()
        #QtGui.QWidget.show(self)

    def addSimpleText(self,text,font=def_font,loc=(0,0)):
        """
        Method to add some text to the scene.
        """
        txt = QtGui.QGraphicsSimpleTextItem(text)
        txt.setFont(font)
        txt.setPos(*loc)
        self.scene.addItem(txt)
        return txt

    def updateScreen(self):
        """
        Update the screen with the latest scene.

        Lots of things are commented in/out b/c of testing.
        """
        #self.ui.view.updateScene([self.scene.sceneRect()])
        #self.scene.update()
        
        # Currently must process events for the scene to be updated (why?)
        QtGui.qApp.processEvents()

        # something here draws the scene to the view
        #self.glw.makeCurrent()
        #self.glw.paintGL()
        #self.glw.updateGL()
        self.glw.swapBuffers()
        new_time = time.time()

        # print out the time since last flip
        print new_time - self.last_time
        self.last_time = new_time

    def jubba(self):
        txt = self.addSimpleText("Jubba",loc=(400,300))
        self.updateScreen()
        #QtCore.QTimer.singleShot(1000,self.updateScreen)
        QtCore.QTimer.singleShot(2000,self.wubba)
    def wubba(self):
        txt2 = exp.addSimpleText("Wubba")
        self.updateScreen()
        #QtCore.QTimer.singleShot(1000,self.updateScreen)

# create an application (required)
app = QtGui.QApplication(sys.argv)

# and our experiment instance
exp=Exp()

# show it
exp.show()

# start the main run loop
# It's exec_ because exec is a reserved word in Python
sys.exit(app.exec_())
