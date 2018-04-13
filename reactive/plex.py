from charms.reactive import when, when_all, when_not, set_state
from charmhelpers.core.hookenv import status_set, log
from charmhelpers.core import hookenv
from charmhelpers.core import host
from charmhelpers.fetch import apt_install
from crontab import CronTab
from glob import glob
import urllib.request
import os
import socket
import tarfile


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
    if config['plex-pass-token']:
        download_url = download_url + '&X-Plex-Token={}'.format(config['plex-pass-token'])
    urlobject = urllib.request.urlopen(download_url)
    filename = urlobject.geturl().split('/')[-1]
    log('File available for download: {}'.format(filename), 'INFO')

    # Download the deb
    fullpath = os.path.join(filepath, filename)
    if not os.path.isfile(fullpath):
        status_set('maintenance', 'downloading plex')
        log('Downloading plex', 'INFO')
        urllib.request.urlretrieve(download_url, fullpath)

    # Install package
    log('Installing  plex', 'INFO')
    status_set('maintenance', 'installing plex')
    apt_install(fullpath)
    hookenv.log("Plex installation complete", "INFO")

    # Clean up debs
    sortedFiles = sorted(os.listdir(filepath),
                         key=lambda f: os.stat(os.path.join(filepath, f)).st_mtime)
    deleteCount = max(len(sortedFiles) - config['keep-debs'], 0)
    for file in sortedFiles[0:deleteCount]:
        os.remove(os.path.join(filepath, file))

    hookenv.open_port(32400, 'TCP')
    set_state('plex.installed')
    status_set('active', '')


@when('plex.installed')
@when_not('plex.configured')
def configure_plex():
    config = hookenv.config()
    backups = './backups'
    host.service_stop('plexmediaserver.service')
    try:
        os.mkdir(backups)
    except OSError as e:
        if e.errno is 17:
            pass
    # if config['restore-config']:
    #     hookenv.log('Restoring plex config', 'INFO')
    #     status_set('maintenance', 'restoring config')
    #     backup_file = hookenv.resource_get('plex-config')
    #     # TODO: Implement full restore
    #     log('Full config restore not yet implemented in charm', 'ERROR')
    if config['restore-db']:
        hookenv.log('Restoring plex db', 'INFO')
        status_set('maintenance', 'restoring db')
        backup_file = hookenv.resource_get('plexdb')
        if backup_file:
            plugin_folder = '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases'
            # Need to clear the plugin folder
            for each_file in os.listdir(plugin_folder):
                file_path = os.path.join(plugin_folder, each_file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            # Restore database file
            with tarfile.open(backup_file, 'r:gz') as inFile:
                inFile.extractall(plugin_folder)
            # Rename to remove a date if it exists
            for file_name in glob(plugin_folder + '/com.plexapp.plugins.library.db*'):
                os.rename(file_name, plugin_folder + '/com.plexapp.plugins.library.db')
            host.chownr(plugin_folder, owner='plex', group='plex')
        else:
            hookenv.log("Add plex-db resource, see juju attach or disable restore-db", 'ERROR')
            status_set('blocked', 'Waiting on couchconfig resource')
            return
    else:
        pass
        # cp.start()
        # while not Path(cp.settings_file).is_file():
        #     time.sleep(1)
        # cp.stop()
        # cp.reload_config()
    host.service_start('plexmediaserver.service')
    status_set('active', 'Plex ready')
    set_state('plex.configured')


@when('plex.installed')
@when_not('cron.installed')
def setup_update_cron():
    config = hookenv.config()
    system_cron = CronTab(user='root')
    unit = hookenv.local_unit()
    directory = hookenv.charm_dir()
    action = directory + '/actions/update'
    command = "juju-run {unit} {action}".format(unit=unit, action=action)
    job = system_cron.new(command=command, comment="Plex update")
    job.setall(config['update-cron'])
    system_cron.write()
    set_state('cron.installed')

# TODO: Debug why this triggers constantly not just on config change of download-url (am I resetting it above?)
# TODO: Is this needed at all with the new install/update method?
# @when('config.changed.download-url')
# def url_updated():
#   log('Running install for url_update','INFO')
#   install_plex()


@when('config.changed.update-cron')
@when('cron.installed')
def update_cron():
    config = hookenv.config()
    cron = CronTab(user='root')
    job = next(cron.find_comment("Plex update"))
    job.clear()
    job.setall(config['update-cron'])
    cron.write()
    hookenv.log("Cron updated for: {}".format(config['update-cron']))


@when_all('plex.configured', 'plex-info.available', 'plex-info.triggered')
@when_not('plex-info.configured')
def configure_interface(plexinfo, *args):
    log('Configuring interface', 'INFO')
    config = hookenv.config()
    info = {'hostname': socket.gethostname(),
            'port': 32400,
            'user': config['user-name'],
            'passwd': config['passwd']
            }
    plexinfo.configure(**info)
