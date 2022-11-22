

def install():
    '''
    os.system("pip3 install -r requirements.txt")
    os.system("pip3 install -r requirements-dev.txt")
    os.system("pip3 install -r requirements-test.txt")
    '''
    try:
        import PIL
    except ImportError:
        import subprocess
        import sys
        import os
        
        # path to python.exe
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        
        # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        
        # install required packages
        subprocess.call([python_exe, "-m", "pip", "install", "Pillow"])
