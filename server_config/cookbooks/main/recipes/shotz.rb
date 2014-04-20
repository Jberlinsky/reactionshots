directory '/home/shotz/sites' do
  owner 'shotz'
  group 'shotz'
  mode 0775
end

virtualenv '/home/shotz/sites/shotzapp.com' do
  owner 'shotz'
  group 'shotz'
  mode 0775
end

directory '/home/shotz/sites/shotzapp.com/run' do
  owner 'shotz'
  group 'shotz'
  mode 0775
end

directory '/home/shotz/sites/shotzapp.com/checkouts' do
  owner 'shotz'
  group 'shotz'
  mode 0775
end

git '/home/shotz/sites/shotzapp.com/checkouts/reactionshots' do
  repository 'git@github.com:ckushner/reactionshots.git'
  reference 'HEAD'
  user 'shotz'
  group 'shotz'
  action :sync
end

script 'Install Requirements' do
  interpreter 'bash'
  user 'shotz'
  group 'shotz'
  code <<-EOH
  /home/shotz/sites/shotzapp.com/bin/pip install -r /home/shotz/sites/shotzapp.com/checkouts/reactionshots/requirements.txt
  EOH
end

cookbook_file '/etc/init/shotz-gunicorn.conf' do
  source 'gunicorn.conf'
  owner 'root'
  group 'root'
  mode 0644
end

cookbook_file '/etc/init/shotz-celery.conf' do
  source 'celery.conf'
  owner 'root'
  group 'root'
  mode 0644
end

service 'shotz-gunicorn' do
  provider Chef::Provider::Service::Upstart
  enabled true
  running true
  supports :restart => true, :reload => true, :status => true
  action [:enable, :start]
end

service 'shotz-celery' do
  provider Chef::Provider::Service::Upstart
  enabled true
  running true
  supports :restart => true, :reload => true, :status => true
  action [:enable, :start]
end
