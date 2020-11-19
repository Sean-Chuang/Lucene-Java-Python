#!/bin/bash
############## [Mac] ##############
# install java (at least 8)
brew tap adoptopenjdk/openjdk
brew cask install adoptopenjdk13

# install ant
brew install ant

# set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v1.8)

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
# - modify the makefile
cd ../
sed -i "bs" "1i\\
ANT=ant\\
PYTHON=python3\\
JCC=python3 -m jcc\\
NUM_FILES=8\\
" Makefile

# - make
make
make install 

# ========================================================= #
############## [Linux] ##############
# install java (at least 8)
sudo yum install java-1.8.0-openjdk

# install ant
sudo yum install ant

# set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home)

# Download pylucene
wget -O pylucene.tar.gz https://archive.apache.org/dist/lucene/pylucene/pylucene-6.5.0-src.tar.gz
mkdir pylucene
tar -zxvf pylucene.tar.gz -C pylucene --strip-components=1

# install jcc
cd pylucene
cd jcc
# Check python3 config
python3-config --ldflags
vim setup.py

python3 setup.py build
python3 setup.py install

# install pylucene
# - modify the makefile
cd ../
sed -i "bs" "1i\\
PREFIX_PYTHON=/usr\\
ANT=JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk.x86_64 /usr/bin/ant\\
PYTHON=$(PREFIX_PYTHON)/bin/python3\\
JCC=$(PYTHON) -m jcc --shared\\
NUM_FILES=10\\
" Makefile

# - make
make
make install