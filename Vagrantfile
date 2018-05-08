# -*- mode: ruby -*-
# vi: set ft=ruby :

# Specify minimum Vagrant version and Vagrant API version
# The VAGRANTFILE_API_VERSION sets the configuration version (older
# styles are supported for backwards compatibility). Please don't change
# it unless you know what you are doing.
Vagrant.require_version '>= 1.6.0'
VAGRANTFILE_API_VERSION = '2'

# Require 'yaml' module
require 'yaml'

# Read YAML file with VM details (box, CPU, and RAM)
machines = YAML.load_file(File.join(File.dirname(__FILE__), 'vagrant.yml'))

# Create and configure the VMs
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Always use Vagrant's default insecure key
  config.ssh.insert_key = false

  # Iterate through entries in YAML file to create VMs
  machines.each do |machine|
    config.vm.define machine['name'] do |srv|

      # Don't check for box updates
      srv.vm.box_check_update = false

      # Set machine's hostname
      srv.vm.hostname = machine['name']

      # Use VMware box by default
      srv.vm.box = machine['box']['vmw']

      # Configure default synced folder (disable by default)
      if machine['sync_disabled'] != nil
        srv.vm.synced_folder '.', '/vagrant', disabled: machine['sync_disabled']
      else
        srv.vm.synced_folder '.', '/vagrant', disabled: true
      end #if machine['sync_disabled']

      # Iterate through networks as per settings in machines.yml
      machine['nics'].each do |net|
        if net['ip_addr'] == 'dhcp'
          srv.vm.network net['type'], type: net['ip_addr']
        else
          srv.vm.network net['type'], ip: net['ip_addr']
        end # if net['ip_addr']
      end # machine['nics'].each

      # Configure CPU & RAM per settings in machines.yml (Fusion)
      srv.vm.provider 'vmware_fusion' do |vmw|
        vmw.vmx['memsize'] = machine['ram']
        vmw.vmx['numvcpus'] = machine['vcpu']
        if machine['nested'] == true
          vmw.vmx['vhv.enable'] = 'TRUE'
        end #if machine['nested']
      end # srv.vm.provider 'vmware_fusion'

      # Configure CPU & RAM per settings in machines.yml (VirtualBox)
      srv.vm.provider 'virtualbox' do |vb, override|
        vb.memory = machine['ram']
        vb.cpus = machine['vcpu']
        override.vm.box = machine['box']['vb']
        vb.customize ['modifyvm', :id, '--nictype1', 'virtio']
        vb.customize ['modifyvm', :id, '--nictype2', 'virtio']
      end # srv.vm.provider 'virtualbox'

      # Configure CPU & RAM per settings in machines.yml (Libvirt)
      srv.vm.provider 'libvirt' do |lv,override|
        lv.memory = machine['ram']
        lv.cpus = machine['vcpu']
        override.vm.box = machine['box']['lv']
        if machine['nested'] == true
          lv.nested = true
        end # if machine['nested']
      end # srv.vm.provider 'libvirt'
    end # config.vm.define
  end # machines.each

  # Apply Ansible playbook
  config.vm.provision 'ansible' do |ansible|
    ansible.playbook = 'ansible/playbook.yml'
    ansible.verbose = ENV['WARDROOM_VERBOSE'] || false
  end # config.vm.provision
end # Vagrant.configure
