'''
Created on 25.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import sys
import locale
import urllib

from gi.repository import Nautilus, GObject, Gtk
from locale import gettext as _

WORK_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(WORK_DIR + "/..")

import nautilusadvacllib as advacllib

class NautilusWindowAddACL(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.set_title(_("Nautilus - Add new ACL"))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(480, 600)