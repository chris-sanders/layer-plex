# Overview

This charm provides [Plex Media Server][plex]

# Usage

To deploy:

    juju deploy plex

You can then browse to http://ip-address:32400/web to configure the plex server.

## Scale out Usage

This charm does not adderss multi-server configurations at this time.

## Known Limitations and Issues

This only currently installs plex, in the future it can be expanded to 
 * select latest release on install 
 * upgrade versions after install
 * relate to media providers to trigger automatic library scans
 * change default port configuration

# Configuration

Note the configuration option "download-url" was set during initial charm creation. New versions or plex pass versions may be available. Plex does not maintain a repository for automatic updates. This option should be set to the latest release while deploying to get the latest version.

Addational optoins are provided to configure the host:
 * hostname: Set the hostname which plex identifies the server by
 * interface & address: Set a MAC address, usefull for static DHCP and firewall holes required for configuring plex. 

# Contact Information

## Upstream Project Name

  - https://github.com/chris-sanders/layer-plex
  - https://github.com/chris-sanders/layer-plex/issues
  - email: sanders.chris@gmail.com


[plex]: http://plex.tv
