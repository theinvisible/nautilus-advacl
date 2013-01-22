'''
Created on 20.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import re
import subprocess

class AdcACLPermission:
    def __init__(self, perm):
        self.read = False
        self.write = False
        self.execute = False
        self.changed = False
        
        self.convert(perm)
        
    def convert(self, perm):
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
    def __init__(self, a_realm, a_object, a_perm):
        self.realm = a_realm
        self.object = a_object
        self.perm = AdcACLPermission(a_perm)

class AdvACLLibrary:
    def __init__(self):
        #self.re_stdacl = re.compile("^(user|group|mask|other):([^:]*):{3}$")
        self.re_stdacl = re.compile("^(user|group|mask|other):([^:]*):([rwx\-]{3})$")
    
    def get_permissions(self, filename):
        perm = []
        
        if not os.path.exists(filename):
            return perm
        
        output = subprocess.check_output(["getfacl", filename])
        out_lines = output.split("\n")
        
        for line in out_lines:
            m_result = self.re_stdacl.match(line)
            if m_result:
                res_realm = m_result.group(1)
                res_object = m_result.group(2)
                res_perm = m_result.group(3)
                
                if not res_object:
                    continue
                
                perm.append(AdcACLObject(res_realm, res_object, res_perm))
                    
        return perm
    
    def set_permissions(self, objAdcACL, filename):
        strPerm = ""
        
        strPerm += objAdcACL.realm + ":"
        strPerm += objAdcACL.object + ":"
        strPerm += objAdcACL.perm.format_as_string() + " "
        
        print strPerm
        
        try:
            subprocess.check_output(["setfacl", "-m", strPerm, filename])
        except subprocess.CalledProcessError as e:
            print "Error occured while executing setfacl. Message: {0}".format(e.output)