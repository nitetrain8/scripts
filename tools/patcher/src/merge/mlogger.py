import os

class Logger():
    def __init__(self, verbose, *files):
        self.files = files
        self.verbose = verbose
        self.fps = fps = []
        for file in self.files:
            print(file)
            try:
                fp = self._open(file)
            except Exception:
                self._close_all()
                raise
            else:
                fps.append(fp)

    def _open(self, file):
        dn = os.path.dirname(file)
        if not os.path.exists(dn):
            os.makedirs(dn, exist_ok=True)  # ew race conditions
        return open(file, 'w')

    def _close_all(self):
        bad = []
        while self.fps:
            fp = self.fps.pop()
            try:
                fp.close()
            except Exception:
                bad.append(fp)
        self.fps = bad

    def log(self, *a, **k):
        for fp in self.fps:
            k['file'] = fp
            print(*a, **k)
        if self.verbose:
            k['file'] = None
            print(*a, **k)