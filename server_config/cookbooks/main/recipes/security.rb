package 'ufw'

service 'ufw' do
  enabled true
  running true
  supports :status => true, :restart => true, :reload => true
  action [:enable, :start]
end

bash "Enable UFW" do
  user 'root'
  code <<-EOH
  ufw allow 22
  ufw allow 80
  ufw allow 4949
  ufw allow 8888
  EOH
end
