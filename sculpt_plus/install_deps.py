import subprocess
import sys
import os


PILL_IMPORT_ERROR = False
PILL_UPDATE_ERROR = False

def is_pil_ok() -> bool:
    global PILL_IMPORT_ERROR
    return PILL_IMPORT_ERROR


class VersionError(Exception):
    pass


def install():
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
            subprocess.call([python_exe, "-m", "pip", "install", "Pillow>=9.3.0", "-t", target])
        except PermissionError as e:
            print(e)
            global PILL_IMPORT_ERROR
            PILL_IMPORT_ERROR = True

    except VersionError:
        try:
            subprocess.call([python_exe, "-m", "pip", "install", '--ignore-installed', "Pillow>=9.3.0", "-t", target])
        except PermissionError as e:
            print(e)
            global PILL_UPDATE_ERROR
            PILL_UPDATE_ERROR = True
