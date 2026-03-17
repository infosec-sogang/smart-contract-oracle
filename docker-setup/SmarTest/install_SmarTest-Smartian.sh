#!/bin/bash

set -e

cd /home/test/tools/SmarTest-Smartian

# Install dependencies (assuming already installed by original SmarTest)
eval $(opam env)

# Install SmarTest-Smartian
git init
git remote add origin https://github.com/kupl/VeriSmart-public.git
git pull origin master --allow-unrelated-histories
patch -p1 < /home/test/tools/SmarTest-Smartian/SmarTest-Smartian.patch 
chmod +x build
eval $(opam env)
./build
