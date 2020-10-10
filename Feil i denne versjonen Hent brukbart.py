import argparse
import site
import os, time
import tempfile
import shutil
import zipfile
import logging
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
    print(root_folder)
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            #print all the file names
            #append the file name to the list
            if file.endswith(".jpg") or file.endswith(".tif") or file.endswith(".tiff"):
                fullPath = os.path.join(root,file)
                filelist.append(fullPath)
                dateOfCapture = getEpocFromFolderPath(fullPath)
                #ERror handle the return argument dateOfCapture
                setCreationTime(fullPath, dateOfCapture.epoch)
                setImageDateTakenAttribute(fullPath, dateOfCapture.datetime)
 
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


def getEpocFromFolderPath(folder_path):
    folder_name = os.path.basename(folder_path)
    first_info = str.split(folder_name)[0]
    date_info = str.split(first_info,'-')
    print(first_info)

    if len(date_info) > 2:        
        year = date_info[0]
        month = date_info[1]
        date = date_info[2]
        dateString = '{date}/{month}/{year}'.format(date=date, month=month, year=year)
        print(dateString)
        retVal.timestring = '{date}:{month}:{year} 00:00:00'.format(date=date, month=month, year=year)
        timeshift = getUtcTimeDiff()
        retVal.datetime = time.strptime(dateString, "%d/%m/%Y");
        retVal.epoch = calendar.timegm(retVal.dateTime) + timeshift  
        print(retVal.timestamp)
        return retVal
    else:
        return None



    

def getUtcTimeDiff():
    utcTime = datetime.datetime.utcnow().timestamp()
    localTime = datetime.datetime.now().timestamp()
    return utcTime - localTime    


def setCreationTime(filepath, epochtime):
    # Convert Unix timestamp to Windows FileTime using some magic numbers
    # See documentation: https://support.microsoft.com/en-us/help/167296
    timestamp = int((epochtime * 10000000) + 116444736000000000)
    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)
    atime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)
    mtime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)
    # Call Win32 API to modify the file creation date
    handle = windll.kernel32.CreateFileW(filepath, 256, 0, None, 3, 128, None)
    windll.kernel32.SetFileTime(handle, byref(ctime), byref(atime), byref(mtime))
    windll.kernel32.CloseHandle(handle)


def setCreationTimePython3(fname, newtime):
    wintime = datetime.datetime(newtime)
    winfile = win32file.CreateFile(
        fname, win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)
    win32file.SetFileTime(winfile, wintime, wintime, wintime)
    winfile.close()

def setImageDateTakenAttribute(filename, image_datetime):
    datetime_new = image_datetime.strftime(self.EXIF_DATETIME_FORMAT).encode(self.EXIF_DATETIME_ENCODING)
    exif_dict = piexif.load(filename)
    exif_dict['Exif'] = { 
        piexif.ExifIFD.DateTimeOriginal: datetime_new 
        } #"%Y:%m:%d %H:%M:%S"
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filename)

#    exif_dict = piexif.load(filename)
#    exif_dict['Exif'] = { piexif.ExifIFD.DateTimeOriginal: timestring } #"%Y:%m:%d %H:%M:%S"
#    exif_bytes = piexif.dump(exif_dict)
#    piexif.insert(exif_bytes, filename)
#

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



#def set_image_datetime(self, image_datetime: datetime):
#    datetime_new = image_datetime.strftime(self.EXIF_DATETIME_FORMAT).encode(self.EXIF_DATETIME_ENCODING)
#    exif_ifd = {
#        piexif.ExifIFD.DateTimeOriginal: datetime_new,
#        piexif.ExifIFD.DateTimeDigitized: datetime_new
#    }
#    zeroth_ifd = {piexif.ImageIFD.DateTime: datetime_new}
#    self._update_exif_tags({IFDs.IFD_0: zeroth_ifd, IFDs.IFD_EXIF: exif_ifd})



    ##From https://stackoverflow.com/a/43047398/3407324
#def isWindows() :
#  import platform
#  return platform.system() == 'Windows' 
#
#def getFileDateTimes( filePath ):        
#    return ( os.path.getctime( filePath ), 
#             os.path.getmtime( filePath ), 
#             os.path.getatime( filePath ) )
#
#def setFileDateTimes( filePath, datetimes ):
#    try :
#        import datetime
#        import time 
#        if isWindows() :
#            import win32file, win32con
#            ctime = datetimes[0]
#            mtime = datetimes[1]
#            atime = datetimes[2]
#            # handle datetime.datetime parameters
#            if isinstance( ctime, datetime.datetime ) :
#                ctime = time.mktime( ctime.timetuple() ) 
#            if isinstance( mtime, datetime.datetime ) :
#                mtime = time.mktime( mtime.timetuple() ) 
#            if isinstance( atime, datetime.datetime ) :
#                atime = time.mktime( atime.timetuple() )             
#            # adjust for day light savings     
#            now = time.localtime()
#            ctime += 3600 * (now.tm_isdst - time.localtime(ctime).tm_isdst)
#            mtime += 3600 * (now.tm_isdst - time.localtime(mtime).tm_isdst)
#            atime += 3600 * (now.tm_isdst - time.localtime(atime).tm_isdst)            
#            # change time stamps
#            winfile = win32file.CreateFile(
#                filePath, win32con.GENERIC_WRITE,
#                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
#                None, win32con.OPEN_EXISTING,
#                win32con.FILE_ATTRIBUTE_NORMAL, None)
#            win32file.SetFileTime( winfile, ctime, atime, mtime )
#            winfile.close()
#        else : """MUST FIGURE OUT..."""
#    except : pass  
#
