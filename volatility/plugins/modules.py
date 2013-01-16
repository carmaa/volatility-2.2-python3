# Volatility
#
# Authors:
# Mike Auty <mike.auty@gmail.com>
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
#

#pylint: disable-msg=C0111

import volatility.plugins.common as common
import volatility.cache as cache
import volatility.win32 as win32
import volatility.utils as utils

class Modules(common.AbstractWindowsCommand):
    """Print list of loaded modules"""
    def __init__(self, config, *args, **kwargs):
        common.AbstractWindowsCommand.__init__(self, config, *args, **kwargs)
        config.add_option("PHYSICAL-OFFSET", short_option = 'P', default = False,
                          cache_invalidator = False, help = "Physical Offset", action = "store_true")

    def render_text(self, outfd, data):
        offsettype = "(V)" if not self._config.PHYSICAL_OFFSET else "(P)"
        self.table_header(outfd,
                          [("Offset{0}".format(offsettype), "[addrpad]"),
                           ("Name", "20"),
                           ('Base', "[addrpad]"),
                           ('Size', "[addr]"),
                           ('File', "")
                           ])

        for module in data:
            if not self._config.PHYSICAL_OFFSET:
                offset = module.obj_offset
            else:
                offset = module.obj_vm.vtop(module.obj_offset)
            self.table_row(outfd,
                         offset,
                         module.BaseDllName,
                         module.DllBase,
                         module.SizeOfImage,
                         module.FullDllName)


    @cache.CacheDecorator("tests/lsmod")
    def calculate(self):
        addr_space = utils.load_as(self._config)

        result = win32.modules.lsmod(addr_space)

        return result
