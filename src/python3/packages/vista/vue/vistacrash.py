#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# [SNIPPET_NAME: Crash Handler]
# [SNIPPET_CATEGORIES: PyGTK, Apport]
# [SNIPPET_DESCRIPTION: a custom except hook for your applications that catches Python exceptions and displays a GTK dialog]
# [SNIPPET_AUTHOR: David D. Lowe <daviddlowe.flimm@gmail.com>]
# [SNIPPET_LICENSE: MIT]
#
# Copyright 2010 David D. Lowe
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""GTK except hook for your applications.
To use, simply import this module and call gtkcrashhandler.initialize().
Import this module before calling Gtk.main().

If gtkcrashhandler cannot import gtk, pygtk, pango or gobject,
gtkcrashhandler will print a warning and use the default excepthook.

If you're using multiple threads, use gtkcrashhandler_thread decorator."""

import sys
import os
import time
import tempfile
try:
    if os.environ.get('DISPLAY'):
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, GObject, Pango
        _gtk_initialized = True
except Exception:
    print("gtkcrashhandler could not load GTK 3", file=sys.stderr)
    _gtk_initialized = False
import traceback
from gettext import gettext as _
import threading

APP_NAME = None
MESSAGE = _("Merci de nous aider à résoudre le problème. \n" \
          "Pour cela, envoyez un mail à XXX_YYY@mail.fr \n en copiant/collant le contenu " \
          "du détail ci-dessous.\n" \
          "Merci.")
USE_APPORT = False

_old_sys_excepthook = None # None means that initialize() has not been called yet

def initialize(app_name=None, message=None, use_apport=False, window=None):
    """Initialize the except hook built on GTK.

    Keyword arguments:
    app_name   -- The current application's name to be read by humans,
                  untranslated.
    message    -- A message that will be displayed in the error dialog,
                  replacing the default message string. Untranslated.
                  If you don't want a message, pass "".
    use_apport -- If set to True, gtkcrashhandler will override the settings
                  in /etc/default/apport and call apport if possible,
                  silently failing if not.
                  If set to False, the normal behaviour will be executed,
                  which may mean Apport kicking in anyway.

    """
    global APP_NAME, MESSAGE, USE_APPORT, _gtk_initialized, _old_sys_excepthook, WINDOW
    if app_name:
        APP_NAME = _(app_name)
    if not message is None:
        MESSAGE = _(message)
    if use_apport:
        USE_APPORT = use_apport
    WINDOW = window
    if _gtk_initialized == True and _old_sys_excepthook is None:
        # save sys.excepthook first, as it may not be sys.__excepthook__
        # (for example, it might be Apport's python hook)
        _old_sys_excepthook = sys.excepthook
        # replace sys.excepthook with our own
        sys.excepthook = _replacement_excepthook


def _replacement_excepthook(my_type, value, tracebk, thread=None):
    """This function will replace sys.excepthook."""
    if str(value) == "FigureManagerGTK3Agg instance has no attribute 'canvas'" :
        os._exit(1)
    # create traceback string and print it
    tb = "".join(traceback.format_exception(my_type, value, tracebk))
    if thread:
        if not isinstance(thread, threading._MainThread):
            tb = "Exception in thread %s:\n%s" % (thread.getName(), tb)
    print(tb, file=sys.stderr)

    # determine whether to add a "Report problem..." button
    add_apport_button = False
    global USE_APPORT
    global WINDOW

    res = show_error_window(tb, add_apport_button=add_apport_button)

    if res in (2, 3): # quit
        sys.stderr = tempfile.NamedTemporaryFile()
        global _old_sys_excepthook
        _old_sys_excepthook(my_type, value, tracebk)
        sys.stderr = sys.__stderr__
        os._exit(1)
    else :
        if WINDOW :
            WINDOW.get_window().set_cursor(None)

def show_error_window(error_string, add_apport_button=False):
    """Displays an error dialog, and returns the response ID.

    error_string       -- the error's output (usually a traceback)
    add_apport_button  -- whether to add a 'report with apport' button

    Returns the response ID of the dialog, 1 for ignore, 2 for close and
    3 for apport.
    """
    # initialize dialog
    title = _("Une erreur est survenue.")
    global APP_NAME
    if APP_NAME:
        title = APP_NAME
    dialog = Gtk.Dialog(title, WINDOW)

    # title Label
    label = Gtk.Label()
    label.set_markup("<b>" + _("Il semblerait qu'une erreur se soit produite") + "</b>")
    label.set_alignment(0, 0.5)
    dialog.get_content_area().pack_start(label, False, False, 0)

    # message Label
    global MESSAGE
    text_label = Gtk.Label(MESSAGE)
    text_label.set_alignment(0, 0.5)
    
    text_label.set_line_wrap(True)
    def text_label_size_allocate(widget, rect):
        """Lets label resize correctly while wrapping text."""
        widget.set_size_request(rect.width, -1)
    text_label.connect("size-allocate", text_label_size_allocate)
    if not MESSAGE == "":
        dialog.get_content_area().pack_start(text_label, False, False, 0)

    # TextView with error_string
    my_buffer = Gtk.TextBuffer()
    my_buffer.set_text(error_string)
    textview = Gtk.TextView()
    textview.set_buffer(my_buffer)
    textview.set_editable(False)
    
    try:
        textview.modify_font(Pango.FontDescription("monospace 8"))
    except Exception:
        print("gtkcrashhandler: modify_font raised an exception", file=sys.stderr)
    
    # allow scrolling of textview
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scrolled.add_with_viewport(textview)
    scrolled.set_size_request(-1, 100)

    # hide the textview in an Expander widget
    expander = Gtk.Expander().new_with_mnemonic(_("_Détail"))
    expander.add(scrolled)
    dialog.get_content_area().pack_start(expander, False, False, 0)

    # add buttons
    if add_apport_button:
        dialog.add_button(_("_Report this problem..."), 3)
    # If we're have multiple threads, or if we're in a GTK callback,
    # execution can continue normally in other threads, so add button
    if Gtk.main_level() > 0 or threading.activeCount() > 1:
        dialog.add_button(_("_Ignorer l'erreur"), 1)
    dialog.add_button(("_Fermer Vista"), 2)
    dialog.set_default_response(2)

    # set dialog aesthetic preferences
    dialog.set_border_width(12)
    dialog.get_content_area().set_spacing(4)
    dialog.set_resizable(True)

    # show the dialog and act on it
    dialog.show_all()
    res = dialog.run()
    dialog.destroy()
    if res < 0:
        res = 2
    return res


def gtkcrashhandler_thread(run):
    """gtkcrashhandler_thread is a decorator for the run() method of 
    threading.Thread.

    If you forget to use this decorator, exceptions in threads will be
    printed to standard error output, and GTK's main loop will continue to run.

    #Example 1:
    class ExampleThread(threading.Thread):
        @gtkcrashhandler_thread
        def run(self):
            1 / 0 # this error will be caught by gtkcrashhandler

    #Example 2:
    def function(arg):
        arg / 0 # this error will be caught by gtkcrashhandler
    threading.Thread(target=gtkcrashhandler_thread(function), args=(1,)).start()
    """
    def gtkcrashhandler_wrapped_run(*args, **kwargs):
        try:
            run(*args, **kwargs)
        except Exception as ee:
            lock = threading.Lock()
            lock.acquire()
            tb = sys.exc_info()[2]
            if Gtk.main_level() > 0:
                GObject.idle_add(
                    lambda ee=ee, tb=tb, thread=threading.currentThread():
                    _replacement_excepthook(ee.__class__,ee,tb,thread=thread))
            else:
                time.sleep(0.1) # ugly hack, seems like threads that are
                                # started before running Gtk.main() cause
                                # this one to crash.
                                # This delay allows Gtk.main() to initialize
                                # properly.
                                # My advice: run Gtk.main() before starting
                                # any threads or don't run Gtk.main() at all
                _replacement_excepthook(ee.__class__, ee, tb,
                                        thread=threading.currentThread())
            lock.release()
    # return wrapped run if gtkcrashhandler has been initialized
    global _gtk_initialized, _old_sys_excepthook
    if _gtk_initialized and _old_sys_excepthook:
        return gtkcrashhandler_wrapped_run
    else:
        return run

if __name__ == "__main__":
    # throw test exception
    initialize(app_name="gtkcrashhandler", message="Don't worry, though. This "
        "is just a test. To use the code properly, call "
        "gtkcrashhandler.initialize() in your PyGTK app to automatically catch "
        " any Python exceptions like this.")
    class DoNotRunException(Exception):
        def __str__(self):
            return "gtkcrashhandler.py should imported, not run"
    raise DoNotRunException()
