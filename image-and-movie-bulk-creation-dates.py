import argparse
import os
import time
import datetime
import calendar
import piexif
from ctypes import windll, wintypes, byref


#Photo:
# Runs over entire directory hunting for folders starting with YYYY-MM-DD format
# For all image files inside such a folder, the creation time and image taken time is 
# edited accordingly
#Movies
#Not yet implemented.

def handleFilesInFolder(root_folder):
    filelist = []
    print('\n\n\n---------------------------------- Image Creation Date Update -----------------------------')
    print('\nRoot folder: {root_folder}\n\nHandling subfolders:'.format(root_folder=root_folder))
    image_count = 0
    skipped_count = 0
    failing_folders = []
    for root, dirs, files in os.walk(root_folder):
        for folder in dirs:
            print(folder) 
        for file in files:
            #print all the file names
            #append the file name to the list
            if file.endswith(".jpg") or file.endswith(".tif") or file.endswith(".tiff"):
                full_path = os.path.join(root,file)
                filelist.append(full_path)
                folder_date = getDateTimeFolderPath(root)
                epoch = getEpocFromDateTime(folder_date)
                if epoch is None:
                    if root not in root_folder:
                        skipped_count = skipped_count + 1
                        if root not in failing_folders:
                            failing_folders.append(root)
                    continue
                setCreationTime(full_path, epoch)
                #setImageDateTakenAttribute(full_path, folder_date)
                setLastModifiedTime(full_path, epoch)
                image_count = image_count + 1
 

    print('\nDone!\n{count} images updated.\n{skipped_count} images skipped.\n'.
        format(count=image_count, skipped_count=skipped_count))    
    if len(failing_folders) > 0:
        print('Skipped folders:')
    for folder in failing_folders:
        print(folder) 
    print('')
    os.system("pause")

def setLastModifiedTime(filepath, epochtime):
    now_epoch = datetime.datetime.now().timestamp()
    os.utime(filepath, (now_epoch, epochtime))

## From https://stackoverflow.com/a/56805533/3407324
def setCreationTime(filepath, epochtime):
    # Convert Unix timestamp to Windows FileTime using some magic numbers
    # See documentation: https://support.microsoft.com/en-us/help/167296
    timestamp = int((epochtime * 10000000) + 116444736000000000)
    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)
    # Call Win32 API to modify the file creation date
    handle = windll.kernel32.CreateFileW(filepath, 256, 0, None, 3, 128, None)
    windll.kernel32.SetFileTime(handle, byref(ctime), None, None) #(handle, ctime, atime, mtime)
    windll.kernel32.CloseHandle(handle)


def setImageDateTakenAttribute(filename, date_time):
    exif_dict = piexif.load(filename)
    exif_dict['Exif'] = { 
        piexif.ExifIFD.DateTimeOriginal: datetime.datetime(*date_time[:6]).strftime("%Y:%m:%d %H:%M:%S") 
    } 
    exif_bytes = piexif.dump(exif_dict)
    try:
        piexif.insert(exif_bytes, filename)
        return 1
    except:
        return 0


def getDateTimeFolderPath(folder_path):
    folder_name = os.path.basename(folder_path)
    first_info = str.split(folder_name)[0]
    date_info = str.split(first_info,'-')
    if len(date_info) > 2:
        year = date_info[0]
        if 'x' in year.lower():
            return None

        month = date_info[1].lower().replace('xx','01').replace('x','1') #.replace('hh','09').replace('vv','03')
        if not month.isnumeric():
            return None

        date = date_info[2].lower().replace('xx','01').replace('x','1')
        if not date.isnumeric():
            return None
        # Choosing 12 AM on the given date to avoid date shifts resulting from daylight savings issues 
        dateString = '{date}:{month}:{year} 12:00'.format(date=date, month=month, year=year)
        return time.strptime(dateString, "%d:%m:%Y %H:%M");
    else:
        return None


def getEpocFromDateTime(datetime):
    if datetime is None:
        return None
    timeshift = getUtcTimeDiff()
    return calendar.timegm(datetime) + timeshift 


def getUtcTimeDiff():
    utcTime = datetime.datetime.utcnow().timestamp()
    localTime = datetime.datetime.now().timestamp()
    timeDiff = utcTime - localTime  
    return timeDiff



if __name__  == '__main__':
    parser = argparse.ArgumentParser(description='Root path')
    parser.add_argument('--src_root_path', help='Root path of the digitalized files:', default='ASK')

    args = parser.parse_args()

    src_root_path = args.src_root_path
    if src_root_path == 'ASK':
        src_root_path = input("Enter the root path of the digitalized files: ")
    if not src_root_path:
        print('Invalid path!')
    else:
        handleFilesInFolder(src_root_path)
