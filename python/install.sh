#!/bin/bash
############## [Mac] ##############
# install java (at least 8)
brew tap adoptopenjdk/openjdk
brew cask install adoptopenjdk13

# install ant
brew install ant

# set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home)

# Download pylucene 
wget https://downloads.apache.org/lucene/pylucene/pylucene-8.6.1-src.tar.gz
tar -zxvf pylucene-8.6.1-src.tar.gz

# install jcc
cd pylucene-8.6.1
cd jcc
python3 setup.py build
python3 setup.py install

# install pylucene
cd ../
# - modify the makefile
sed -i "bs" "1i\\
ANT=ant\\
PYTHON=python3\\
JCC=python3 -m jcc\\
NUM_FILES=8\\
" Makefile

# - make
make
make install 

