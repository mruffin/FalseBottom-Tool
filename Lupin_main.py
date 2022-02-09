import os
import re
import tkinter as tk
from tkinter import filedialog
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess



manifest_location = ''
apk_name = ''


def gen_decompilation():
    global manifest_location, apk_name

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    name_search = re.search('[^/]*(?=[.][a-zA-Z]+$)', file_path)

    name = name_search.group()

    apk_name = name

    cwd = os.getcwd() + '\\' + 'Decompiled_Apps\\' + name

    manifest_location = cwd

    apkt_cmd = 'cmd /c "apktool d -o ' + cwd + ' ' + file_path + '"'

    os.system(apkt_cmd)

def get_package_name():
    global manifest_location

    root = ET.parse(manifest_location + "\AndroidManifest.xml").getroot()

    packageName = root.attrib['package']

    return packageName


def is_backup_allowed():
    global manifest_location

    root = ET.parse(manifest_location + "\AndroidManifest.xml").getroot()

    application = root.findall("application")

    try:
        backup_value = application[0].attrib['{http://schemas.android.com/apk/res/android}allowBackup']
    except:
        return True

    if backup_value == 'false':
        return False
    elif backup_value == 'true':
        return True


def is_app_installed(package_name):

    batcmd = "adb shell pm list packages"

    result = subprocess.check_output(batcmd, shell=True).decode("utf-8")

    if package_name in result:
        return True
    else:
        return False

def create_backup(package_name):
    global apk_name
    cwd = os.getcwd() + '\\' + 'Backups\\'
    backup_string = "adb backup -f " + cwd + apk_name + '.ab -noapk ' + package_name

    path_to_zip_file = cwd + apk_name + '.tar'

    path_to_backup = cwd + apk_name + '.ab'

    decompress_string = "java -jar abe.jar unpack " + path_to_backup + ' ' + path_to_zip_file

    unzip_string = "7z x " + path_to_zip_file + " -aoa -o" + cwd + apk_name

    if is_backup_allowed():
        subprocess.call(backup_string, shell=True)
        subprocess.call(decompress_string, shell=True)
        subprocess.call(unzip_string, shell=True)

def recover_artifacts(package_name):
    global apk_name
    dest_files = os.getcwd() + '\\' + 'Artifacts\\' + apk_name + '\\files'
    if package_name == 'ws.clockthevault':
        src_files = os.getcwd() + '\\' + 'Backups\\' + apk_name + '\\' + 'apps\\ws.clockthevault\\f\\lockerVault'
        shutil.copytree(src_files, dest_files)
        src_preferences = os.getcwd() + '\\' + 'Backups\\' + apk_name + '\\' + 'apps\\ws.clockthevault\\sp'
        dest_preferences = os.getcwd() + '\\' + 'Artifacts\\' + apk_name + '\\preferences'
        shutil.copytree(src_preferences, dest_preferences)
    elif package_name == 'com.theronrogers.vaultyfree':
        Path(dest_files).mkdir(parents=True, exist_ok=True)
        pull_string = 'adb pull sdcard/Documents/Vaulty ' + dest_files
        subprocess.call(pull_string, shell=True)



gen_decompilation()

package_name = get_package_name()

r = is_app_installed(package_name)

if r == True:
    create_backup(package_name)
    recover_artifacts(package_name)

