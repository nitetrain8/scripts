


import os
import datetime
import shutil

def get_ArchiveDate():
    mytime = datetime.date.today()
    date_str = mytime.strftime("%y%m%d")
    return date_str

dbg_tmp = "C:\\Users\\PBS Biotech\\Documents\\Personal"
dbg_lv_data = dbg_tmp + "\\LabVIEW Data"
dbg_archive = dbg_tmp + "\\archive"
dbg_config = dbg_tmp + "\\config"
dbg_cyth_path = dbg_tmp + "\\_CythClients"
dbg_archive_new = '\\'.join([dbg_archive, get_ArchiveDate()]) 



PBS_3L_labview = "C:\\Documents and Settings\\Chris\\My Documents\\LabVIEW Data"
PBS_3L_archive = "C:\\Documents and Settings\\Chris\\Desktop\\Archived Folders"
PBS_3L_cyth = "C:\\Program Files\\Cyth Systems\\_CythClients"
PBS_3L_archive_new = '\\'.join([PBS_3L_archive, get_ArchiveDate()])

if os.path.exists(dbg_archive_new):
    i = 2
    tmp = dbg_archive_new + " " + str(i)
    while os.path.exists(tmp):
        i += 1
        tmp = "{} {}".format(dbg_archive_new, str(i))
    dbg_archive_new = tmp
    
    
# shutil.rmtree(dbg_archive_new)
shutil.copytree(dbg_lv_data, dbg_archive_new + "\\LabVIEW Data")
shutil.copytree(dbg_config, dbg_archive_new + "\\config")
