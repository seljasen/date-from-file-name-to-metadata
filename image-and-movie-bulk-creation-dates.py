import argparse
import site
import os
import tempfile
import shutil
import zipfile
import logging
import datetime
from win32_setctime import setctime


import time
import datetime
import calendar
from ctypes import windll, wintypes, byref
import win32.lib.win32con as win32con
import win32file 
import pywintypes
import piexif


#Photo:
# 1. Look for a date in the given folder name.
    # 2. If date is given, look for subfolder with date in name. if found, run self on this folder first.
    # 3. For all files in folder Set creation date, and probably modification date if desired 
    #       like the date from the folder name.
# 4. If no date is found in root folder name, run self on all subfolders, 
#       and do nothing with the files in current folder




def handleFilesInFolder(root_folder):
    filelist = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            #print all the file names
            #append the file name to the list
            if file.endswith(".jpg") or file.endswith(".tif") or file.endswith(".tiff"):
                full_path = os.path.join(root,file)
                filelist.append(full_path)
                folder_date = getDateTimeFolderPath(root)
                epoch = getEpocFromDateTime(folder_date)
                setctime(full_path, epoch)
                setImageDateTakenAttribute(full_path, folder_date)
                print('Files:')    
#        for name in files:
#            print(name)
#        print('Root:')  
#        print(root)
#        print('Directories:')    
#        for directory in dirs:
#            print(directory)  
#        print('Filelist')
#        for file in filelist:
#            print(file)  

def setImageDateTakenAttribute(filename, date_time):
    exif_dict = piexif.load(filename)
    exif_dict['Exif'] = { piexif.ExifIFD.DateTimeOriginal: datetime.datetime(*date_time[:6]).strftime("%Y:%m:%d %H:%M:%S") } #"%Y:%m:%d %H:%M:%S"
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filename)


def getDateTimeFolderPath(folder_path):
    folder_name = os.path.basename(folder_path)
    first_info = str.split(folder_name)[0]
    date_info = str.split(first_info,'-')
    print(first_info)
    if len(date_info) > 2:
        year = int(date_info[0])
        month = int(date_info[1])
        date = int(date_info[2])
        dateString = '{date}:{month}:{year}'.format(date=date, month=month, year=year)
        #timestring = '{date}:{month}:{year} 00:00:00'.format(date=date, month=month, year=year)
        return time.strptime(dateString, "%d:%m:%Y");
    else:
        return time.gmtime(0)

def getEpocFromFolderPath(folder_path):
    timeshift = getUtcTimeDiff()
    datetime = getDateTimeFolderPath(folder_path)
    return calendar.timegm(datetime) + timeshift          

def getEpocFromDateTime(datetime):
    timeshift = getUtcTimeDiff()
    return calendar.timegm(datetime) + timeshift        

def getUtcTimeDiff():
    utcTime = datetime.datetime.utcnow().timestamp()
    localTime = datetime.datetime.now().timestamp()
    return utcTime - localTime   

def main(
    src_root_path,
    dest_root_path,
    has_aux_well,
):
    print('Source folder:')
    print(src_root_path)
    logger = logging.getLogger('creation_date_edit')
    update_xml_files( 
        src_root_path,
        dest_root_path,
        has_aux_well,
    )


    os.system("pause")


if __name__  == '__main__':
    parser = argparse.ArgumentParser(description='Root path')
    parser.add_argument('--src_root_path', help='Root path of the digitalized files:', default='ASK')

    args = parser.parse_args()

    src_root_path = args.src_root_path
    if src_root_path == 'ASK':
        src_root_path = input("Enter the root path of the digitalized files: ")

    handleFilesInFolder(src_root_path)
