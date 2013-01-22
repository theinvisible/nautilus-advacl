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

def tvObjects_sel_changed(sel):
    #print "selection changed2!!!"
    global tvObjects

    tv, iter = sel.get_selected()
    if not iter:
        return
    
    model = tvObjects.get_model()
    objACL = model.get_value(iter, 0)
    #print "selected", model.get_value(iter, 1)
    tvPermissions_set_permision(objACL.perm)
    
def tvPermissions_set_permision(objPerm):
    global tvPermissions
    
    model = tvPermissions.get_model()
    
    model[0][1] = objPerm.read
    model[1][1] = objPerm.write
    model[2][1] = objPerm.execute
    
def on_cell_toggled(widget, path):
    global tvPermissions
    
    model = tvPermissions.get_model()
    iter = model.get_iter(path)
    state = model.get_value(iter, 1)
    if state == True:
        model.set_value(iter, 1, False)
    elif state == False:
        model.set_value(iter, 1, True)

builder = Gtk.Builder()
#builder.add_objects_from_file("/home/rene/DEV/eclipse/nautilus-advacl/nautilus-prop.glade", ["boxMain"])
builder.add_from_file("/home/rene/DEV/eclipse/nautilus-advacl/nautilus-prop.glade")
#bbox = builder.get_objects()
bbox = builder.get_object("window1")
bbox.connect("destroy", Gtk.main_quit)
print bbox
bbox.show()

# Treeview
#store = Gtk.ListStore(str)
#store.append(["test1"])
#store.append(["test2"])
#store.append(["test3"])

tvObjects = builder.get_object("tvObjects")
#tvObjects.set_model(store)

renderer = Gtk.CellRendererText()
column = Gtk.TreeViewColumn("Objekt", renderer, text=1)
tvObjects.append_column(column)

selection = tvObjects.get_selection()
selection.connect("changed", tvObjects_sel_changed)

# Treeview2
store2 = Gtk.ListStore(str, bool)
store2.append(["Lesen", False])
store2.append(["Schreiben", False])
store2.append(["Ausfuehren", False])

tvPermissions = builder.get_object("tvPermissions")
tvPermissions.set_model(store2)

renderer2 = Gtk.CellRendererText()
column2 = Gtk.TreeViewColumn("Objekt", renderer, text=0)
column2.set_min_width(250)
tvPermissions.append_column(column2)

renderer_toggle = Gtk.CellRendererToggle()
renderer_toggle.connect("toggled", on_cell_toggled)
column_toggle = Gtk.TreeViewColumn("Zulassen", renderer_toggle, active=1)
tvPermissions.append_column(column_toggle)

#renderer_toggle2 = Gtk.CellRendererToggle()
#column_toggle2 = Gtk.TreeViewColumn("Verweigern", renderer_toggle2, active=2)
#tvPermissions.append_column(column_toggle2)

lib = nautilusadvacllib.AdvACLLibrary()
perms = lib.get_permissions("/home/rene/tmp/test")

store = Gtk.ListStore(GObject.TYPE_PYOBJECT, str)

for perm in perms:
    print perm.realm, perm.object, perm.perm
    store.append([perm, perm.object])
    
tvObjects.set_model(store)

Gtk.main()