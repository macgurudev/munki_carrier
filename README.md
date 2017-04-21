# munki_carrier
Python script that allows a Master -- Client munki setup.

<b>Background</b>

Needed a way that "common" software could be packaged and distributed to all "clients" with-in our organization. These common packages for example could be Microsoft Office, Adobe, Browsers, etc.

Clients would like to still have control over when these packages would become available to their end users. They also like having their own Admin tools to work with their repos and they like the ability to add their own customizations to the pkginfo. This is the solution I came up with.

<b>What is it and summary of the setup</b>
Munki_carrier is the idea that allows the above to be met. A "master" repo is setup on a single server. This master is where all "common" software is imported. This repo is then shared to the client's server via NFS mounts. Only the pkgs, pkgsinfo, and icons directories are shared from the master repo to the client's.

The pkgs directory is mounted directly with-in the client's current munki_repo and mapped to a folder called master.
  ex: /Users/Shared/munki_repo/pkgs/master

The pkgsinfo and icons directories are mounted some place outside the client's munki_repo. 
  ex: /usr/local/munkimaster/masterpkgs or /usr/local/munkimaster/mastericons

This is where munki_carrier comes in. The python script will look at the master pkgsinfo files and see if these files already exist in the client's munki_repo. If a pkginfo file does not exist, it is copied into the client's repo and the default catalog is changed to what is set in the script.
  ex: Files copied to /Users/munki_repo/pkgsinfo/master/

The script will also copy any icons if available from the master icon directory into the client's icons directory. This can either be just by the "name" of the pkg or via the "icon_name" key.


