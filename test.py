'''
Created on 19.01.2013

@author: rene
'''

#!/usr/bin/python2

import sys
import os

from gi.repository import Nautilus, GObject, Gtk

#

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/nautilus-advacl")

import nautilusadvacllib

print sys.path

builder = Gtk.Builder()
#builder.add_objects_from_file("/home/rene/DEV/eclipse/nautilus-advacl/nautilus-prop.glade", ["boxMain"])
builder.add_from_file("/home/rene/DEV/eclipse/nautilus-advacl/nautilus-prop.glade")
#bbox = builder.get_objects()
bbox = builder.get_object("window1")
print bbox
bbox.show()

# Treeview
store = Gtk.ListStore(str)
#store.append(["test1"])
#store.append(["test2"])
#store.append(["test3"])

tvObjects = builder.get_object("tvObjects")
tvObjects.set_model(store)

renderer = Gtk.CellRendererText()
column = Gtk.TreeViewColumn("Objekt", renderer, text=0)
tvObjects.append_column(column)

# Treeview2
store2 = Gtk.ListStore(str, bool, bool)
#store2.append(["Lesen", False, True])
#store2.append(["Schreiben", True, False])
#store2.append(["Ausfuehren", False, True])

tvPermissions = builder.get_object("tvPermissions")
tvPermissions.set_model(store2)

renderer2 = Gtk.CellRendererText()
column2 = Gtk.TreeViewColumn("Objekt", renderer, text=0)
column2.set_min_width(250)
tvPermissions.append_column(column2)

renderer_toggle = Gtk.CellRendererToggle()
column_toggle = Gtk.TreeViewColumn("Zulassen", renderer_toggle, active=1)
tvPermissions.append_column(column_toggle)

renderer_toggle2 = Gtk.CellRendererToggle()
column_toggle2 = Gtk.TreeViewColumn("Verweigern", renderer_toggle2, active=2)
tvPermissions.append_column(column_toggle2)

lib = nautilusadvacllib.AdvACLLibrary()
lib.get_permissions("/home/rene/tmp/test")

Gtk.main()