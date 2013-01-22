'''
Created on 20.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import sys
import locale
import urllib

from gi.repository import Nautilus, GObject, Gtk
from locale import gettext as _

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/nautilus-advacl")

import nautilusadvacllib as advacllib

class AdvACLExtension(GObject.GObject, Nautilus.PropertyPageProvider):
    def __init__(self):
        #locale.bindtextdomain('nautilusadvacl', '/opt/extras.ubuntu.com/qreator/share/locale/')
        locale.textdomain('nautilusadvacl')
        self.advacllibrary = advacllib.AdvACLLibrary()
    
    def get_property_pages(self, files):
        if len(files) != 1:
            return
        
        file = files[0]
        print file.get_uri_scheme()
        if file.get_uri_scheme() != 'file':
            return
        
        self.filename = urllib.unquote(file.get_uri()[7:])
        print self.filename

        self.property_label = Gtk.Label(_("Advanced ACL"))
        self.property_label.show()   
        
        self.builder = Gtk.Builder()
        self.builder.add_objects_from_file("/home/rene/DEV/eclipse/nautilus-advacl/nautilus-prop.glade", ["boxMain"])
        self.bbox = self.builder.get_object("boxMain")
        self.bbox.show()
        
        self.init_widgets()
        self.load_acls()
        
        return Nautilus.PropertyPage(name="Advanced ACL",
                                     label=self.property_label, 
                                     page=self.bbox),
                                    
    def load_acls(self):
        # We load the acls from file and update the treeview
        tvObjects = self.builder.get_object("tvObjects")
        tvPermissions = self.builder.get_object("tvPermissions")
        tvObjects.set_model(None)
        
        permList = self.advacllibrary.get_permissions(self.filename)
        permStore = Gtk.ListStore(GObject.TYPE_PYOBJECT, str)
        
        for permObj in permList:
            permStore.append([permObj, permObj.object + " (" + permObj.realm + ")"])
            
        tvObjects.set_model(permStore)
        
    def init_widgets(self):
        self.tvObjects = self.builder.get_object("tvObjects")
        self.tvPermissions = self.builder.get_object("tvPermissions")
        self.btnPermApply = self.builder.get_object("btnPermApply")
        
        # tvObjects
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Object"), renderer, text=1)
        self.tvObjects.append_column(column)
        
        selection = self.tvObjects.get_selection()
        selection.connect("changed", self.tvObjects_sel_changed)
        #tvObjects.connect("cursor-changed", self.tvObjects_sel_changed)
        
        # tvPermissions
        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn(_("Object"), renderer, text=1)
        column2.set_min_width(350)
        self.tvPermissions.append_column(column2)
        
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.tvPermissions_toggled)
        column_toggle = Gtk.TreeViewColumn(_("Grant"), renderer_toggle, active=2)
        column_toggle.set_min_width(100)
        self.tvPermissions.append_column(column_toggle)
        
        #renderer_toggle2 = Gtk.CellRendererToggle()
        #column_toggle2 = Gtk.TreeViewColumn(_("Deny"), renderer_toggle2, active=2)
        #self.tvPermissions.append_column(column_toggle2)
        
        # tvPermissions data
        store = Gtk.ListStore(str, str, bool)
        store.append(["r", _("Read"), False])
        store.append(["w", _("Write"), False])
        store.append(["x", _("Execute"), False])
        self.tvPermissions.set_model(store)
        
        # btnPermApply
        self.btnPermApply.connect("clicked", self.btnPermApply_clicked)
        
    def tvObjects_sel_changed(self, sel):
        #print "selection changed2!!!"

        tv, iter = sel.get_selected()
        if not iter:
            return
        
        model = self.tvObjects.get_model()
        objACL = model.get_value(iter, 0)
        #print "selected", model.get_value(iter, 1)
        self.tvPermissions_set_permission(objACL.perm)
        
    def tvPermissions_set_permission(self, objPerm):
        model = self.tvPermissions.get_model()
        
        model[0][2] = objPerm.read
        model[1][2] = objPerm.write
        model[2][2] = objPerm.execute
        
    def tvPermissions_toggled(self, widget, path):
        model = self.tvPermissions.get_model()
        iter = model.get_iter(path)
        attr = model.get_value(iter, 0)
        state = model.get_value(iter, 2)
        
        selection = self.tvObjects.get_selection()
        tv, iterObjects = selection.get_selected()
        objectsModel = self.tvObjects.get_model()
        objACL = objectsModel.get_value(iterObjects, 0)
        
        print objACL.perm.format_as_string()
        
        if state == True:
            model.set_value(iter, 2, False)
            objACL.perm.setPerm(attr, False)
        elif state == False:
            model.set_value(iter, 2, True)
            objACL.perm.setPerm(attr, True)
            
    def btnPermApply_clicked(self, button):
        objectsModel = self.tvObjects.get_model()
        
        # We check now if there are any changed settings
        for aclObj in objectsModel:
            objACL = aclObj[0]
            if objACL.perm.changed == True:
                print objACL.object
                self.advacllibrary.set_permissions(objACL, self.filename)