import glob
import python_minifier
from fnmatch import fnmatch
from os.path import join, dirname, exists, isdir
from os import walk, unlink
from pathlib import PurePath
from shutil import ignore_patterns, make_archive, copytree, rmtree, copyfile

module_name='sculpt_plus' # Rename this to match your module name (addon src folder name).

root=dirname(__file__)
module_dir=join(root, module_name)
build_dir=join(root, 'build')

# Make a copy of the src folder to build dir.
_temp_dir = join(build_dir, 'temp')
if exists(_temp_dir) and isdir(_temp_dir):
    rmtree(_temp_dir, ignore_errors=True)
module_copy_dir = join(_temp_dir, module_name) # So that we have a folder inside the .zip with all addon files in there. 'temp' will be replaced by the .zip...
copytree(module_dir, module_copy_dir, ignore=ignore_patterns('__pycache__', '*.pyc', '*.pyo', '*.old.py', '*.dev.py'))

# Minify .py files to decrease space.
minify_re=join(module_copy_dir, '/**/*.py') # r'.\sculpt_plus\*.py'
code=''
# for filepath in  glob.iglob(minify_re, recursive=True):
for path, subdirs, files in walk(module_copy_dir):
    for filename in files:
        filepath = PurePath(path, filename)
        if filepath.suffix != '.py':
            continue
        with open(filepath, 'r', encoding="utf8") as f:
            raw_code = f.read().replace("\0", "")
            if not raw_code:
                continue
            code = python_minifier.minify(raw_code, remove_annotations=False)
        with open(filepath, 'w', encoding="utf8") as f:
            f.write(code)

# Compress folder to .zip
version='0.0.1'#str(bl_info['version'])[1:-1].replace(', ', '.')
with open(join(module_copy_dir, '__init__.py'), 'r') as f:
    for line in f.readlines():
        if line.startswith('bl_info'):
            bl_info = eval(line[8:])
            version = str(bl_info['version'])[1:-1].replace(', ', '.')
            blender = str(bl_info['blender'])[1:-1].replace(', ', '.')
build_name=f'{module_name}_v{version}-b{blender}'
zip_path=join(build_dir, build_name)
make_archive(zip_path, 'zip', _temp_dir)

# sculpt plus installer...
sculpt_plus_installer_path = join(root, 'sculpt_plus_installer')
sculpt_plus_installer_zipfile = join(sculpt_plus_installer_path, 'sculpt_plus.zip')
copyfile(zip_path + '.zip', sculpt_plus_installer_zipfile)
make_archive(join(root, 'sculpt_plus_installer'), 'zip', sculpt_plus_installer_path)

# Clenup.
rmtree(_temp_dir, ignore_errors=True)
