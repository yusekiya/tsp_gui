import sys
from cx_Freeze import setup, Executable, hooks

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {'excludes': ['tkinter', 'multiprocessing', 'OpenSSL',
                                  'PIL', 'IPython', 'ConfigParser', 'configparser'
                                  'SocketServer', 'asyncio', 'Queue',
                                  'cffi', 'curses', 'html']}

setup(name='TSPSolver',
      version='1.1',
      options={'build_exe': build_exe_options},
      executables=[Executable('tsp_gui.py', base=base)])
