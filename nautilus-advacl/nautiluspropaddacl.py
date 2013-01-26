'''
Created on 25.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import sys
import locale
import urllib

import pwd, grp

from gi.repository import Nautilus, GObject, Gtk
from locale import gettext as _

WORK_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(WORK_DIR + "/..")

import nautilusadvacllib as advacllib

class NautilusWindowAddACL(Gtk.Window):
    def __init__(self, window):
        Gtk.Window.__init__(self)
        self.advacllibrary = advacllib.AdvACLLibrary()
        
        self.set_title(_("Nautilus - Add new ACL"))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(480, 600)
        self.set_modal(True)
        
        self.objWindowMain = window
        
        self.init_widgets()
        
    def init_widgets(self):
        print "init widgets"
        self.boxMain = self.objWindowMain.builder_add_acl.get_object("boxMain")
        self.objTypes = self.objWindowMain.builder_add_acl.get_object("cbObjectTypes")
        self.tvObjects = self.objWindowMain.builder_add_acl.get_object("tvObjects")
        self.tvPermissions = self.objWindowMain.builder_add_acl.get_object("tvPermissions")
        self.btnAddObject = self.objWindowMain.builder_add_acl.get_object("btnAddObject")
        self.btnCancel = self.objWindowMain.builder_add_acl.get_object("btnCancel")
        
        self.add(self.boxMain)
        
        print self.objTypes
        
        # tvPermissions
        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn(_("Object"), renderer2, text=1)
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
        
        objTypesStore = Gtk.ListStore(str, str)
        objTypesStore.append(["user", _("Users")])
        objTypesStore.append(["group", _("Groups")])
        self.objTypes.set_model(objTypesStore)
        
        renderer_text = Gtk.CellRendererText()
        self.objTypes.connect("changed", self.cbObjectTypes_changed)
        self.objTypes.pack_start(renderer_text, True)
        self.objTypes.add_attribute(renderer_text, "text", 1)
        self.objTypes.set_active(0)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Object"), renderer, text=1)
        self.tvObjects.append_column(column)
        
        # btnObjAdd
        self.btnAddObject.connect("clicked", self.btnAddObject_clicked)
        
        # btnCancel
        self.btnCancel.connect("clicked", self.btnCancel_clicked)
        
    def cbObjectTypes_changed(self, combo):
        # Type has changed, we have to update our list of acl objects
        model = self.objTypes.get_model()
        type = model.get_value(combo.get_active_iter(), 0)
        print "current object: ", type
        
        self.tvObjects.set_model(None)
        
        objStore = Gtk.ListStore(str, str)
        
        if type == "group":
            groups = grp.getgrall()
            for group in groups:
                objStore.append([group[0], group[0]])
                
        elif type == "user":
            users = pwd.getpwall()
            for user in users:
                objStore.append([user[0], user[0]])
                
        self.tvObjects.set_model(objStore)
        
    def tvPermissions_toggled(self, widget, path):
        model = self.tvPermissions.get_model()
        iter = model.get_iter(path)
        attr = model.get_value(iter, 0)
        state = model.get_value(iter, 2)
        
        if state == True:
            model.set_value(iter, 2, False)
        elif state == False:
            model.set_value(iter, 2, True)
            
    def btnAddObject_clicked(self, button):
        model = self.tvPermissions.get_model()
        selection = self.tvObjects.get_selection()
        tv, iterObjects = selection.get_selected()
        if iterObjects == None:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, _("Not all required fields was provided"))
            dialog.format_secondary_text(_("Please choose a object you want to add."))
            dialog.run()    
            dialog.destroy()
        
            return 
        
        # Get ACL object
        objectsModel = self.tvObjects.get_model()
        object = objectsModel.get_value(iterObjects, 0)
        
        # Get ACL type
        idx = self.objTypes.get_active()
        type = self.objTypes.get_model()[idx][0]
        
        # Get ACL permissions
        permModel = self.tvPermissions.get_model()
        
        objAdvACL = advacllib.AdcACLObject(type, object)
        objPerm = advacllib.AdcACLPermission()
        objPerm.setPerm(permModel[0][0], permModel[0][2])
        objPerm.setPerm(permModel[1][0], permModel[1][2])
        objPerm.setPerm(permModel[2][0], permModel[2][2])
        objAdvACL.perm = objPerm
        
        self.advacllibrary.set_permissions(objAdvACL, self.objWindowMain.filename)
        
        self.objWindowMain.load_acls()
        self.destroy()
        
    def btnCancel_clicked(self, button):
        self.destroy()