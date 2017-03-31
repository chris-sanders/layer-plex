from charms.reactive import hook, when, when_any, when_not, set_state, remove_state
from charmhelpers.core.hookenv import status_set
from charmhelpers.core import hookenv 
from charmhelpers.fetch import apt_install
import urllib.request
import os


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
  filename = config['download-url'].split('/')[-1]
  
  # Download the deb
  fullpath = os.path.join(filepath,filename)
  if not os.path.isfile(fullpath):
    status_set('maintenance','downloading plex')
    urllib.request.urlretrieve(config['download-url'],fullpath)

  # Install package
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

@when('config.changed.download-url')
def url_updated():
  install_plex()

@when('plex.installed')
@when_not('layer-mac.installed')
def change_mac():
    set_state('layer-mac.ready')
