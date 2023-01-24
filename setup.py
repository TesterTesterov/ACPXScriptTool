import sys
import cx_Freeze

base = None

if (sys.platform == 'win32'):
    base = "Win32GUI"


executables = [cx_Freeze.Executable("main.py",
                                    shortcut_name="ACPXScriptTool",
                                    shortcut_dir="ACPXScriptTool",
                                    #base="Win32GUI"
                                    )]

cx_Freeze.setup(
        name="ACPXScriptTool",
        version="1.0",
        description="Dual languaged (rus+eng) tool for (dis)assembling scripts of ACPX.\n"
                    "Двуязычное средство (рус+англ) для (диз)ассемблирования скриптов ACPX.",
        options={"build_exe": {"packages": []}},
        executables=executables
)