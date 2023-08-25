import subprocess
import sys
import os
import requests 
import tempfile
import bpy


# ----------------------------------------------------------------


PILL_IMPORT_ERROR = False
PILL_UPDATE_ERROR = False

def is_pil_ok() -> bool:
    global PILL_IMPORT_ERROR
    return PILL_IMPORT_ERROR


class VersionError(Exception):
    pass


# ----------------------------------------------------------------


def install():
    from . import PILLOW_VERSION, BM_VERSION

    try:
        import brush_manager
        bm_version = brush_manager.bl_info['version']
    except ImportError:
        if BM_VERSION != "latest":
            url = "https://api.github.com/repos/{}/{}/releases/tags/{}".format(
                'jfranmatheu', 'Blender-Brush-Manager', BM_VERSION)
        else:
            url = "https://api.github.com/repos/{}/{}/releases/latest".format(
                'jfranmatheu', 'Blender-Brush-Manager')

        r = requests.get(url, stream=True)
        print("[Sculpt+] Install BM - Request Status Code:", r.status_code)
        if r.status_code == 200:
            with tempfile.TemporaryFile(mode='w+b', suffix='.zip') as tmpfile:
                for chunk in r.iter_content(chunk_size=128):
                    tmpfile.write(chunk)
                bpy.ops.preferences.addon_install(filepath=tmpfile.name, overwrite=True)
                bpy.ops.preferences.addon_enable(module='brush_manager')
                bpy.ops.wm.save_userpref()

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    '''
    os.system("pip3 install -r requirements.txt")
    os.system("pip3 install -r requirements-dev.txt")
    os.system("pip3 install -r requirements-test.txt")
    '''
    # path to python.exe
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    target = os.path.join(sys.prefix, 'lib', 'site-packages')

    try:
        import PIL
        
        if not hasattr(PIL, '__version__') or float(PIL.__version__[:-2]) < 9.3:
            print("Pillow version is too old! Requires to install a recent version...")
            raise VersionError("Pillow version is too old!")

    except ImportError:
        # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])

        # install required packages
        try:
            subprocess.call([python_exe, "-m", "pip", "install", PILLOW_VERSION, "-t", target])
        except PermissionError as e:
            print(e)
            global PILL_IMPORT_ERROR
            PILL_IMPORT_ERROR = True

    except VersionError:
        try:
            subprocess.call([python_exe, "-m", "pip", "install", '--ignore-installed', PILLOW_VERSION, "-t", target])
        except PermissionError as e:
            print(e)
            global PILL_UPDATE_ERROR
            PILL_UPDATE_ERROR = True
