#!/usr/bin/env python
import subprocess, os.path, time, ConfigParser, json
import gio, pyudev

"""
usb-dumper
Copyright (C) 2014   Tuxicoman
#Description: usb-dumper is a tool that automatically dump memory content of any USB hardwre plugged to your computer. Universal Media Storage (USB sticks, MP3 players, etc...) and MTP (Android 4.x phones, etc..) are supported.
#Source: http://codingteam.net/project/usb-dumper/browse


This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


#default config
config = {}
config["destination_folder"] = os.path.expanduser("~/usb-dumped") #Folder where files will be dumped on your disk. By default in a folder next to this script.
config["discard_folder_names"] = ["cache", "thumb"] #folder names patterns you don't want to dump
config["discard_file_names"] = [".ogg",".mp3", ".wma", ".m4a", ".obf", ".apk"] #filenames patterns you don't want to dump
config["discard_serial_devices"] = [] #Serials of devices you don't want to dump

config_file_path = os.path.expanduser('~/.config/usb-dumper/usb-dumper.conf')
config_section = "usb-dumper"


def read_config(config_file_path, config_dict):
  configparser = ConfigParser.RawConfigParser()
  configparser.read(config_file_path)
  for key, previous_value in config_dict.items():
    if configparser.has_option(config_section, key):
      new_value = configparser.get(config_section, key).decode('utf-8')
      if type(previous_value) in (list, bool):
        new_value = json.loads(new_value)
      config_dict[key] = new_value

def save_config(config_file_path, config_dict):
  configparser = ConfigParser.RawConfigParser()
  configparser.add_section(config_section)
  for key, value in config_dict.items():
    if type(value) in (list, bool) :
      value = json.dumps(value)
    configparser.set(config_section, key, value.encode('utf-8'))
    
  config_file_folder = os.path.dirname(config_file_path)
  if not os.path.exists(config_file_folder) :
    os.makedirs(config_file_folder)
  with open(config_file_path, 'w') as configfile:
    configparser.write(configfile)
  
class MTP_Device:
  """Class for MTP device like android 4.x phones, mp3 player"""
  def __init__(self, device):
    self.device_node = device.device_node
    self.name = "%s %s" % (device.attributes['manufacturer'], device.attributes['product'])
    self.serial = device.attributes['serial']
    self.busnum = int(device.attributes['busnum'])
    self.devnum = int(device.attributes['devnum'])

class UMS_Device:
  """Class for Universal Media Storage device like USB keys, Android < 4.0 phones"""
  def __init__(self, device):
    self.device_node = device.device_node
    self.name = "%s %s %s" % (device['ID_VENDOR'], device['ID_MODEL'], device['ID_FS_LABEL'])
    self.serial = device['ID_SERIAL_SHORT']
    
def pick_device(connected_device):
  """Test eligible device fo dump """
  if connected_device["SUBSYSTEM"] == "usb" and "ID_MTP_DEVICE" in connected_device.keys():
    device = MTP_Device(connected_device)
  elif connected_device["SUBSYSTEM"] == "block" and "ID_USB_DRIVER" in connected_device.keys() and connected_device["ID_USB_DRIVER"] == "usb-storage" and "ID_FS_TYPE" in connected_device.keys():
    device = UMS_Device(connected_device)
  else:
    return None
    
  if device.serial in config["discard_serial_devices"]:
    print "discarded %s because in 'discard_serial_devices'" % device.name
    return None
  else:
    print "%s accepted" % device.name
    return device

def run_shell_command(command):
  """run shell command"""
  debug = False
  
  ret = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  out= ret.stdout.readlines()
  err= ret.stderr.readlines()
  if (len(out) >0 or len(err) >0 ) and debug == True:
    print "command", command
    if len(out) >0:
      print "out", out
    if len(err) >0:
      print "err", err
  return ret, out, err
  
def recursive_copy(gvfs_path, dest_path):
  """Recursively copy files from input GVFS path to destination path"""
  folders = []
  files = []
   
  infos = gvfs_path.enumerate_children('standard::name,standard::type,standard::size', gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS)
  for info in infos:
    child = gvfs_path.get_child(info.get_name())
    child_info = child.query_info("standard::display-name", gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS)
    child_name_lowered = child_info.get_display_name().decode('utf-8').lower()
    if info.get_file_type() == gio.FILE_TYPE_DIRECTORY:
      for discard_name_pattern in config["discard_folder_names"]:
        if discard_name_pattern in child_name_lowered :
          break
      else:
        print dest_path, child_info.get_display_name()
        folders.append((child, os.path.join(dest_path, child_info.get_display_name().decode('utf-8'))))
    elif info.get_file_type() == gio.FILE_TYPE_REGULAR:
      for discard_name_pattern in config["discard_file_names"]:
        if discard_name_pattern in child_name_lowered :
          break
      else:
        files.append((child, os.path.join(dest_path, child_info.get_display_name().decode('utf-8')), info.get_size()))
    
  #Copy files
  if len(files) > 0:
    total_size = 0
    for file_object, file_destination_path, file_size in files:
      total_size += file_size
    print "\nPrepare to copy %s in %s" % (pretty_print_size(total_size), dest_path)
    copy_files(files)     

  for folder_object, folder_destination_path in folders :
    recursive_copy(folder_object, folder_destination_path)

def copy_files(files):
  """Copy files"""
  debug = False
  
  for file_object, file_destination_path, file_size in files:
    created = False
    
    if debug == False :
      #Ensure folder exists
      folder_destination_path = os.path.split(file_destination_path)[0]
      dest_folder = gio.File(folder_destination_path.encode('utf-8'))
      if not dest_folder.query_exists() or dest_folder.query_file_type(gio.FILE_QUERY_INFO_NONE) != gio.FILE_TYPE_DIRECTORY:
        dest_folder.make_directory_with_parents()
      
      #Create and copy data
      print file_destination_path
      dest_file = gio.File(file_destination_path.encode('utf-8'))
      if not dest_file.query_exists() or dest_file.query_file_type(gio.FILE_QUERY_INFO_NONE) != gio.FILE_TYPE_REGULAR:
        #dest_file.create()
        file_object.copy(dest_file, nothing)
        created = True
    
    if created == True:
      print "%s %s copied" % (file_destination_path, pretty_print_size(file_size))
    else:
      if debug == False :
        print "%s already exists" % file_destination_path
      else:
        print "discarded by debug mode"
    
def pretty_print_size(size):
  """Format size number into human readable string"""
  symbols  = ["B", "KB","MB","GB"]
  pos = 0
  while size > 999 and pos < len(symbols)-1:
    pos+=1
    size /= 1000.0
  return "%.1f %s" %(size, symbols[pos])
  
def nothing(*args):
  """callback that does nothing"""
  pass
  
def copy_device(device):
  """Dump device files to disk"""
  #Try to access to device files
  if isinstance(device, UMS_Device):
    
    #Test if the device is already mount
    f = open("/etc/mtab", "r")
    lines = f.readlines()
    f.close()
    for l in lines:
      l = l.split()
      dev_path = l[0]
      mount_point = l[1]
      
      if dev_path == device.device_node:
        break
    else:
      command = "gvfs-mount -d %s" % device.device_node
      ret, out, err = run_shell_command(command)
      if len(err) > 0:
        print "\n%s %s discarded at mount 1" % (device.device_node, device.name)
        print err
        return False #Discard this device
      
    #Test if the device is mounted now
    command = "gvfs-ls %s -l --attributes=standard::display-name" % mount_point
    ret, out, err = run_shell_command(command)
    if len(err) > 0:
      print "\n%s %s discarded because mount_point %s is not accessible at mount 2" % (device.device_node, device.name, mount_point)
      print err
      return False #Discard this device
            
  elif isinstance(device, MTP_Device):
    #Test mountable device
    mount_point = "mtp://[usb:%s,%s]" % ("%.3i" % device.busnum, "%.3i" % device.devnum)

    #Test if the device is already mount
    command = "gvfs-ls %s -l --attributes=standard::display-name" % mount_point
    ret, out, err = run_shell_command(command)
    if len(err) > 0:
      #Try to mount
      command = "gvfs-mount -d %s" % device.device_node
      ret, out, err = run_shell_command(command)
      if len(err) > 0:
        print "\n%s %s discarded at mount 1" % (device.device_node, device.name)
        print err
        return False#Discard this device
      else:
        #Test if the device is mounted now
        command = "gvfs-ls %s -l --attributes=standard::display-name" % mount_point
        ret, out, err = run_shell_command(command)
        if len(err) > 0:
          print "\n%s %s discarded at mount 2" % (device.device_node, device.name)
          print err
          return False #Discard this device
          
  print "%s %s mounted at %s" % (device.device_node, device.name, mount_point)
  
  #Start to copy device files
  device_path = gio.File(mount_point)
  destination_path = os.path.join(config["destination_folder"], "%s_%s" % (device.serial, device.name))
  recursive_copy(device_path, destination_path)
  
  return True


print "### Welcome to USB_dumper ###"
read_config(config_file_path, config)
save_config(config_file_path, config)

#List USB devices already connected
print "Dumping already connected USB devices"
usb_devices_dumped = 0
context = pyudev.Context()
for connected_device in context.list_devices(subsystem="block") :
  device = pick_device(connected_device)
  if device != None:
    success = copy_device(device)
    if success == True :
      usb_devices_dumped += 1
  
for connected_device in context.list_devices(subsystem="usb") :
  device = pick_device(connected_device)
  if device != None:
    success = copy_device(device)
    if success == True :
      usb_devices_dumped += 1 
print "%i USB devices dumped" % usb_devices_dumped

#Listen to USB new devices connected
def udev_device_event(connected_device):
  """Callback when a new USB device is connected"""
  print('background event {0.action}: {0.device_path}'.format(connected_device))
  if connected_device.action == "add":
    device = pick_device(connected_device)
    if device != None:
      time.sleep(2) #Delay to be able to mount
      copy_device(device)
    
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')
monitor.filter_by(subsystem='block')
observer = pyudev.MonitorObserver(monitor, callback=udev_device_event, name='monitor-observer')
observer.daemon = False
print "Listening to new USB devices connected. Press Ctrl-Z to stop"
observer.start()
