#!/usr/bin/env python3

import os, sys, subprocess
import glob
import shutil
import re
from subprocess import DEVNULL

if os.geteuid()!=0:
  sys.exit("\033[031m[ERROR]\033[0m Blackmenu must run with root permission (use sudo or the script will fail)")

if not os.path.exists("/usr/share/gtk-engines/murrine.xml"):
  reply = str(input("\033[31m[Warning]\033[0m gtk murrine engine is not installed, it is highly recommanded to install it in order to have a proper display of the categories icons, do you want to install it now ? [Y/n] ")).lower().strip()
  if reply == "y" or reply == "yes" :
    os.system("pacman -S --noconfirm gtk-engine-murrine")

print("\033[32m[*]\033[0m Creating the new menu entry")

for file in glob.glob("/usr/share/applications/ba-*.desktop") + glob.glob("/usr/share/applications/ba_*.desktop") + glob.glob("/usr/share/desktop-directories/BlackArch*.directory"):
  os.remove(file)
if not os.path.exists("/etc/xdg/menus/applications-merged"):
  os.mkdir("/etc/xdg/menus/applications-merged")
shutil.copy2("/usr/share/blackmenu/X-BlackArch.menu","/etc/xdg/menus/applications-merged/X-BlackArch.menu")
shutil.copy2("/usr/share/blackmenu/BlackArch.directory","/usr/share/desktop-directories/BlackArch.directory")

for u in os.listdir("/usr/share/blackmenu/menu-i/"):
  c=u.replace("BlackArch-","").replace(".png","")
  file = open("/usr/share/blackmenu/dfdir", "r")
  out = open("/usr/share/desktop-directories/BlackArch-{}.directory".format(c), "w")
  for line in file:
    line = re.sub("Icon=.*","Icon=BlackArch-{}".format(c),line)
    line = re.sub("Name=.*","Name={}".format(c),line)
    out.write(line)

print("\033[32m[*]\033[0m Update the icons theme in use")

if os.path.exists("/home/{}/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml".format(os.environ["SUDO_USER"])):
  file = open("/home/{}/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml".format(os.environ["SUDO_USER"]))
  for line in file:
    if re.search("IconThemeName", line):
      thic=re.sub('"/>\n',"",re.sub('.*<property name="IconThemeName" type="string" value="',"",line))
else: thic="gnome"

if os.path.exists("/usr/share/icons/{}/icon-theme.cache".format(thic)):
  os.remove("/usr/share/icons/{}/icon-theme.cache".format(thic))

for file in glob.glob("/usr/share/blackmenu/menu-i/*"):
  filen = re.sub("/usr/share/blackmenu/menu-i/","",file)
  shutil.copy2(file, "/usr/share/icons/{}/32x32/apps/{}".format(thic,filen))
for file in glob.glob("/usr/share/icons/{}/32x32/apps/*".format(thic)):
  os.chmod(file, 0o755)

#Terminal to use for the blackarch entry
terminal="xfce4-terminal"

print("\033[32m[*]\033[0m Generating the menu, please wait...")

pkglist = str(subprocess.check_output('pacman -Qq', shell=True)).split("\\n")[:-1]
bapkgs = str(subprocess.check_output('pacman -Sqg blackarch', shell=True)).split("\\n")[:-1]
installed_ba = set(pkglist).intersection(bapkgs)
outinst = open("/usr/share/blackmenu/installed_ba.txt","w")
for i in range(len(installed_ba)):
  outinst.write("{}\n".format(list(installed_ba)[i]))

for u in installed_ba:

  pkginfo = str(subprocess.check_output('pacman -Si {}'.format(u), shell=True)).split("\\n")
  pkgi=[]
  for i in range(len(pkginfo)):
    if "Repository:blackarch" in pkginfo[i].replace(' ',''):
      for j in range(8):
         pkgi.append(pkginfo[i+j])
         pkgi[j]=pkgi[j].split(" : ")
         for k in range(len(pkgi[j])):
           pkgi[j][k]=pkgi[j][k].strip()
  del pkgi[0]
  del pkgi[3:6]
  pkgi=dict(pkgi)

  tname=pkgi["Name"]

  #Check blackarch group
  if len(pkgi["Groups"].split()) > 1 and pkgi["Groups"].split()[0] == "blackarch":
    subc=pkgi["Groups"].split()[1].replace("blackarch-","")
  else:
    continue

  desc=pkgi["Description"]

  #Find icon
  if len(glob.glob("/usr/share/icons/{}/*/*/{}.svg".format(thic,tname))) >=1:
    icon=tname
  elif len(glob.glob("/usr/share/icons/{}/*/*/kali-{}.svg".format(thic,tname))) >=1:
    icon="kali-{}".format(tname)
  else:
    icon="utilities-terminal"

  namecat="X-BlackArch-"
  if subc in {"code-audit", "decompiler", "dissassembler", "reversing"}:
    namecat+="Audit"
  elif subc in {"automation"}:
    namecat+="Automation"
  elif subc in {"backdoor", "keylogger", "malware"}:
    namecat+="Backdoor"
  elif subc in {"binary"}:
    namecat+="Binary"
  elif subc in {"bluetooth"}:
    namecat+="Bluetooth"
  elif subc in {"cracker"}:
    namecat+="Cracker"
  elif subc in {"crypto"}:
    namecat+="Crypto"
  elif subc in {"defensive"}:
    namecat+="Defensive"
  elif subc in {"dos"}:
    namecat+="Dos"
  elif subc in {"exploitation", "social", "spoof", "fuzzer"}:
    namecat+="Exploitation"
  elif subc in {"forensic", "anti-forensic"}:
    namecat+="Forensic"
  elif subc in {"honeypot"}:
    namecat+="Honeypot"
  elif subc in {"mobile"}:
    namecat+="Mobile"
  elif subc in {"networking", "fingerprint", "firmware", "tunnel"}:
    namecat+="Networking"
  elif subc in {"scanner","recon"}:
    namecat+="Scanning"
  elif subc in {"sniffer"}:
    namecat+="Sniffer"
  elif subc in {"voip"}:
    namecat+="Voip"
  elif subc in {"webapp"}:
    namecat+="Webapp"
  elif subc in {"windows"}:
    namecat+="Windows"
  elif subc in {"wireless"}:
    namecat+="Wireless"
  else:
    namecat+="Misc"

  bin=[]
  try:
    binp = str(subprocess.check_output("pkgfile -lbqR blackarch {}".format(tname), shell=True)).split("\\n")[:-1]
  except:
    continue
  excludes = ".keep|.exe|.applet|.txt|.dll|.conf|.apk|.key|.pem|.bat|.js|.cmd|.dex|.cache|.bfd|.mcld|.gold|xml.ap_|.ap_.d|.3ps|.prop|.gitignore|a.out|.xml|.xml.d|.ap_|.jar|.bin|.png|.css|.md|.app|.class|.pl|.rb|.ps|.ps1".split("|")
  if len(binp) >= 1:
    binp[0] = binp[0].replace("b'","")
    for i in range(len(binp)):
      if any(out in binp[i] for out in excludes):
        continue
      try:
        subprocess.check_call(["which",binp[i]],stdout=DEVNULL,stderr=DEVNULL)
      except:
        continue
      bin.append(binp[i].replace("/usr/bin/","").replace("/usr/sbin/","").replace("/usr/share/{}/".format(tname),""))

  rexec=[]
  for i in range(len(bin)):
    hf = open("/usr/share/blackmenu/help-flags.txt")
    for line in hf:
      if "{} ".format(bin[i]) == line[:len(bin[i])+1]:
        rexec.append([bin[i],line.replace(" ;\n","")])

  #Apply overrides
  #ovr=yaml.load(open('/usr/share/blackmenu/redirects.yaml'),Loader=yaml.FullLoader)
  #if tname in ovr["exec"]:
  #  rexec=ovr["exec"][tname]
  #if tname in ovr["icon"]:
  #  icon=ovr["icon"][tname]

  for i in range(len(rexec)):
    file = open("/usr/share/blackmenu/dfdesk")

    if rexec[i][0] == tname or len(rexec)==1:
      output = open("/usr/share/blackmenu/ba-{}.desktop".format(tname),"w")
    else:
      output = open("/usr/share/blackmenu/ba_{}-{}.desktop".format(tname,rexec[i][0]),"w")

    for line in file:
      if "Name=" in line:
         line = re.sub("Name=.*","Name={}".format(rexec[i][0].replace(".sh","").replace(".py","")),line)
      if "Icon=" in line:
         line = re.sub("Icon=.*","Icon={}".format(icon),line)
      if "Exec=" in line:
         line = re.sub("Exec=.*","Exec={} -e \"bash -ic \'/usr/bin/{}; exec $SHELL\'\"".format(terminal,rexec[i][1]),line)
      if "Categories=" in line:
         line = re.sub("Categories=.*","Categories={};".format(namecat),line)
      if "Comment=" in line:
         line= re.sub("Comment=.*","Comment={}".format(desc),line)
      output.write(line)


print("\033[32m[*]\033[0m Cleanup...")

for file in glob.glob("/usr/share/blackmenu/ba-*.desktop") + glob.glob("/usr/share/blackmenu/ba_*.desktop"):
  shutil.move(file,"/usr/share/applications")

os.system("xdg-icon-resource forceupdate")

print("\033[32m[*]\033[0m Done, if the new menu is not displaying correctly, you may need to restart xfce4")
