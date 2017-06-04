from charms.reactive import hook, when, when_all, when_any, when_not, set_state, remove_state
from charmhelpers.core.hookenv import status_set, log
from charmhelpers.core import hookenv 
from charmhelpers.fetch import apt_install
import urllib.request
import os
import socket

@when_not('plex.installed')
def install_plex():
  # Create directory for debs
  config = hookenv.config()
  filepath = './debs'
  try:
    os.mkdir(filepath)
  except OSError as e:
    if e.errno is 17:
      pass

  # Parse the filename from the URL
  if config['download-url'] != '' and \
     config['download-url'] != "https://plex.tv/downloads/latest/1?build=linux-ubuntu-x86_64&distro=ubuntu":
    filename = config['download-url'].split('/')[-1]
  else:
    config['download-url']="https://plex.tv/downloads/latest/1?build=linux-ubuntu-x86_64&distro=ubuntu"
    filename = "plex.deb"
  
  # Download the deb
  fullpath = os.path.join(filepath,filename)
  if not os.path.isfile(fullpath):
    status_set('maintenance','downloading plex')
    log('Downloading plex','INFO')
    urllib.request.urlretrieve(config['download-url'],fullpath)

  # Install package
  log('Installing  plex','INFO')
  status_set('maintenance','installing plex')
  apt_install(fullpath)

  # Clean up debs
  mtime = lambda f: os.stat(os.path.join(filepath,f)).st_mtime
  sortedFiles = sorted(os.listdir(filepath),key=mtime)
  deleteCount = max(len(sortedFiles)-config['keep-debs'],0)
  for file in sortedFiles[0:deleteCount]:
    os.remove(os.path.join(filepath,file))

  hookenv.open_port(32400,'TCP')
  set_state('plex.installed')
  status_set('active','')

#TODO: Debug why this triggers constantly not just on config change of download-url (am I resetting it above?)
#@when('config.changed.download-url')
#def url_updated():
#  log('Running install for url_update','INFO')
#  install_plex()

@when_all('plex.installed','plex-info.available','plex-info.triggered')
@when_not('plex-info.configured')
def configure_interface(plexinfo,*args):
  log('Configuring interface','INFO')
  config = hookenv.config()
  info = {'hostname':socket.gethostname(),
          'port':32400,
          'user':config['user-name'],
          'passwd':config['passwd']
         }
  plexinfo.configure(**info)
