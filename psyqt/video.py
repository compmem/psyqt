#emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See the COPYING file distributed along with the psyqt package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

# Import Qt modules
from PyQt4 import QtCore,QtGui,QtOpenGL

class Video(QtGui.QWidget):
    def __init__(self):
        # init the widget
        QtGui.QWidget.__init__(self)

        # set up the scene
        self.scene=QtGui.QGraphicsScene()
        self.scene.setSceneRect(0,0,800,600)

        # set up the view
        self.grview.setScene(self.scene)
        self.grview.setRenderHint(QtGui.QPainter.Antialiasing)
        self.glw = QtOpenGL.QGLWidget()
        #self.glw.setAutoBufferSwap(False)
        self.grview.setViewport(self.glw)
