from fabric.api import env, local, sudo
env.user = 'root'
env.hosts = ['ops.jasonberlinsky.com']

env.chef_executable = '/usr/local/rvm/gems/ruby-2.0.0-p353/bin/chef-solo'

def install_chef():
  sudo('apt-get update', pty=True)
  sudo('apt-get install -y git-core rubygems ruby ruby-dev', pty=True)
  sudo('gem install chef', pty=True)

def sync_config():
  local('rsync -av . %s@%s:/etc/chef' % (env.user, env.hosts[0]))

def update():
  sync_config()
  sudo('cd /etc/chef && %s' % env.chef_executable, pty=True)
