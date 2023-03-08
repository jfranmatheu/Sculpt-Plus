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
    "blender" : (3, 3, 1),
    "version" : (1, 0, 1),
    "location" : "3D Viewport > Sculpt Mode",
    "warning" : "BETA VERSION! May be unstable!",
    "category" : "General"
}

if __package__ != 'sculpt_plus':
    import sys
    print("[Sculpt+] Please, rename the addon folder as 'sculpt_plus'")
    sys.exit(0)

import bpy
if bpy.app.background:
    print("[Sculpt+] Addon doesn't work in background!")
    def register(): pass
    def unregister(): pass
else:
    from . import auto_load

    auto_load.init()

    def register():
        auto_load.register()

    def unregister():
        auto_load.unregister()
