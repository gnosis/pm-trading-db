# -*- mode: ruby -*-
# vi: set ft=ruby :

$ethereumcpp = <<SCRIPT
if ! which eth | grep -q /usr/bin/eth || ! which solc | grep -q /usr/bin/solc; then
    DEBIAN_FRONTEND=noninteractive sudo apt-get install -y software-properties-common
    DEBIAN_FRONTEND=noninteractive sudo add-apt-repository -y ppa:ethereum/ethereum
    DEBIAN_FRONTEND=noninteractive sudo add-apt-repository -y ppa:ethereum/ethereum-dev
    DEBIAN_FRONTEND=noninteractive sudo apt-get update
fi

DEBIAN_FRONTEND=noninteractive sudo apt-get install libboost-filesystem1.54.0 libboost-program-options1.54.0 libboost-system1.54.0 solc

SCRIPT

$fucking_locale = <<SCRIPT
    locale-gen en_US en_US.UTF-8 pt_BR.UTF-8 de_DE.UTF-8
    dpkg-reconfigure locales
SCRIPT

$dependencies = <<SCRIPT
    DEBIAN_FRONTEND=noninteractive apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
    DEBIAN_FRONTEND=noninteractive echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
    DEBIAN_FRONTEND=noninteractive apt-get update
    # pyenv
    DEBIAN_FRONTEND=noninteractive apt-get install -y curl python-dev \
        libreadline-dev libbz2-dev libssl-dev libsqlite3-dev libxslt1-dev \
        libxml2-dev libxslt1-dev git python-pip build-essential automake libtool libffi-dev libgmp-dev pkg-config mongodb-org
SCRIPT

$pyenv = <<SCRIPT
if [ ! -d ~/.pyenv ]; then
    pip install --egg pyenv
else
    . ~/.bash_profile
    pyenv update
fi
if [ ! -f ~/.bash_profile ]; then
    touch ~/.bash_profile
fi
if ! grep -q pyenv ~/.bash_profile; then
    echo '
# pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
' >> ~/.bash_profile
fi

. ~/.bash_profile
pyenv install 2.7.9
pyenv rehash
pyenv global 2.7.9
SCRIPT

$requirements = <<SCRIPT
pip install --upgrade pip
pip install -r /vagrant/requirements.txt
SCRIPT

$node_dependencies = <<SCRIPT
    curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
    apt-get install -y nodejs        
SCRIPT

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.provider "virtualbox" do |v|
      v.memory = 2048
  end

  config.ssh.forward_agent = true
  config.vm.network :forwarded_port, host: 8282, guest: 8282
  config.vm.network :forwarded_port, guest: 27019, host: 27019

  config.vm.provision "shell", inline: $dependencies
  # config.vm.provision "shell", inline: $ethereumcpp
  config.vm.provision "shell", inline: $fucking_locale
  # config.vm.provision "shell", inline: $pyenv, privileged: false
  # config.vm.provision "shell", inline: $requirements, privileged: false
  config.vm.provision "shell", inline: $node_dependencies, privileged: true

end
