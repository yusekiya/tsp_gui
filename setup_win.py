import sys
from cx_Freeze import setup, Executable, hooks

base = None
if sys.platform == "win32":
    base = "Win32GUI"

    build_exe_options = {'packages': ['matplotlib.backends.backend_qt4agg',
                                      'scipy']}

def load_scipy_patched(finder, module):
    """the scipy module loads items within itself in a way that causes
        problems without the entire package and a number of other subpackages
        being present."""
    finder.IncludePackage("scipy._lib")  # Changed include from scipy.lib to scipy._lib
    finder.IncludePackage("scipy.misc")

hooks.load_scipy = load_scipy_patched

setup(name='TSPSolver',
      version=1.1,
      options={'build_exe': build_exe_options},
      executables=[Executable('tsp_gui.py', base=base)])
