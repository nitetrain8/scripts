# states / events for update callback
class _increment():
    def __init__(self, value=0):
        self.value = value
    def __call__(self):
        v = self.value
        self.value += 1
        return v
_increment = _increment()

MPD_IN_PUT = _increment()
MPD_IN_GET = _increment()
MPD_OUT_PUT = _increment()
MPD_OUT_GET = _increment()
MPD_WRITE_COMPLETE = _increment()
MPD_MAIN_RUNNING = _increment()
MPD_ALL_COMPLETE = _increment()
PGS_BEGIN_PROCESS_PDFS = _increment()
PGS_PDFTK_INFO_BEGIN = _increment()
PGS_MPD_API_LOGIN = _increment()
PGS_MPD_API_LOGGED_IN = _increment()
PGS_PDFTK_INFO_DONE = _increment()
PGS_IPG_FLAG_WAITING = _increment()
PGS_PREPARE_POSTSCRIPT = _increment()
PGS_BEGIN_BIND_PDF = _increment()
PGS_PDFTK_THREAD_DEATH = _increment()
PGS_PROCESS_PDFS_DONE = _increment()
PDFTK_INFO_OOPS = _increment()
PGS_DONE = _increment()
PGS_UPDATE_WORD_INDEX = _increment()
PGS_CREATE_WORD_DOC = _increment()
PGS_BEGIN_PDF_INDEX = _increment()
PDFTK_GETTING_INFO = _increment()
PGS_LOGGING_IN = _increment()

state2name = [0] * (_increment.value + 1)
_k = _v = None
for _k, _v in globals().items():
    if _k.upper() == _k and \
    isinstance(_v, int) and \
    _k[:3] in {"PDF", "PGS", "MPD"}:
        state2name[_v] = _k
del _k, _v, _increment