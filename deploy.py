import glob
import python_minifier
from os.path import join, dirname
from shutil import ignore_patterns, make_archive, copytree, rmtree

module_name='sculpt_plus' # Rename this to match your module name (addon src folder name).

root=dirname(__file__)
module_dir=join(root, module_name)
build_dir=join(root, 'build')

# Make a copy of the src folder to build dir.
_temp_dir = join(build_dir, 'temp')
module_copy_dir = join(_temp_dir, module_name) # So that we have a folder inside the .zip with all addon files in there. 'temp' will be replaced by the .zip...
copytree(module_dir, module_copy_dir, ignore=ignore_patterns('__pycache__', '*.pyc', '*.pyo', '*.old.py', '*.dev.py'))

# Minify .py files to decrease space.
minify_re=join(module_copy_dir, '*.py') # r'.\sculpt_plus\*.py'
code=''
for filepath in glob.iglob(minify_re, recursive=True):
    with open(filepath, 'r') as f:
        code = python_minifier.minify(f.read(), remove_annotations=False)
    with open(filepath, 'w') as f:
        f.write(code)

# Compress folder to .zip
version='0.0.1'#str(bl_info['version'])[1:-1].replace(', ', '.')
with open(join(module_copy_dir, '__init__.py'), 'r') as f:
    for line in f.readlines():
        if line.startswith('bl_info'):
            bl_info = eval(line[8:])
            version = str(bl_info['version'])[1:-1].replace(', ', '.')
build_name=module_name.replace('_', ' ').replace('-', ' ').capitalize().replace(' ', '')
zip_path=join(build_dir, build_name+'_'+version)
make_archive(zip_path, 'zip', _temp_dir)

# Clenup.
rmtree(_temp_dir, ignore_errors=True)
