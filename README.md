# SamyGO for B-Series
Create your own firmware for your B-Series Samsung TV

## Usage Information:

Run 

    $ . setup.sh

to setup OE environment.

Setup generate two configuration files:

You can pass argument '-cl' if you want build environment for content library apps. Ex: ". setup.sh -cl"

 1. build-${DISTRO}/conf/local.conf
 2. build-${DISTRO}/env.source

bitbake downloads sources to `$HOME/sources`. You can change it defining `DL_DIR` variable

After configure, use bitbake command.

    $ bitbake -s #to see avaliable task

Normally 

    $ bitbake externalboot-base

is what you are looking for.

## Results

After building all tools, results are at *build-samygo/tmp/deploy/images* directory.

## Background Information:

OpenEmbedded: http://openembedded.org

SamyGO: https://www.samygo.tv

