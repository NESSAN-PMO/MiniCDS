#!/usr/bin/env python

from __future__ import print_function
import os, sys
import configparser

#Common configuration file

#General paths
selfpath=os.path.abspath(__file__)
configpath=os.path.dirname(selfpath)+"/config"

#Read values from main.cfg
config = configparser.ConfigParser()
config.read(configpath+"/main.cfg")
cfg_general=config._defaults

def printCfg():
    for section in config.sections():
        print()
        print("================ "+section+" ================")
        for item in config.items(section):
            print(item)

if __name__ == '__main__':
	printCfg()
