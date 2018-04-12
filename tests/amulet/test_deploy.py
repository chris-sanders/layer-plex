#!/usr/bin/python3

import pytest
import amulet
import requests


@pytest.fixture(scope="module")
def deploy():
    deploy = amulet.Deployment(series='xenial')
    deploy.add('plex')
    deploy.setup(timeout=1000)
    return deploy


@pytest.fixture(scope="module")
def plex(deploy):
    return deploy.sentry['plex'][0]


class TestPlex():

    def test_deploy(self, deploy):
        try:
            deploy.sentry.wait(timeout=1500)
        except amulet.TimeoutError:
            raise

    def test_web_frontend(self, deploy, plex):
        page = requests.get('http://{}:{}'.format(plex.info['public-address'], 32400))
        assert page.status_code == 200
        print(page)

    def test_action_update(self, deploy, unit):
        uuid = unit.run_action('renew-upnp')
        action_output = deploy.get_action_output(uuid, full_output=True)
        print(action_output)
        assert action_output['status'] == 'completed'

    #     # test we can access over http
    #     # page = requests.get('http://{}'.format(self.unit.info['public-address']))
    #     # self.assertEqual(page.status_code, 200)
    #     # Now you can use self.d.sentry[SERVICE][UNIT] to address each of the units and perform
    #     # more in-depth steps. Each self.d.sentry[SERVICE][UNIT] has the following methods:
    #     # - .info - An array of the information of that unit from Juju
    #     # - .file(PATH) - Get the details of a file on that unit
    #     # - .file_contents(PATH) - Get plain text output of PATH file from that unit
    #     # - .directory(PATH) - Get details of directory
    #     # - .directory_contents(PATH) - List files and folders in PATH on that unit
    #     # - .relation(relation, service:rel) - Get relation data from return service
