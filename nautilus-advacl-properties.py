'''
Created on 20.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import locale

from gi.repository import Nautilus, GObject, Gtk
from locale import gettext as _

class AdvACLExtension(GObject.GObject, Nautilus.PropertyPageProvider):
    def __init__(self):
        #locale.bindtextdomain('nautilusadvacl', '/opt/extras.ubuntu.com/qreator/share/locale/')
        locale.textdomain('nautilusadvacl')
    
    def get_property_pages(self, files):
        if len(files) != 1:
            return
        
        file = files[0]
        if file.get_uri_scheme() != 'file':
            return

        if file.is_directory():
            return

        self.property_label = Gtk.Label(_("Advanced ACL"))
        self.property_label.show()   
        
        self.builder = Gtk.Builder()
        self.builder.add_objects_from_file("/home/rene/DEV/eclipse/nautilus-advacl/nautilus-prop.glade", ["boxMain"])
        self.bbox = self.builder.get_object("boxMain")
        self.bbox.show()
        
        self.init_widgets()
        
        return Nautilus.PropertyPage(name="Advanced ACL",
                                     label=self.property_label, 
                                     page=self.bbox),
                                    
    def load_acls(self, file):
        # We load the acls from file and update the treeview
        tvObjects = self.builder.get_object("tvObjects")
        tvPermissions = self.builder.get_object("tvPermissions")
        
    def init_widgets(self):
        tvObjects = self.builder.get_object("tvObjects")
        tvPermissions = self.builder.get_object("tvPermissions")
        
        # tvObjects
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Object"), renderer, text=0)
        tvObjects.append_column(column)
        
        # tvPermissions
        renderer2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn(_("Object"), renderer, text=0)
        column2.set_min_width(250)
        tvPermissions.append_column(column2)
        
        renderer_toggle = Gtk.CellRendererToggle()
        column_toggle = Gtk.TreeViewColumn(_("Grant"), renderer_toggle, active=1)
        tvPermissions.append_column(column_toggle)
        
        renderer_toggle2 = Gtk.CellRendererToggle()
        column_toggle2 = Gtk.TreeViewColumn(_("Deny"), renderer_toggle2, active=2)
        tvPermissions.append_column(column_toggle2)