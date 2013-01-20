'''
Created on 20.01.2013

@author: Rene Hadler
@email:  rene@iksdeh.at
'''

import os
import re
import subprocess

class AdvACLLibrary:
    def __init__(self):
        #self.re_stdacl = re.compile("^(user|group|mask|other):([^:]*):{3}$")
        self.re_stdacl = re.compile("^(user|group|mask|other):([^:]*):([rwx\-]{3})$")
    
    def get_permissions(self, filename):
        perm = {}
        
        if not os.path.exists(filename):
            return perm
        
        output = subprocess.check_output(["getfacl", filename])
        print output
        out_lines = output.split("\n")
        
        for line in out_lines:
            m_result = self.re_stdacl.match(line)
            if m_result:
                res_realm = m_result.group(1)
                res_object = m_result.group(2)
                res_perm = m_result.group(3)
                
                print line
                
                if res_realm == "user":
                    if not res_realm in perm:
                        perm[res_realm] = {}
                        
                    perm[res_realm][res_object] = {}
                    perm[res_realm][res_object]["perm"] = res_perm
                    pass
                    
        print perm