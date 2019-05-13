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

# Helper module for Wardroom
module VagrantWardroom
  # Helper modules for different Vagrant providers
  module Providers
    # Helper functions to configure VirtualBox
    module VirtualBox
      module_function

      FIRST_PARAVIRTUALIZATION_VERSION = Gem::Version.new('5.0.2')
      WARDROOM_NETWORK_NAME = ENV['WARDROOM_NETWORK_NAME'] || 'wardroom-private'

      def driver
        @@driver ||= VagrantPlugins::ProviderVirtualBox::Driver::Meta.new
      end

      def virtualbox_version
        @@virtualbox_version ||= Gem::Version.new(driver.version)
      end

      def supports_paravirtualization?
        @@supports_paravirtualization ||= Gem::Version.new(driver.version) >= FIRST_PARAVIRTUALIZATION_VERSION
      end

      def enable_high_performance(vbox)
        vbox.customize ['modifyvm', :id, '--paravirtprovider', 'kvm'] if supports_paravirtualization?
        vbox.customize ['modifyvm', :id, '--largepages', 'on']
        vbox.customize ['modifyvm', :id, '--vtxvpid', 'on']
        vbox.customize ['modifyvm', :id, '--x2apic', 'on']
        vbox.customize ['modifyvm', :id, '--biosapic', 'x2apic']
        vbox.customize ['modifyvm', :id, '--hpet', 'on']
      end

      def disable_uart(vbox)
        vbox.customize ['modifyvm', :id, '--uartmode1', 'disconnected']
      end

      def configure(conf, params)
        conf.vm.provider 'virtualbox' do |vbox, override|
          disable_uart(vbox)
          enable_high_performance(vbox)
          override.vm.network 'private_network', ip: params[:ip], virtualbox__intnet: WARDROOM_NETWORK_NAME if params.key?(:ip)
          vbox.memory = params[:memory] if params.key?(:memory)
          vbox.linked_clone = true if Gem::Version.new(Vagrant::VERSION) >= Gem::Version.new('1.8.0')
        end
      end
    end
  end
end
