#
# BitBake Curses UI Implementation
#
# Implements an ncurses frontend for the BitBake utility.
#
# Copyright (C) 2006 Michael 'Mickey' Lauer
# Copyright (C) 2006-2007 Richard Purdie
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
    We have the following windows:

        1.) Main Window: Shows what we are ultimately building and how far we are. Includes status bar
        2.) Thread Activity Window: Shows one status line for every concurrent bitbake thread.
        3.) Command Line Window: Contains an interactive command line where you can interact w/ Bitbake.

    Basic window layout is like that:

        |---------------------------------------------------------|
        | <Main Window>               | <Thread Activity Window>  |
        |                             | 0: foo do_compile complete|
        | Building Gtk+-2.6.10        | 1: bar do_patch complete  |
        | Status: 60%                 | ...                       |
        |                             | ...                       |
        |                             | ...                       |
        |---------------------------------------------------------|
        |<Command Line Window>                                    |
        |>>> which virtual/kernel                                 |
        |openzaurus-kernel                                        |
        |>>> _                                                    |
        |---------------------------------------------------------|

"""

import os, sys, curses, itertools, time
import bb
import xmlrpclib
from bb import ui
from bb.ui import uihelper

parsespin = itertools.cycle( r'|/-\\' )

X = 0
Y = 1
WIDTH = 2
HEIGHT = 3

MAXSTATUSLENGTH = 32

class NCursesUI:
    """
    NCurses UI Class
    """
    class Window:
        """Base Window Class"""
        def __init__( self, x, y, width, height, fg=curses.COLOR_BLACK, bg=curses.COLOR_WHITE ):
            self.win = curses.newwin( height, width, y, x )
            self.dimensions = ( x, y, width, height )
            """
            if curses.has_colors():
                color = 1
                curses.init_pair( color, fg, bg )
                self.win.bkgdset( ord(' '), curses.color_pair(color) )
            else:
                self.win.bkgdset( ord(' '), curses.A_BOLD )
            """
            self.erase()
            self.setScrolling()
            self.win.noutrefresh()

        def erase( self ):
            self.win.erase()

        def setScrolling( self, b = True ):
            self.win.scrollok( b )
            self.win.idlok( b )

        def setBoxed( self ):
            self.boxed = True
            self.win.box()
            self.win.noutrefresh()

        def setText( self, x, y, text, *args ):
            self.win.addstr( y, x, text, *args )
            self.win.noutrefresh()

        def appendText( self, text, *args ):
            self.win.addstr( text, *args )
            self.win.noutrefresh()

        def drawHline( self, y ):
            self.win.hline( y, 0, curses.ACS_HLINE, self.dimensions[WIDTH] )
            self.win.noutrefresh()

    class DecoratedWindow( Window ):
        """Base class for windows with a box and a title bar"""
        def __init__( self, title, x, y, width, height, fg=curses.COLOR_BLACK, bg=curses.COLOR_WHITE ):
            NCursesUI.Window.__init__( self, x+1, y+3, width-2, height-4, fg, bg )
            self.decoration = NCursesUI.Window( x, y, width, height, fg, bg )
            self.decoration.setBoxed()
            self.decoration.win.hline( 2, 1, curses.ACS_HLINE, width-2 )
            self.setTitle( title )

        def setTitle( self, title ):
            self.decoration.setText( 1, 1, title.center( self.dimensions[WIDTH]-2 ), curses.A_BOLD )

    #-------------------------------------------------------------------------#
#    class TitleWindow( Window ):
    #-------------------------------------------------------------------------#
#        """Title Window"""
#        def __init__( self, x, y, width, height ):
#            NCursesUI.Window.__init__( self, x, y, width, height )
#            version = bb.__version__
#            title = "BitBake %s" % version
#            credit = "(C) 2003-2007 Team BitBake"
#            #self.win.hline( 2, 1, curses.ACS_HLINE, width-2 )
#            self.win.border()
#            self.setText( 1, 1, title.center( self.dimensions[WIDTH]-2 ), curses.A_BOLD )
#            self.setText( 1, 2, credit.center( self.dimensions[WIDTH]-2 ), curses.A_BOLD )

    #-------------------------------------------------------------------------#
    class ThreadActivityWindow( DecoratedWindow ):
    #-------------------------------------------------------------------------#
        """Thread Activity Window"""
        def __init__( self, x, y, width, height ):
            NCursesUI.DecoratedWindow.__init__( self, "Thread Activity", x, y, width, height )
    
        def setStatus( self, thread, text ):
            line = "%02d: %s" % ( thread, text )
            width = self.dimensions[WIDTH]
            if ( len(line) > width ):
                line = line[:width-3] + "..."
            else:
                line = line.ljust( width )
            self.setText( 0, thread, line )

    #-------------------------------------------------------------------------#
    class MainWindow( DecoratedWindow ):
    #-------------------------------------------------------------------------#
        """Main Window"""
        def __init__( self, x, y, width, height ):
            self.StatusPosition = width - MAXSTATUSLENGTH
            NCursesUI.DecoratedWindow.__init__( self, None, x, y, width, height )
            curses.nl()

        def setTitle( self, title ):
            title = "BitBake %s" % bb.__version__
            self.decoration.setText( 2, 1, title, curses.A_BOLD )
            self.decoration.setText( self.StatusPosition - 8, 1, "Status:", curses.A_BOLD )

        def setStatus(self, status):
            while len(status) < MAXSTATUSLENGTH:
                status = status + " "
            self.decoration.setText( self.StatusPosition, 1, status, curses.A_BOLD )


    #-------------------------------------------------------------------------#
    class ShellOutputWindow( DecoratedWindow ):
    #-------------------------------------------------------------------------#
        """Interactive Command Line Output"""
        def __init__( self, x, y, width, height ):
            NCursesUI.DecoratedWindow.__init__( self, "Command Line Window", x, y, width, height )

    #-------------------------------------------------------------------------#
    class ShellInputWindow( Window ):
    #-------------------------------------------------------------------------#
        """Interactive Command Line Input"""
        def __init__( self, x, y, width, height ):
            NCursesUI.Window.__init__( self, x, y, width, height )

# put that to the top again from curses.textpad import Textbox
#            self.textbox = Textbox( self.win )
#            t = threading.Thread()
#            t.run = self.textbox.edit
#            t.start()

    #-------------------------------------------------------------------------#
    def main(self, stdscr, server, eventHandler):
    #-------------------------------------------------------------------------#
        height, width = stdscr.getmaxyx()

        # for now split it like that:
        # MAIN_y + THREAD_y = 2/3 screen at the top
        # MAIN_x = 2/3 left, THREAD_y = 1/3 right
        # CLI_y = 1/3 of screen at the bottom
        # CLI_x = full

        main_left = 0
        main_top = 0
        main_height = ( height / 3 * 2 )
        main_width = ( width / 3 ) * 2
        clo_left = main_left
        clo_top = main_top + main_height
        clo_height = height - main_height - main_top - 1
        clo_width = width
        cli_left = main_left
        cli_top = clo_top + clo_height
        cli_height = 1
        cli_width = width
        thread_left = main_left + main_width
        thread_top = main_top
        thread_height = main_height
        thread_width = width - main_width

        #tw = self.TitleWindow( 0, 0, width, main_top )
        mw = self.MainWindow( main_left, main_top, main_width, main_height )
        taw = self.ThreadActivityWindow( thread_left, thread_top, thread_width, thread_height )
        clo = self.ShellOutputWindow( clo_left, clo_top, clo_width, clo_height )
        cli = self.ShellInputWindow( cli_left, cli_top, cli_width, cli_height )
        cli.setText( 0, 0, "BB>" )

        mw.setStatus("Idle")

        helper = uihelper.BBUIHelper()
        shutdown = 0
   
        try:
            cmdline = server.runCommand(["getCmdLineAction"])
            if not cmdline:
                return
            ret = server.runCommand(cmdline)
            if ret != True:
                print "Couldn't get default commandlind! %s" % ret
                return
        except xmlrpclib.Fault, x:
            print "XMLRPC Fault getting commandline:\n %s" % x
            return

        exitflag = False
        while not exitflag:
            try:
                event = eventHandler.waitEvent(0.25)
                if not event:
                    continue
                helper.eventHandler(event)
                #mw.appendText("%s\n" % event[0])
                if isinstance(event, bb.build.Task):
                    mw.appendText("NOTE: %s\n" % event._message)
                if isinstance(event, bb.msg.MsgDebug):
                    mw.appendText('DEBUG: ' + event._message + '\n')
                if isinstance(event, bb.msg.MsgNote):
                    mw.appendText('NOTE: ' + event._message + '\n')
                if isinstance(event, bb.msg.MsgWarn):
                    mw.appendText('WARNING: ' + event._message + '\n')
                if isinstance(event, bb.msg.MsgError):
                    mw.appendText('ERROR: ' + event._message + '\n')
                if isinstance(event, bb.msg.MsgFatal):
                    mw.appendText('FATAL: ' + event._message + '\n')
                if isinstance(event, bb.event.ParseProgress):
                    x = event.sofar
                    y = event.total
                    if x == y:
                        mw.setStatus("Idle")
                        mw.appendText("Parsing finished. %d cached, %d parsed, %d skipped, %d masked." 
                                % ( event.cached, event.parsed, event.skipped, event.masked ))
                    else:
                        mw.setStatus("Parsing: %s (%04d/%04d) [%2d %%]" % ( parsespin.next(), x, y, x*100/y ) )
#                if isinstance(event, bb.build.TaskFailed):
#                    if event.logfile:
#                        if data.getVar("BBINCLUDELOGS", d):
#                            bb.msg.error(bb.msg.domain.Build, "log data follows (%s)" % logfile)
#                            number_of_lines = data.getVar("BBINCLUDELOGS_LINES", d)
#                            if number_of_lines:
#                                os.system('tail -n%s %s' % (number_of_lines, logfile))
#                            else:
#                                f = open(logfile, "r")
#                                while True:
#                                    l = f.readline()
#                                    if l == '':
#                                        break
#                                    l = l.rstrip()
#                                    print '| %s' % l
#                                f.close()
#                        else:
#                            bb.msg.error(bb.msg.domain.Build, "see log in %s" % logfile)

                if isinstance(event, bb.command.CookerCommandCompleted):
                    exitflag = True
                if isinstance(event, bb.command.CookerCommandFailed):
                    mw.appendText("Command execution failed: %s" % event.error)
                    time.sleep(2)
                    exitflag = True
                if isinstance(event, bb.cooker.CookerExit):
                    exitflag = True

                if helper.needUpdate:
                    activetasks, failedtasks = helper.getTasks()
                    taw.erase()
                    taw.setText(0, 0, "")
                    if activetasks:
                        taw.appendText("Active Tasks:\n")
                        for task in activetasks:
                            taw.appendText(task)
                    if failedtasks:
                        taw.appendText("Failed Tasks:\n")
                        for task in failedtasks:
                            taw.appendText(task)

                curses.doupdate()
            except KeyboardInterrupt:
                if shutdown == 2:
                    mw.appendText("Third Keyboard Interrupt, exit.\n")
                    exitflag = True
                if shutdown == 1:
                    mw.appendText("Second Keyboard Interrupt, stopping...\n")
                    server.runCommand(["stateStop"])
                if shutdown == 0:
                    mw.appendText("Keyboard Interrupt, closing down...\n")
                    server.runCommand(["stateShutdown"])
                shutdown = shutdown + 1
                pass

def init(server, eventHandler):
    if not os.isatty(sys.stdout.fileno()):
        print "FATAL: Unable to run 'ncurses' UI without a TTY."
        return
    ui = NCursesUI()
    try:
        curses.wrapper(ui.main, server, eventHandler)
    except:
        import traceback
        traceback.print_exc()

