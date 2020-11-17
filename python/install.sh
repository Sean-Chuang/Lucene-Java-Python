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
#wget https://downloads.apache.org/lucene/pylucene/pylucene-8.6.1-src.tar.gz
wget -O pylucene.tar.gz https://archive.apache.org/dist/lucene/pylucene/pylucene-7.4.0-src.tar.gz
mkdir pylucene
tar -zxvf pylucene.tar.gz -C pylucene --strip-components=1

# install jcc
cd pylucene
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

