'''
Created on 25.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import re
import subprocess

class AdcACLPermission:
    def __init__(self, perm=None):
        self.read = False
        self.write = False
        self.execute = False
        self.changed = False
        
        self.convert(perm)
        
    def convert(self, perm):
        if perm == None:
            return
        
        if perm[0] == "r":
            self.read = True
            
        if perm[1] == "w":
            self.write = True
            
        if perm[2] == "x":
            self.execute = True
            
    def setPerm(self, attr, state):
        self.changed = True
        
        if attr == "r":
            self.read = state
        elif attr == "w":
            self.write = state
        elif attr == "x":
            self.execute = state
            
    def format_as_string(self):
        strPerm = ""
        
        strPerm += "r" if self.read else "-"
        strPerm += "w" if self.write else "-"
        strPerm += "x" if self.execute else "-"
        
        return strPerm
            
class AdcACLObject:
    def __init__(self, a_realm, a_object, a_perm=None, a_default=False):
        self.realm = a_realm
        self.object = a_object
        self.default = a_default
        if a_perm == None:
            self.perm = None
        else:
            self.perm = AdcACLPermission(a_perm)

class AdvACLLibrary:
    def __init__(self):
        #self.re_stdacl = re.compile("^(user|group|mask|other):([^:]*):{3}$")
        self.re_stdacl = re.compile("^(user|group|mask|other):([^:]*):([rwx\-]{3})$")
        self.re_dflacl = re.compile("^default:(user|group|mask|other):([^:]*):([rwx\-]{3})$")
    
    def get_permissions(self, filename, a_default=False):
        perm = []
        
        if not os.path.exists(filename):
            return perm
        
        output = subprocess.check_output(["getfacl", filename])
        out_lines = output.split("\n")
        
        regexp = ""
        if a_default == True:
            regexp = self.re_dflacl
        else:
            regexp = self.re_stdacl
        
        for line in out_lines:
            m_result = regexp.match(line)
            if m_result:
                res_realm = m_result.group(1)
                res_object = m_result.group(2)
                res_perm = m_result.group(3)
                
                if not res_object:
                    continue
                
                perm.append(AdcACLObject(res_realm, res_object, res_perm, a_default))
                    
        return perm
    
    def set_permissions(self, objAdcACL, filename):
        strPerm = ""
        
        if objAdcACL.default == True:
            strPerm += "default:"
        
        strPerm += objAdcACL.realm + ":"
        strPerm += objAdcACL.object + ":"
        strPerm += objAdcACL.perm.format_as_string() + " "
        
        try:
            subprocess.check_output(["setfacl", "-m", strPerm, filename])
        except subprocess.CalledProcessError:
            print "No success running as user, try with sudo and then give up..."
            try:
                subprocess.check_output(["pkexec", "setfacl", "-m", strPerm, filename])
            except subprocess.CalledProcessError:
                print "Command denied, coninue..."
            
    def remove_acl(self, objAdcACL, filename):
        strRemove = ""
        
        if objAdcACL.default == True:
            strRemove += "default:"
        
        strRemove += objAdcACL.realm + ":"
        strRemove += objAdcACL.object
        
        try:
            subprocess.check_output(["setfacl", "-x", strRemove, filename])
            return True
        except subprocess.CalledProcessError as e:
            print "No success running as user, try with sudo and then give up..."
            try:
                subprocess.check_output(["pkexec", "setfacl", "-x", strRemove, filename])
                return True
            except subprocess.CalledProcessError:
                print "Command denied, coninue..."
                return False