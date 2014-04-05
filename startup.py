from IPython.lib.editorhooks import get_ipython, subprocess, TryNext


def set_npp_hook():
    template = "\"C:/Program Files/Notepad++/notepad++.exe\" -nosession -n{line} \"{filename}\""

    def call_editor(self, filename, line=0):
        if line is None:
            line = 0

        cmd = template.format(filename=filename, line=line)
        print(">", cmd)
        proc = subprocess.Popen(cmd, shell=True)
        if proc.wait() != 0:
            raise TryNext()

    get_ipython().set_hook('editor', call_editor)
    get_ipython().editor = template

set_npp_hook()


def set_pycharm_hook():
    pycharm = "C:/Program Files/JetBrains/PyCharm/bin/pycharm.exe"
    template = "\"%s\" {filename} --line {line}" % pycharm

    def call_editor(self, filename, line=0):
        if line is None:
            line = 0

        cmd = template.format(filename=filename, line=line)
        print(">", cmd)
        proc = subprocess.Popen(cmd, shell=True)
        input("Press Enter when finished editing...")

    get_ipython().set_hook('editor', call_editor)
    get_ipython().editor = template


