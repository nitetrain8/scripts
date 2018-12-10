import os
import shutil
def _recurse_files(src, dst, files):
    for f in os.listdir(src):
        sfp = os.path.join(src, f)
        dfp = os.path.join(dst, f)
        if os.path.isdir(sfp):
            files.append((sfp, dfp, True, 0))
            _recurse_files(sfp, dfp, files)
        else:  # file
            files.append((sfp, dfp, False, os.stat(sfp).st_size))


def _progress_cb(state, src, dst, files,*args):
    if state == "SCANNING":
        print("Scanning for files in \"%s\"..."%src)
    elif state == "BEGINNING_COPY":
        print("Found %d files ..." % len(files))
    elif state == "COPYING":
        c,t = args
        pc = "%.1f%%"%(100*c/t)
        fn = os.path.basename(src)
        mbc = c / 1024 / 1024
        mbt = t / 1024 / 1024
        if len(fn) > 15:
            fn = "%.12s..."%fn
        print("\r%s Complete (%d/%d MB), copying \"%s\" ..."%(pc, mbc, mbt, fn), " "*15, end="")
    elif state == "DONE":
        print("\nCopy Finished!")

def copytreeprog(src, dst, cb=_progress_cb):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    files = []
    cb("SCANNING", src, dst, files)
    _recurse_files(src, dst, files)
    cb("BEGINNING_COPY", src, dst, files)
    os.makedirs(dst, exist_ok=True)
    bytes_total = sum(t[3] for t in files)
    bytes_copied = 0
    for s,d,isdir, sz in files:
        cb("COPYING", s, d, files, bytes_copied, bytes_total)
        bytes_copied += sz
        if isdir:
            os.makedirs(d, exist_ok=True)
        else:
            shutil.copy2(s,d)
    cb("DONE", src, dst, files)