#!
 
# This is statement is required by the build system to query build info
if __name__ == '__build__':
    raise Exception
 
import string
__version__ = string.split('$Revision: 1.1.1.1 $')[1]
__date__ = string.join(string.split('$Date: 2007/02/15 19:25:21 $')[1:3], ' ')
__author__ = 'Tarn Weisner Burton <twburton@users.sourceforge.net>'

from BlobManager import *

import sys
print "Make sure /home/andrew/repos/AITD exists"
sys.path.insert(0, '/home/andrew/repos/AITD')
from MotionTracker import Target
 
#
# Ported to PyOpenGL 2.0 by Tarn Weisner Burton 10May2001
#
# This code was created by Richard Campbell '99 (ported to Python/PyOpenGL by John Ferguson 2000)
#
# The port was based on the PyOpenGL tutorial module: dots.py  
#
# If you've found this code useful, please let me know (email John Ferguson at hakuin@voicenet.com).
#
# See original source and C based tutorial at http://nehe.gamedev.net
#
# Note:
# -----
# This code is not a good example of Python and using OO techniques.  It is a simple and direct
# exposition of how to use the Open GL API in Python via the PyOpenGL package.  It also uses GLUT,
# which in my opinion is a high quality library in that it makes my work simpler.  Due to using
# these APIs, this code is more like a C program using function based programming (which Python
# is in fact based upon, note the use of closures and lambda) than a "good" OO program.
#
# To run this code get and install OpenGL, GLUT, PyOpenGL (see http://www.python.org), and PyNumeric.
# Installing PyNumeric means having a C compiler that is configured properly, or so I found.  For 
# Win32 this assumes VC++, I poked through the setup.py for Numeric, and chased through disutils code
# and noticed what seemed to be hard coded preferences for VC++ in the case of a Win32 OS.  However,
# I am new to Python and know little about disutils, so I may just be not using it right.
#
# BTW, since this is Python make sure you use tabs or spaces to indent, I had numerous problems since I 
# was using editors that were not sensitive to Python.
#
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from optparse import OptionParser
import sys
import random

from ConnectionManager import *
from GLCircles import *
 
# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'
 
# Number of the glut window.
window = 0


REVERSE_DISPLAY = False

# array of blobs to test with
blobManager = BlobManager()

# OpenCV application
cvApp = Target()
blobManager.cvApp = cvApp

# command line arguments configuration
parser = OptionParser()
parser.add_option("-f", "--fullscreen", action="store_true", help="Sets GLUT window to fullscreen")
(options, args) = parser.parse_args()

 
# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):                # We call this right after our OpenGL window is created.
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
 
    glMatrixMode(GL_MODELVIEW)
 
# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
        Height = 1
 
    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
 
# The main drawing function. 
def DrawGLScene():
    global blobManager, client
    
    # Clear The Screen And The Depth Buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()                    # Reset The View 
    
    # allow for transparency
    glEnable( GL_BLEND )
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable( GL_DEPTH_TEST )
    
    glClearColor(0.0,0.0,0.0,0.0)
    
    
    
    # move drawing curser back
    glTranslatef(0.0, 0.0, -6.0)
    
    if REVERSE_DISPLAY:
        glRotatef(180, 0.0, 1.0, 0.0)
    
    """
    if cvApp.display_image is not None:
        glTexImage2D(GL_TEXTURE_2D, 
            0, 
            GL_RGB, 
            640, 
            480, 
            0,
            GL_RGB, 
            GL_UNSIGNED_BYTE, 
            cvApp.display_image)
    
    """
    # draw background img
    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
    glColor4f(1.0, 1.0, 1.0, 0.3)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(-3.2, 3) 
    glTexCoord2f(1.0, 0.0)
    glVertex2f(3.2, 3)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(3.2, -3) 
    glTexCoord2f(0.0, 1.0)
    glVertex2f(-3.2, -3) 
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    
    
    glPushMatrix()
    blobManager.update()
    blobManager.draw()
    glPopMatrix()
    
 
    #  since this is double buffered, swap the buffers to display what just got drawn. 
    glutSwapBuffers()
 
# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
    # If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        sys.exit()
 
def main():
    global window, options
    # For now we just pass glutInit one empty argument. I wasn't sure what should or could be passed in (tuple, list, ...)
    # Once I find out the right stuff based on reading the PyOpenGL source, I'll address this.
    glutInit(sys.argv)
 
    # Select type of Display mode:   
    #  Double buffer 
    #  RGBA color
    # Alpha components supported 
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
 
    # get a 640 x 480 window 
    glutInitWindowSize(640, 480)
 
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)
 
    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python (like myself), remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("ArtInTheDark 2012")
 
       # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.    
    glutDisplayFunc(DrawGLScene)
 
    # full screen.
    if options.fullscreen:
        glutFullScreen()
 
    # When we are doing nothing, redraw the scene.
    glutIdleFunc(DrawGLScene)
 
    # Register the function called when our window is resized.
    glutReshapeFunc(ReSizeGLScene)
 
    # Register the function called when the keyboard is pressed.  
    glutKeyboardFunc(keyPressed)
 
    # Initialize our window. 
    InitGL(640, 480)
    
    # start CV
    start_new_thread(cvApp.run, ())
 
    # Start Event Processing Engine    
    glutMainLoop()
 
# Print message to console, and kick off the main to get it rolling.
print "Hit ESC key to quit."
main()
