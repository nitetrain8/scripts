import threading
import queue
import time
import os
import requests
from .update_events import PGS_MPD_API_LOGIN, MPD_WRITE_COMPLETE, MPD_OUT_PUT, \
                            MPD_OUT_GET, MPD_MAIN_RUNNING, MPD_IN_PUT, MPD_IN_GET, MPD_ALL_COMPLETE

__all__ = ['download_issues_pdf_multithread']


class _InternalError(Exception):
    pass


def _download_worker(copy, in_q, out_q, path, update, n):
    update(PGS_MPD_API_LOGIN)
    api = copy()
    api.login()
    iss = None
    while True:
        if iss is None:
            iss = in_q.get(True)
        update(MPD_IN_GET, iss)
        if iss is None:
            print("\rEmpty Queue, exiting download worker #%d"%n)
            return
        try:
            pdf = api.download_issue_pdf(iss.id, timeout=10)
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (502, 504):  # bad gateway
                print("\rThread #%d Got bad gateway error for issue #%d: retrying"%(n, iss.id))
                continue
            else:
                raise
        fn = "%s/%d.pdf" % (path, iss.id)
        out_q.put((fn, pdf, iss))
        update(MPD_OUT_PUT, (fn, iss))
        in_q.task_done()
        iss = None


def _write_queue_to_disk(out_q, update, filenames, max_writes=None):
    """ Drain current output queue, writing all 
    files to disk.
    :param out_q: output queue, tuple of (filename, raw_bytes)
    :type out_q: (str, bytes)
    """
    written = 0
    while True:
        try:
            fn, pdf, iss = out_q.get(False)
            update(MPD_OUT_GET, fn)
        except queue.Empty:
            break
        else:
            with open(fn, 'wb') as f:
                f.write(pdf)
            filenames.append((fn, iss))
            update(MPD_WRITE_COMPLETE, fn)
        written += 1
        if max_writes and written >= max_writes:
            break


def _make_threads(nthreads, api, in_q, out_q, path, update):
    """ Helper for thread creation """
    threads = set()
    for i in range(nthreads):
        thread_args = (api.copy, in_q, out_q, path, update, i)
        t = threading.Thread(None, _download_worker, args=thread_args, daemon=True)
        t.start()
        threads.add(t)
    return threads


class DummyState():
    def __init__(self, *args):
        pass

    @staticmethod
    def update(state, arg):
        
        if state == MPD_IN_PUT:
            pass  # no default message
        elif state == MPD_IN_GET:
            pass  # no default message
        elif state == MPD_OUT_PUT:
            pass  # no default message
        elif state == MPD_OUT_GET:
            pass  # no default message
        elif state == MPD_WRITE_COMPLETE:
            msg = "Wrote file to disk: %s" % arg
        elif state == MPD_MAIN_RUNNING:
            msg = "Downloading files  (%d/%d)"
            msg %= arg  # (done, arg)
        elif state == MPD_ALL_COMPLETE:
            print("\nDone")
            return
        else:
            raise _InternalError("Invalid state provided to callback")

        msg = "\r%s                        " % msg
        print(msg, end="")


def download_issues_pdf_multithread(api, issues, path=".", max_threads=8, state=None):
    """
    Download issues asyncronously using multithreading. 
    :param api: IssuetrackerAPI instance
    :param issues: iterable of Issue objects
    :param path: directory to download issues to
    :param max_threads: max number of threads to use
    """
    os.makedirs(path, exist_ok=True)
    in_q = queue.Queue()
    out_q = queue.Queue()
    filenames = []
    nthreads = min(max_threads, 20)  # sanity

    if state is None:
        state = DummyState()
    
    threads = _make_threads(nthreads, api, in_q, out_q, path, state.update)

    nissues = 0
    for i in issues:
        in_q.put(i)
        state.update(MPD_IN_PUT, i)
        nissues += 1

    for i in range(nthreads):
        state.update(MPD_IN_PUT, None)
        in_q.put(None)
        
    while threads:    
        time.sleep(2)
        completed = max(nissues - in_q.qsize(), 0)
        state.update(MPD_MAIN_RUNNING, (completed, nissues))
    
        for t in list(threads):
            if not t.is_alive():
                threads.remove(t)
        
        _write_queue_to_disk(out_q, state.update, filenames, 10)
    
    _write_queue_to_disk(out_q, state.update, filenames, None)
    state.update(MPD_ALL_COMPLETE, "Downloaded %d files %d remaining" % (out_q.qsize(), in_q.qsize()))
    return filenames
        
