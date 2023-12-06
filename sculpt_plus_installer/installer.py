BM_MODULE_NAME = 'brush_manager'
BM_TAG_VERSION = 'v1.0-b3.6.x'
BUILD_NAME = F'{BM_MODULE_NAME}_{BM_TAG_VERSION}'


import bpy
import requests
import tempfile
# old url: import zipfile
# old url: import os
# old url: import shutil
# old url: import addon_utils
from pathlib import Path


src_path = Path(__file__).parent


class VersionError(Exception):
    pass


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

def install_bm():
    print("Installing Brush-Manager addon...")

    bpy.ops.preferences.addon_install(filepath=str(src_path / 'brush_manager_build.zip'))
    print("Brush Manager addon installed successfully!")
    bpy.ops.preferences.addon_enable(module='sculpt_plus')


def install_sculpt_plus():
    print("Installing Sculpt Plus addon...")

    bpy.ops.preferences.addon_install(filepath=str(src_path / 'sculpt_plus_build.zip'))
    print("Sculpt Plus addon installed successfully!")
    bpy.ops.preferences.addon_enable(module='sculpt_plus')
    bpy.ops.preferences.addon_show(module='sculpt_plus')
    bpy.ops.preferences.addon_expand(module='sculpt_plus')


def install_addon():
    print("Starting Sculpt Plus Intaller...")
    try:
        import brush_manager
        if hasattr(brush_manager, 'tag_version') and brush_manager.tag_version != BM_TAG_VERSION:
            raise VersionError(f"Required Brush Manager version is {BM_TAG_VERSION} but found {brush_manager.tag_version}")
    except (ModuleNotFoundError, ImportError) as e:
        install_bm()
    except VersionError as e:
        ## print("Saving data from Brush Manager's old version...")
        ## bm_data = brush_manager.prefs.get_prefs(bpy.context).serialize_data()
        print("Uninstalling Brush Manager's old version...")
        bpy.ops.preferences.addon_disable(module='brush_manager')
        bpy.ops.preferences.addon_remove(module='brush_manager')
        del brush_manager
        import sys
        del sys.modules['brush_manager']
        ## bpy.ops.preferences.addon_refresh()
        print("Brush Manager' old version uninstalled successfully!")
        install_bm()
        ## print("Loading data from Brush Manager's old version...")
        ## import brush_manager
        ## brush_manager.prefs.get_prefs(bpy.context).deserialize_data(bm_data)
    install_sculpt_plus()

    print("Uninstalling Sculpt Plus Installer...")
    bpy.ops.preferences.addon_disable(module='sculpt_plus_installer')
    bpy.ops.preferences.addon_remove(module='sculpt_plus_installer')
