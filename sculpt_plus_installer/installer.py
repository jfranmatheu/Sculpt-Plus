BM_MODULE_NAME = 'brush_manager'
BM_TAG_VERSION = 'v1.0-b3.6.x'
BUILD_NAME = F'{BM_MODULE_NAME}_{BM_TAG_VERSION}'


import sys
import bpy
import requests
import tempfile
from dataclasses import dataclass
# old url: import zipfile
# old url: import os
# old url: import shutil
# old url: import addon_utils
from pathlib import Path


src_path = Path(__file__).parent


class VersionError(Exception):
    pass


@dataclass
class FakeArea:
    def tag_redraw(self):
        pass

@dataclass
class FakeContext:
    area: FakeArea

@dataclass
class AddonRemoveOperatorWrapper:
    ''' HACK since in this state Blender didn't load the  UI nor context and
        'addon_remove' operator is trying to tag_redraw the preferences UI. '''
    module: str

    def report(self, *args):
        pass


def uninstall_module(module_name: str):
    from bpy.types import PREFERENCES_OT_addon_remove
    print("Uninstalling %s's old version..." % module_name)
    bpy.ops.preferences.addon_disable(module=module_name)
    PREFERENCES_OT_addon_remove.execute(AddonRemoveOperatorWrapper(module_name), FakeContext(FakeArea()))
    for _module_name in list(sys.modules.keys()):
        if _module_name.startswith(module_name):
            del sys.modules[_module_name]


# ----------------------------------------------------------------


def install_bm_from_web():
    print("Installing Brush Manager addon...")

    try:
        import brush_manager
        if hasattr(brush_manager, 'tag_version') and brush_manager.tag_version != BM_TAG_VERSION:
            raise VersionError(f"Required Brush Manager version is {BM_TAG_VERSION} but found {brush_manager.tag_version}")

    except (ModuleNotFoundError, ImportError, VersionError) as e:
        print(e)

        url = f"https://github.com/jfranmatheu/Blender-Brush-Manager/raw/main/build/{BUILD_NAME}.zip"

        r = requests.get(url, stream=True)
        print("[Sculpt+] Install BM - Request Status Code:", r.status_code)
        if r.status_code == 200:

            # Download the .zip file.
            with tempfile.TemporaryFile(mode='w+b', suffix='.zip', delete=False) as tmpfile:
                for chunk in r.iter_content(chunk_size=128):
                    tmpfile.write(chunk)

            # BUILD URL DOWNLOAD.
            bpy.ops.preferences.addon_install(filepath=tmpfile.name)
            bpy.ops.preferences.addon_enable(module=BM_MODULE_NAME)

    '''
        # OLD URL.

        with tempfile.TemporaryDirectory(prefix='blender_') as tmp_dir:
            # Extract the zip to the addons folder.
            with zipfile.ZipFile(tmpfile.name, 'r') as zip_ref:
                unzipped_path = os.path.join(tmp_dir, zip_ref.filelist[0].filename[:-1]) # remove '/'
                zip_ref.extractall(tmp_dir)

            zip_path = os.path.join(tmp_dir, module_name)

            # Fix github and zipfile shit.
            shutil.move(os.path.join(unzipped_path, module_name), tmp_dir)
            shutil.make_archive(zip_path, 'zip', unzipped_path)
            shutil.rmtree(unzipped_path, ignore_errors=True)

            bpy.ops.preferences.addon_install(filepath=zip_path + '.zip')
            bpy.ops.preferences.addon_enable(module_name)
    '''

def load_brush_sets():
    import brush_manager
    from sculpt_plus.path import SculptPlusPaths
    print("Loading Sculpt data...")
    # First install! Let's force a load...
    # internally will create a timer_register to install when possible...
    brush_manager.api.BM_DATA.get().SCULPT # this getter should import default brushes... SHOULD...
    # brush_manager.api.BM_OPS.import_library_default( # NOTE: SCULPT+ HAS NOT DFEFAULT.BLEND FOR THIS, BUT BM addon.
    #     libpath=SculptPlusPaths.SRC_LIB_BLEND('default.blend'),
    #     ui_context_mode='SCULPT',
    #     ui_context_item='BRUSH'
    # )
    try:
        brush_manager.api.BM_OPS.import_library_internal(
            libpath=SculptPlusPaths.SRC_LIB_BRUSH_PACKS('OrbBrushes', 'OrbBrushes.blend'),
            custom_uuid='ORB_BRUSHES',
            ui_context_mode='SCULPT',
            ui_context_item='BRUSH'
        )
    except Exception:
        pass


def install_bm():
    print("Installing Brush-Manager addon...")

    bpy.ops.preferences.addon_install(filepath=str(src_path / 'brush_manager_build.zip'))
    print("Brush Manager addon installed successfully!")
    bpy.ops.preferences.addon_enable(module='brush_manager')


def install_sculpt_plus():
    print("Installing Sculpt Plus addon...")

    bpy.ops.preferences.addon_install(filepath=str(src_path / 'sculpt_plus_build.zip'))
    print("Sculpt Plus addon installed successfully!")
    bpy.ops.preferences.addon_enable(module='sculpt_plus')
    bpy.ops.preferences.addon_show(module='sculpt_plus')
    bpy.ops.preferences.addon_expand(module='sculpt_plus')


def uninstall_old_addon_versions():
    try:
        import sculpt_plus
        uninstall_module('sculpt_plus')
        del sculpt_plus
    except (ModuleNotFoundError, ImportError) as e:
        pass
    try:
        import brush_manager
        # brush_manager.api.BM_OPS.clear_data()
        uninstall_module('brush_manager')
        del brush_manager
    except (ModuleNotFoundError, ImportError) as e:
        pass


def install_addon(uninstall_old=True):
    if uninstall_old:
        uninstall_old_addon_versions()

    print("Starting Sculpt Plus Intaller...")
    version_error = False
    try:
        import brush_manager
        if hasattr(brush_manager, 'tag_version') and brush_manager.tag_version != BM_TAG_VERSION:
            raise VersionError(f"Required Brush Manager version is {BM_TAG_VERSION} but found {brush_manager.tag_version}")
    except (ModuleNotFoundError, ImportError) as e:
        install_bm()
    except VersionError as e:
        version_error = True
        uninstall_module('brush_manager')
        del brush_manager
        print("Brush Manager' old version uninstalled successfully!")
        install_bm()
    install_sculpt_plus()

    print("Uninstalling Sculpt Plus Installer...")
    bpy.ops.preferences.addon_disable(module='sculpt_plus_installer')
    bpy.ops.preferences.addon_remove(module='sculpt_plus_installer')

    if not version_error:
        bpy.app.timers.register(load_brush_sets)
