import sys
import os
os.chdir(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(".\scripts"))
#print(sys.path)
import os
#print(os.path.abspath("."))
import install
import copyprog
import os
try:
    DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
    INSTALL_RIO_DIR = os.path.join(DESKTOP, "1 Install RIO")
    EXTRACT_DIR = os.path.join(DESKTOP, "Hello Installer.tmp")
    STATE_FILE = os.path.join(EXTRACT_DIR, "InstallState.txt")
    def extract():
        dn = os.path.dirname  # brevity
        print("Extracting installer files ... ")
        hd_src = dn(dn(os.path.abspath(__file__)))
        hd_dst = os.path.join(EXTRACT_DIR, "auto_hd_install")
        # py_src = os.path.abspath(os.path.dirname(sys.executable))
        # end debug!
        copyprog.copytreeprog(hd_src, hd_dst)


    state, data = install.check_state()
    if state == install.STATE_EXTRACT:
        print("GOT STATE_EXTRACT, EXTRACTING TO DESKTOP")
        py, bat = install.extract_to_desktop()
        #extract()
        bat = "C:\\users\\natha\\desktop\\Hello Installer.tmp\\auto_hd_install\\install.bat"
        py = ""
        install.set_state(install.STATE_INIT, (py, bat))
        #print(bat)
        install.restart_instance(py, bat)  # exits process
    elif state == install.STATE_INIT:
        py, bat = data
        print("GOT STATE_INIT, TEEHEE")
        install.schedule_for_startup(py, bat)
        print("Should have scheduled or whatever")
        install.set_state(install.STATE_INSTALL_PBS, None)
        install.reboot()
        # print(sys.executable)
        raise Exception
    elif state == install.STATE_INSTALL_PBS:
        print("OMFG IT WORKED")
        input("OMG OMG OMG OMG OMG")
    else:
        print("GOT STATE %d" % state)

    import os
    os.remove("C:\\users\\natha\\desktop\\Hello Installer.tmp\\InstallState.txt")
except Exception:
    import traceback
    traceback.print_exc()
    input("Exception...")
finally:
    pass
    #input("exiting...")