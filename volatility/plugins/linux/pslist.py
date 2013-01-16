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
@organization: Digital Forensics Solutions
"""

import volatility.obj as obj
import volatility.plugins.linux.common as linux_common

class linux_pslist(linux_common.AbstractLinuxCommand):
    """Gather active tasks by walking the task_struct->task list"""

    def __init__(self, config, *args, **kwargs):
        linux_common.AbstractLinuxCommand.__init__(self, config, *args, **kwargs)
        config.add_option('PID', short_option = 'p', default = None,
                          help = 'Operate on these Process IDs (comma-separated)',
                          action = 'store', type = 'str')

    def calculate(self):
        linux_common.set_plugin_members(self)
        init_task_addr = self.get_profile_symbol("init_task")

        init_task = obj.Object("task_struct", vm = self.addr_space, offset = init_task_addr)

        pidlist = self._config.PID
        if pidlist:
            pidlist = [int(p) for p in self._config.PID.split(',')]

        # walk the ->tasks list, note that this will *not* display "swapper"
        for task in init_task.tasks:

            if not pidlist or task.pid in pidlist:

                yield task

    def render_text(self, outfd, data):

        self.table_header(outfd, [("Offset", "[addrpad]"),
                                  ("Name", "20"),
                                  ("Pid", "15"),
                                  ("Uid", "15"),
                                  ("Start Time", "")])
        for task in data:
            self.table_row(outfd, task.obj_offset,
                                  task.comm,
                                  str(task.pid),
                                  str(task.uid) if task.uid else "-",
                                  self.get_task_start_time(task))

class linux_memmap(linux_pslist):
    """Dumps the memory map for linux tasks"""

    def render_text(self, outfd, data):

        self.table_header(outfd, [("Task", "16"),
                                  ("Pid", "8"),
                                  ("Virtual", "[addrpad]"),
                                  ("Physical", "[addrpad]"),
                                  ("Size", "[addr]")])

        for task in data:
            task_space = task.get_process_address_space()

            pagedata = task_space.get_available_pages()
            if pagedata:
                for p in pagedata:
                    pa = task_space.vtop(p[0])
                    # pa can be 0, according to the old memmap, but can't == None(NoneObject)
                    if pa != None:
                        self.table_row(outfd, task.comm, task.pid, p[0], pa, p[1])
                    #else:
                    #    outfd.write("0x{0:10x} 0x000000     0x{1:12x}\n".format(p[0], p[1]))
            else:
                outfd.write("Unable to read pages for {0} pid {1}.\n".format(task.comm, task.pid))

