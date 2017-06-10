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
  download_url = config['download-url']
  log('download_url: {}'.format(download_url),'DEBUG')
  if config['plex-pass-token']:
    download_url = download_url+'&X-Plex-Token={}'.format(config['plex-pass-token'])
    log('Pass download_url: {}'.format(download_url),'DEBUG')
  urlobject = urllib.request.urlopen(download_url)
  filename = urlobject.geturl().split('/')[-1]
  log('Download url: {}'.format(urlobject.geturl()),'DEBUG')
  log('file to download: {}'.format(filename),'INFO')
  
  # Download the deb
  fullpath = os.path.join(filepath,filename)
  if not os.path.isfile(fullpath):
    status_set('maintenance','downloading plex')
    log('Downloading plex','INFO')
    urllib.request.urlretrieve(download_url,fullpath)

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
