# Volatility
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA 

"""
@author:       Andrew Case
@license:      GNU General Public License 2.0 or later
@contact:      atcuno@gmail.com
@organization:
"""

import volatility.obj as obj
import volatility.plugins.linux.common as linux_common
from volatility.plugins.linux.slab_info import linux_slabinfo

class linux_vma_cache(linux_common.AbstractLinuxCommand):
    """Gather VMAs from the vm_area_struct cache"""
    
    def __init__(self, config, *args): 
        linux_common.AbstractLinuxCommand.__init__(self, config, *args)
        self._config.add_option('UNALLOCATED', short_option = 'u', 
                        default = False,
                        help = 'Show unallocated',
                        action = 'store_true')       
    
    def calculate(self):
        linux_common.set_plugin_members(self)        
        
        has_owner = self.profile.obj_has_member("mm_struct", "owner")

        cache = linux_slabinfo(self._config).get_kmem_cache("vm_area_struct", self._config.UNALLOCATED)
        
        for vm in cache:
            start = vm.vm_start
            end   = vm.vm_end
            
            if has_owner and vm.vm_mm and vm.vm_mm.is_valid():
                task = vm.vm_mm.owner
                (task_name, pid) = (task.comm, task.pid)
            else:
                (task_name, pid) = ("", "")
            
            if vm.vm_file and vm.vm_file.is_valid():
                path = linux_common.get_partial_path(vm.vm_file.dentry)
            else:
                path = ""

            yield task_name, pid, start, end, path

    def render_text(self, outfd, data):

        self.table_header(outfd, [("Process", "16"), 
                          ("PID", "6"), 
                          ("Start", "[addrpad]"),
                          ("End", "[addrpad]"),
                          ("Path", "")])

        for task_name, pid, start, end, path in data:
           
            self.table_row(outfd, task_name, pid, start, end, path) 
        
 














