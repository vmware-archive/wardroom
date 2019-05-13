# Copyright 2019 The Wardroom Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# If you update this file, please follow
# https://suva.sh/posts/well-documented-makefiles

.DEFAULT_GOAL:=help

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: ## Build Ansible Galaxy role archives
	$(MAKE) galaxy-archive ROLE=common
	$(MAKE) galaxy-archive ROLE=docker
	$(MAKE) galaxy-archive ROLE=etcd
	$(MAKE) galaxy-archive ROLE=kubernetes
	$(MAKE) galaxy-archive ROLE=kubernetes-cni
	$(MAKE) galaxy-archive ROLE=kubernetes-common
	$(MAKE) galaxy-archive ROLE=kubernetes-master
	$(MAKE) galaxy-archive ROLE=kubernetes-node
	$(MAKE) galaxy-archive ROLE=kubernetes-user
	$(MAKE) galaxy-archive ROLE=packer-cleanup
	$(MAKE) galaxy-archive ROLE=providers
	$(MAKE) galaxy-archive ROLE=test_loadbalancer

build:
	mkdir -p build

galaxy-archive: build
	cd ansible/roles/$(ROLE) && tar cfz ../../../build/wardroom-$(ROLE).tar.gz *

clean: ## Delete build artifacts
	-rm -rf build
