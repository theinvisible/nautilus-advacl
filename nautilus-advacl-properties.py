'''
Created on 20.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import sys
import locale
import urllib
import pyinotify

from gi.repository import Nautilus, GObject, Gtk, GLib
from locale import gettext as _

WORK_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(WORK_DIR + "/nautilus-advacl")

import nautilusadvacllib as advacllib
from nautiluspropaddacl import NautilusWindowAddACL

class FileEvent(pyinotify.ProcessEvent):
    def __init__(self, objMain):
        self.main = objMain
    
    def process_IN_ATTRIB(self, event):
        print "Metadata changed:", event.pathname
        self.main.load_acls()
        self.main.tvObjects_sel_first_row()

class AdvACLExtension(GObject.GObject, Nautilus.PropertyPageProvider):
    def __init__(self):
        locale.bindtextdomain('nautilusadvacl', WORK_DIR + '/nautilus-advacl/locale/')
        locale.textdomain('nautilusadvacl')
        self.advacllibrary = advacllib.AdvACLLibrary()
    
    def init_fileeventhandler(self):
        # Install inotify handler
        print "Observing: ", self.filename
        
        wm = pyinotify.WatchManager()
        mask = pyinotify.IN_ATTRIB
        handler = FileEvent(self)
        self.notifierFile = pyinotify.Notifier(wm, handler, timeout=10)
        wdd = wm.add_watch(self.filename, mask, rec=True)
        #self.notifierFile = pyinotify.ThreadedNotifier(self.wmFile, handler)
        #self.notifierFile.start()
        
        #self.wddFile = self.wmFile.add_watch(self.filename, mask, rec=True)
        GLib.timeout_add(500, self.checkFileEvents)
        
    def checkFileEvents(self):
        self.notifierFile.process_events()
        while self.notifierFile.check_events():
            self.notifierFile.read_events()
            self.notifierFile.process_events()
            
        return True
    
    def get_property_pages(self, files):
        if len(files) != 1:
            return
        
        file = files[0]
        print file.get_uri_scheme()
        if file.get_uri_scheme() != 'file':
            return
        
        self.filename = urllib.unquote(file.get_uri()[7:])
        self.init_fileeventhandler()

        self.property_label = Gtk.Label(_("Advanced ACL"))
        self.property_label.show()   
        
        self.builder = Gtk.Builder()
        self.builder.add_objects_from_file(WORK_DIR + "/nautilus-advacl/nautilus-prop.glade", ["boxMain"])
        self.bbox = self.builder.get_object("boxMain")
        self.bbox.show()
        
        self.init_widgets()
        self.load_acls()
        
        self.tvObjects_sel_first_row()
        
        return Nautilus.PropertyPage(name="Advanced ACL",
                                     label=self.property_label, 
                                     page=self.bbox),
                                    
    def load_acls(self):
        # We load the acls from file and update the treeview
        tvObjects = self.builder.get_object("tvObjects")
        tvPermissions = self.builder.get_object("tvPermissions")
        tvObjects.set_model(None)
        
        permList = self.advacllibrary.get_permissions(self.filename, self.cbxDefaultACL.get_active())
        permStore = Gtk.ListStore(GObject.TYPE_PYOBJECT, str)
        
        for permObj in permList:
            permStore.append([permObj, permObj.object + " (" + permObj.realm + ")"])
            
        tvObjects.set_model(permStore)
        
    def init_widgets(self):
        self.tvObjects = self.builder.get_object("tvObjects")
        self.tvPermissions = self.builder.get_object("tvPermissions")
        self.btnPermApply = self.builder.get_object("btnPermApply")
        self.btnObjRemove = self.builder.get_object("btnObjRemove")
        self.btnObjAdd = self.builder.get_object("btnObjAdd")
        self.cbxDefaultACL = self.builder.get_object("cbxDefaultACL")
        
        # tvObjects
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Object"), renderer, text=1)
        self.tvObjects.append_column(column)
        
        selection = self.tvObjects.get_selection()
        selection.connect("changed", self.tvObjects_sel_changed)
        #tvObjects.connect("cursor-changed", self.tvObjects_sel_changed)
        
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
        
        # btnPermApply
        self.btnPermApply.connect("clicked", self.btnPermApply_clicked)
        
        # btnObjRemove
        self.btnObjRemove.connect("clicked", self.btnObjRemove_clicked)
        
        # btnObjAdd
        self.btnObjAdd.connect("clicked", self.btnObjAdd_clicked)
        
        # Load further widgets for adding ACLs
        #self.builder_add_acl = Gtk.Builder()
        #self.builder_add_acl.add_objects_from_file(WORK_DIR + "/nautilus-advacl/nautilus-prop-add-acl.glade", ["boxMain"])
        #boxAddACL = self.builder_add_acl.get_object("boxMain")
        
        #self.win_add_acl = NautilusWindowAddACL(self)
        #self.win_add_acl.set_modal(True)
        #self.win_add_acl.add(boxAddACL)
        self.btnObjAdd.connect("destroy", self.cleanupAdvACL)
        
        self.cbxDefaultACL.connect("toggled", self.cbxDefaultACL_toggled)
        
    def tvObjects_sel_first_row(self):
        model = self.tvObjects.get_model()
        if model.get_iter_first() == None:
            return
        
        selection = self.tvObjects.get_selection()
        selection.select_iter(model.get_iter_first())
        
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
                
    def btnObjRemove_clicked(self, button):
        objectsModel = self.tvObjects.get_model()
        selection = self.tvObjects.get_selection()
        tv, iterObjects = selection.get_selected()
        if not iterObjects:
            return
        
        objACL = objectsModel.get_value(iterObjects, 0)
        
        # We remove now the selected entry
        print "removing", objACL.object
        if self.advacllibrary.remove_acl(objACL, self.filename):
            objectsModel.remove(iterObjects)
            
    def btnObjAdd_clicked(self, button):
        # Yeah, we need to load the glade file everytime coz else it will only show up the first time
        self.builder_add_acl = Gtk.Builder()
        self.builder_add_acl.add_objects_from_file(WORK_DIR + "/nautilus-advacl/nautilus-prop-add-acl.glade", ["boxMain"])
        self.win_add_acl = NautilusWindowAddACL(self)
        self.win_add_acl.show()
        
    def cleanupAdvACL(self, data):
        print "cleanup"
        #self.wmFile.rm_watch(self.wddFile.values())
        #self.notifierFile.stop()
        
    def cbxDefaultACL_toggled(self, cbx):
        print "default toggled"
        self.load_acls()
        self.tvObjects_sel_first_row()