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

    import sys
    import bl_ext
    # sys.modules['sculpt_plus'] = bl_ext.user_default.sculpt_plus
    # print("1 +++++++++++++++++++++++++++++++++++++++", sys.modules.get('bl_ext.user_default.sculpt_plus', None))
    sys.modules['sculpt_plus'] = sys.modules.get('bl_ext.user_default.sculpt_plus', None)

    from .ackit import init_modules, register_modules, unregister_modules
    init_modules({'TYPES', 'OPS', 'ICONS'}, types_alias='splus')

    def register():
        bpy.splus = {}
        register_modules()

    def unregister():
        unregister_modules()
        del bpy.splus
