# Copyright 2019 The Wardroom Authors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative 'lib/vagrant-wardroom/providers.rb'

Vagrant.configure('2') do |config|
  config.vm.define 'xenial' do |conf|
    conf.vm.box = 'generic/ubuntu1604'
    VagrantWardroom::Providers.configure(conf)
  end

  config.vm.define 'bionic' do |conf|
    conf.vm.box = 'generic/ubuntu1804'
    VagrantWardroom::Providers.configure(conf)
  end

  config.vm.define 'centos7' do |conf|
    conf.vm.box = 'centos/7'
    VagrantWardroom::Providers.configure(conf)
  end

  config.vm.provision 'ansible' do |ansible|
    ansible.playbook = 'ansible/playbook.yml'
    ansible.verbose = ENV['WARDROOM_VERBOSE'] || false
  end
end
