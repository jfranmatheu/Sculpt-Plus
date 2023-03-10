

def install():
    '''
    os.system("pip3 install -r requirements.txt")
    os.system("pip3 install -r requirements-dev.txt")
    os.system("pip3 install -r requirements-test.txt")
    '''
    try:
        import PIL

        if not hasattr(PIL, '__version__') or float(PIL.__version__[:-2]) < 9.4:
            print("Pillow version is too old! Requires to install a recent version...")
            raise ImportError("Pillow version is too old!")

    except ImportError:
        import subprocess
        import sys
        import os

        # path to python.exe
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        target = os.path.join(sys.prefix, 'lib', 'site-packages')

        # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])

        # install required packages
        subprocess.call([python_exe, "-m", "pip", "install", "Pillow>=9.4.0", "-t", target])
