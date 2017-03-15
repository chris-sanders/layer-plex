from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set
from charmhelpers.core import hookenv 
from charmhelpers.fetch import apt_install
import urllib.request
import os.path

config = hookenv.config()

@when_not('plex.installed')
def install_plex():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview

    # Parse the filename from the URL
    filename = config['download-url'].split('/')[-1]
    # Download the deb
    if not os.path.isfile(filename):
    	status_set('maintenance','downloading plex')
    	urllib.request.urlretrieve(config['download-url'],filename)
    status_set('maintenance','installing plex')
    apt_install('./{}'.format(filename))
    status_set('active','')
    set_state('plex.installed')
