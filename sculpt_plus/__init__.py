# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Sculpt +",
    "author" : "J. Fran Matheu (@jfranmatheu)",
    "description" : "",
    "blender" : (3, 6, 2),
    "version" : (1, 1, 0),
    "location" : "Topbar [S+] button > 'Sculpt+' WorkSpace",
    "warning" : "BETA VERSION! May be unstable!",
    "category" : "General"
}


PILLOW_VERSION = "Pillow>=9.3.0"
BM_VERSION = 'v1.0-b3.6.x'

USE_DEV_ENVIRONMENT = True

if __package__ != 'sculpt_plus':
    import sys
    print("[Sculpt+] Please, rename the addon folder as 'sculpt_plus'")
    sys.exit(0)

import bpy
if bpy.app.background:
    print("[Sculpt+] WARN! Addon doesn't work in background!")
    def register(): pass
    def unregister(): pass
else:
    from . import install_deps
    install_deps.install()

    from . import auto_load
    auto_load.init(USE_DEV_ENVIRONMENT)

    def register():
        auto_load.register()

    def unregister():
        auto_load.unregister()
