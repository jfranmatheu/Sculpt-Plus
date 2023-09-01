''' Made by @jfranmatheu ^u^

NOTE: This Script assumes that your project structure looks like this:
project_folder/
    addon_source/
    build/ # Created by this script.
    deploy.py # THIS SCRIPT!
    README.md
'''

# ----------------------------------------------------------------
#  M O D I F Y   T H E S E  !  :D

MODULE_NAME = 'sculpt_plus' # Rename this to match your module name (addon source folder name).
BUILD_DIRNAME = 'build' # Your build/output directory name.

# V = Addon Version. (V:1, V:2, V:3)
# B = Blender Version. (B:1, B:2, B:3)
# MODULE_NAME:u (upper-case). MODULE_NAME:l (lower-case). MODULE_NAME:t (title-like).
VERSION_FORMAT = '{MODULE_NAME:t}_v{V:1}.{V:2}.{V:3}-b{B:1}.{B:2}.x'

# Flags.
USE_MINIFIER = False
USE_PY_PACKER = False

# Additional (optional) file or directory patterns that should be excluded from the addon build.
IGNORE = ('*.old.py', '*.dev.py')

# ----------------------------------------------------------------


from re import search as re_search
from string import Formatter
from os.path import join
from os import walk
from pathlib import Path
from shutil import ignore_patterns, make_archive, copytree
from tempfile import TemporaryDirectory

if USE_PY_PACKER:
    from os import system

if USE_MINIFIER:
    try:
        import python_minifier
    except (ImportError, ModuleNotFoundError):
        USE_MINIFIER = False
        print("WARNING! Could not find 'python_minifier' package installed! USE_MINIFIER option will be disabled.")


root = Path(__file__).parent
module_dir = root / MODULE_NAME
builds_dir = root / BUILD_DIRNAME


class VersionFormatter(Formatter):
    def format_field(self, value, format_spec):
        if isinstance(value, str):
            spec_option = format_spec[-1]
            if spec_option in {'u', 'l', 't', '1', '2', '3'}:
                format_spec = format_spec[:-1]
                if spec_option in {'1', '2', '3'}:
                    value = value[int(spec_option) - 1]
                else:
                    if spec_option == 'u':
                        value = value.upper()
                    elif spec_option == 'l':
                        value = value.lower()
                    elif spec_option == 't':
                        value = value.replace('_', ' ').title().replace(' ', '')
        return super(VersionFormatter, self).format(value, format_spec)


with TemporaryDirectory(prefix=F'{MODULE_NAME}_build_') as temp_dir:
    module_copy_dir = join(temp_dir, MODULE_NAME)
    copytree(module_dir, module_copy_dir, ignore=ignore_patterns('__pycache__', '*.pyc', '*.pyo', *IGNORE))

    if USE_MINIFIER:
        for path, subdirs, files in walk(module_copy_dir):
            for filename in files:
                filepath = Path(path, filename)
                if filepath.suffix != '.py':
                    continue
                with filepath.open('r+', encoding="utf8") as f:
                    raw_code = f.read().replace("\0", "")
                    f.seek(0)
                    min_code = python_minifier.minify(raw_code, remove_annotations=False)
                    f.write(min_code)
                    f.truncate()

    init_py = module_dir / '__init__.py'

    with init_py.open('r') as f:
        bl_info_code = re_search(r"\{(.|\n)*?\}", f.read())
        if bl_info_code is None:
            raise Exception("Could not find bl_info in __init__.py at", init_py.name)

        bl_info = eval(bl_info_code[0])
        version = str(bl_info['version'])[1:-1].replace(', ', '')
        blender = str(bl_info['blender'])[1:-1].replace(', ', '')

    fmt = VersionFormatter()
    build_name = fmt.format(VERSION_FORMAT, MODULE_NAME=MODULE_NAME, V=version, B=blender)
    build_zip_path = str(builds_dir / build_name)

    zipname = make_archive(build_zip_path, 'zip', temp_dir)

    if USE_PY_PACKER:
        system(f'copy /B "{str(init_py)}" + "{zipname}" "{str(build_zip_path)}.py"')
