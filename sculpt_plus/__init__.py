# This program is under the terms of the GNU General Public License as published by
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
'''
if __package__ != 'sculpt_plus':
    import sys
    print("[Sculpt+] Please, rename the addon folder as 'sculpt_plus'")
    sys.exit(0)
'''

import bpy
if bpy.app.background:
    print("[Sculpt+] WARN! Addon doesn't work in background!")
    def register(): pass
    def unregister(): pass
else:
    print(f">>>>>>>>>>>>>>> Loading addon: {__package__} <<<<<<<<<<<<<<<<<<<<<<<<<")

    from . import auto_load

    auto_load.init()

    def register():
        bpy.hurr = {}
        auto_load.register()

    def unregister():
        auto_load.unregister()
        del bpy.hurr
