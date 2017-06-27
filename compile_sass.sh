#!/bin/bash
cd /vagrant_data/static
printf "Compiling SASS ...\n"
bundler
bundler exec compass compile