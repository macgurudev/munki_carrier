#!/usr/bin/python

import sys
import plistlib
import datetime
import tempfile
import os
import glob
import re
import shutil
import logging

## AUTHOR: macgurudev (Robert Henderson)
## DATE: 10-20-2016

###### DESCRIPTION ######
# Script will compare pkginfo files located in the master repo with those already
# on the client computer. If copy of file is not present, then it will copy the file
# while updating the catalog to a new default other than Production. 
#
# Script will also update the installer pkg info along with uninstaller pkg info (if present).
#
###### END ######

# Variables that can be changed

log_File = "/Users/admin/Library/Logs/munki_linker.log"		# Currently unused

bashCommand = "/usr/local/munki/makecatalogs"			# Munki Makecatalogs exec location
default_Catalog = "Master"					# Default catalog to use
master_PkgsInfo = "/usr/local/munkimaster/masterpkgsinfo"  	# Path to the Master pkgsInfo directory
master_Icons = "/usr/local/munkimaster/mastericons"		# Path to the Master icons directory

pkgs_Info = "/Volumes/MUNKI_Stor/munki_repo/pkgsinfo/master" 	# Path to client pkgsInfo directory
client_Icons = "/Volumes/MUNKI_Stor/munki_repo/icons"		# Path to client icons
nfs_Mount_Name = "master"					# NFS mount name for pkgs


## Init Variables. Leave these blank
icon_Name = ""
package_List = ""

###### MAIN SCRIPT ######

# Walk the master directory looking for only files
for root, dirs, files in os.walk(master_PkgsInfo, topdown=False):
	for name in files:
		# Exclude the damn .DS_Store files
		if name != ".DS_Store":
			full_Path = os.path.join(root, name) # Full path
			
			# Trim off the master directory path to get relative file path
			trimmed_Path = re.sub(master_PkgsInfo, '', full_Path)
			# Add to client Repo path
			client_Full_Path = pkgs_Info + trimmed_Path
			
			
			# Test to see if the file exists in the client pkgsInfo dir
			if os.path.exists(client_Full_Path):
				# Exists, do nothing
				#print "IGNOREING file",full_Path,"."
				pass
			else:
				# Does not exist, copy the file
				
				# Trim file name off full path
				trimmed_cFullPath = re.sub(name, '', client_Full_Path)
				
				# Create directories first
				if os.path.isdir(trimmed_cFullPath):
					pass
				else:
					os.makedirs(trimmed_cFullPath)
				
				# Copy the file from master to client
				shutil.copy(full_Path, trimmed_cFullPath)
				
				# Modify the catalog to the new default
				try:
					p = plistlib.readPlist(client_Full_Path)
					
					# Read current installer item location
					installerLocation = p["installer_item_location"]
					# Update installer location
					installerLocation = nfs_Mount_Name + "/" + installerLocation
					# Write change to memory
					p ["installer_item_location"] = installerLocation
					
					# See if uninstaller item location present
					try:
						uninstallerLocation = p["uninstaller_item_location"]
						uninstallerLocation = nfs_Mount_Name + "/" + uninstallerLocation
						p ["uninstaller_item_location"] = uninstallerLocation
					except:
						pass
					# Change catalog	
					p ["catalogs"] = [default_Catalog]
					
					# Icons, do we have an icon
					icon_Name = p["name"]
					icon_Path = master_Icons + "/" + icon_Name + ".png"
					#print icon_Path
					
					# Test to see if the file exists in master repo icon
					if os.path.exists(icon_Path):
						# Exists, copy over icon
						shutil.copy(icon_Path, client_Icons)
						print "Copied icon by name: ",icon_Path
					else:
						# No icon found using the name of the pkg, try icon_name key
						#print "TRYING TO COPY BY VALUE"
						icon_Name = p["icon_name"]
						#print "Icon Name: ",icon_Name
						icon_Path = master_Icons + "/" + icon_Name
						#print "Icon Name: ",icon_Path
						# Test to see if the file exists in master repo icon
						if os.path.exists(icon_Path):
							# Exists, copy over icon
							shutil.copy(icon_Path, client_Icons)
							print "Copied icon by key value: ", icon_Path
					
					# Add package to package list
					pack_Name = p["name"]
					pack_Ver = p["version"]
					pack_Output = pack_Name + ": v. " + pack_Ver
					package_List = package_List + '\n' + '\t' + pack_Output

					# Write changes back out
					plistlib.writePlist(p, client_Full_Path)
					
					# Run bash command to makecatalogs for munki
					os.system(bashCommand)
				except:
					print("Oh no!  Failure :(")
				
				print "Added new pkginfo for: ",name
			
# Output all packages added:
print ""
print "Packages added to the repo: "
print package_List
print ""

