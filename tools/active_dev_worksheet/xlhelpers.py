
import win32com
import win32com.client
import contextlib

@contextlib.contextmanager
def screen_lock(xl, preserve=True):
    updating = xl.ScreenUpdating
    xl.ScreenUpdating = False
    xl.DisplayAlerts = False
    try:
        yield
    finally:
        if not preserve or updating == True:
            xl.ScreenUpdating = True
        xl.DisplayAlerts = True

class _XLC:
    def __init__(self):
        # based on win32com.client.constants.__getattr__
        for d in win32com.client.constants.__dicts__:
            for k in d:
                if k.startswith("xl"):
                    setattr(self, k, d[k])

    def __getattr__(self, attr):
        val = getattr(win32com.client.constants, attr)
        setattr(self, attr, val)
        return val

xlc = _XLC()


def open_excel(background=False):
    if background:
        xl = background_excel()
    else:
        xl = win32com.client.gencache.EnsureDispatch("Excel.Application")
    xl.Visible = True
    return xl

def _check_constants():
    """Determines whether win32com.client.constants class
    has a populated list of excel constants by testing for
    presence of known values. 

    Returns:
        bool: True if the constants are populated, otherwise false.
    """    
    try:
        xlc.xlNormal
        xlc.xlSolid
        xlc.xlAutomatic
        xlc.xlNone
    except AttributeError:
        return False
    return True


def _get_xl_app():
    return win32com.client.DispatchEx("Excel.Application")


def background_excel():

    # It is possible (seems to happen after system updates) for
    # the win32com.client.constants dictionary to fail to populate,
    # due to some cache (perhaps the AppData/local/Temp folder?)
    # being cleared. 

    # Because the DispatchEx method is fully dynamic,
    # the constants dict isn't populated and all constant values must be
    # known from other sources. By default, the xlc constants
    # object uses win32com.client.constants, populated when
    # gencache.EnsureDispatch is used. 

    # test a few of the constants here - if they work, go ahead. Otherwise,
    # use the gencache method to try to force win32com to build the dicts.
    # This method has drawbacks so issue a warning to user. 
    
    # Test Protocol:
    # 1. Delete ~/AppData/Local/Temp/gen_py/<python version>
    # 2. Comment-out any code saving the workbook to sharepoint (or other)
    # 3. Restart the notebook & run all cells
    # 4. Verify it all works
    # 5. Close excel & verify no lingering excel processes
    # 
    # Run with and without a separate workbook opened by user 
    
    # Tested 6/3/2020 - seems to work just fine
    
    xl = _get_xl_app()
    if not _check_constants():
        print("Warning: Excel constants dictionary not initialized. Attempting workaround...")
        
        # Attempt to populate the dicts using gencache
        xl2 = win32com.client.gencache.EnsureDispatch("Excel.Application")
        
        # We don't want the Excel process to linger, but we also want to
        # try to avoid nuking a user's excel process if they're using it already.
        if xl2.Workbooks.Count == 0:
            xl2.Quit()
        
        del xl2
        gc.collect()
        
        # try again, bail if fail
        if not _check_constants():
            raise RuntimeError("Failed to load win32com.client.constants dictionary") 
        
        print("Workaround successful. Resuming activity...")
        
    return xl