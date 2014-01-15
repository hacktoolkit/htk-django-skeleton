from fabric.api import *
from fab_helpers import HtkAppServerFabricTaskManager

env.user = 'deploy'
#env.key_filename = []
env.use_ssh_config = True
env.forward_agent = True

env.roledefs = {
    # app servers
    'prod' : [
        'hacktoolkit.com',
    ],
}

################################################################################
# App Servers

@roles('prod')
def deploy():
    mgr = HtkAppServerFabricTaskManager('prod')
    mgr.deploy()
