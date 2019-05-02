# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

Vagrant.configure("2") do |config|

  config.vm.define "xenial" do |conf|
    conf.vm.box = "generic/ubuntu1604"
    conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--uartmode1", "disconnected"]
    end
  end

  config.vm.define "centos7" do |conf|
    conf.vm.box = "centos/7"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbook.yml"
    ansible.verbose = ENV['WARDROOM_VERBOSE'] || false
  end

end
