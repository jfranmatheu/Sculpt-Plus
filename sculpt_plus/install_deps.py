import subprocess
import sys
import os
import bpy


addons_path: str = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons')


# ----------------------------------------------------------------


class VersionError(Exception):
    pass


# ----------------------------------------------------------------


def check_brush_manager():
    from . import BM_VERSION

    module_name = 'brush_manager'

    try:
        import brush_manager
        if hasattr(brush_manager, 'tag_version') and brush_manager.tag_version != BM_VERSION:
            raise VersionError(f"Required Brush Manager version is {BM_VERSION} but found {brush_manager.tag_version}")

    except (ModuleNotFoundError, ImportError) as e:
        print(e)


# ----------------------------------------------------------------

PILL_IMPORT_ERROR = False
PILL_UPDATE_ERROR = False

def is_pil_ok() -> bool:
    global PILL_IMPORT_ERROR
    return PILL_IMPORT_ERROR


def install_pill():
    from . import PILLOW_VERSION

    # path to python.exe
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    target = os.path.join(sys.prefix, 'lib', 'site-packages')

    try:
        import PIL

        if not hasattr(PIL, '__version__') or float(PIL.__version__[:-2]) < 9.3:
            print("Pillow version is too old! Requires to install a recent version...")
            raise VersionError("Pillow version is too old!")

    except (ModuleNotFoundError, ImportError):
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


# ----------------------------------------------------------------

def install():
    check_brush_manager()
    install_pill()


    '''
    os.system("pip3 install -r requirements.txt")
    os.system("pip3 install -r requirements-dev.txt")
    os.system("pip3 install -r requirements-test.txt")
    '''
