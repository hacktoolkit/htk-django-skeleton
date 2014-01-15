import requests

from fabric.api import *
from fabric.contrib.files import exists

def rollbar_record_deploy(access_token, env='other'):
    """Tracking deploys
    http://rollbar.com/docs/deploys_fabric/
    """
    environment = env
    local_username = local('whoami', capture=True)
    # fetch last committed revision in the locally-checked out branch
    revision = local('git log -n 1 --pretty=format:"%H"', capture=True)

    resp = requests.post('https://api.rollbar.com/api/1/deploy/', {
        'access_token': access_token,
        'environment': environment,
        'local_username': local_username,
        'revision': revision
    }, timeout=3)

    if resp.status_code == 200:
        print "Deploy recorded successfully."
    else:
        print "Error recording deploy:", resp.text

class FabricTaskManager(object):
    def deploy(self):
        """Default deploy task
        """
        print 'I am a dummy task'

    def _get_hosts(self):
        hosts = []
        return hosts

    def _get_setup_args(self):
        setup_args = '-h'
        return setup_args

class HtkAppServerFabricTaskManager(FabricTaskManager):
    SITE_BASE = '/home/deploy/sites/hacktoolkit.com'
    SITE_DIR = '%s/www' % SITE_BASE
    SCRIPTS_DIR = '%s/scripts' % SITE_DIR
    REPOSITORY = 'deploy@kebu.me:/home/git/git/hacktoolkit.com/www.git'
    ROLLBAR_ACCESS_TOKEN = 'ROLLBAR_ACCESS_TOKEN'

    def __init__(self, env=None):
        self.env = env

    def deploy(self):
        #self.test_local()
        self.clone_repository()
        self.update_code()
        #self.test_remote()
        self.restart()
        self.update_static_asset_version()
        self.post_deploy()

    def test_local(self):
        # if tests fail, deployment will stop
        local('make test')

    def test_remote(self):
        with cd(self.SITE_DIR):
            run('make test')

    def clone_repository(self):
        """Clones the repository if it doesn't exist yet
        """
        if not exists('%s/.git' % self.SITE_DIR):
            run('mkdir -p %s' % self.SITE_BASE)
            with cd(self.SITE_BASE):
                run('git clone %s' % self.REPOSITORY)
                run('git submodule init')
                run('git submodule update')

    def update_code(self):
        """Updates the code
        """
        with cd(self.SITE_DIR):
            run('git pull')
            run('git submodule init')
            run('git submodule update')

    def restart(self):
        """Restarts the services for this site
        - Apache
        """
        sudo('/etc/init.d/apache2 restart', shell=False)

    def update_static_asset_version(self):
        with cd(self.SCRIPTS_DIR):
            run('python update_static_asset_version.py')

    def post_deploy(self):
        """Anything else that we want to run at the end of a deploy
        """
        if self.env:
            rollbar_env = 'production' if self.env == 'prod' else self.env
            rollbar_record_deploy(self.ROLLBAR_ACCESS_TOKEN, env=rollbar_env)
