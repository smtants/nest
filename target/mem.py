#! /usr/bin python
# -*- coding:utf-8 -*-
#
#   do mem related indicators
#   xianwen.zhang
#   2017-12-12

import os
import time
from smtants.nest.include import log 
from smtants.nest.include import mariadbclass 

DATABASE = 'ops_mem'
mariadbclass = mariadbclass.init(DATABASE)

def mem(obj):
    try:
        tarList = obj['value']
        for key in tarList: 
            tar = {}
            tar['dataType']  = key
            tar['endpoint']  = obj['endpoint']
            tar['timestamp'] = obj['timestamp']
            tar['value']     = tarList[key]
            tar['step']      = obj['step']   
            
            mem_add(tar)

    except Exception as e:
        log.lg_write_nest(" ==mem.mem== " + str(e))
        exit()

def mem_add(tar):
    try:
        table = DATABASE + '_' + tar['dataType'].split('.')[1]
        sql = 'insert into ' + table + ' (endpoint, value, timestamp, step) values("'
        sql += str(tar['endpoint']) + '","'
        sql += str(tar['value']) + '",'
        sql += str(tar['timestamp']) + ','
        sql += str(tar['step']) + ')'
        mariadbclass.execute(sql)
    except Exception as e:
        log.lg_write_nest(" ==cpu_add== " + str(e))
        exit()

def main():
    if not os.path.exists('/proc/meminfo'):
        exit('/proc/meminfo is not exists !')
    
    f = open('/proc/meminfo', 'r', 1)
    meminfo = f.read().split('\n')

    memtotal  = 0
    memfree   = 0
    buffers   = 0
    cached    = 0
    memused   = 0
    swaptotal = 0
    swapfree  = 0
    swapused  = 0
    for value in meminfo:
        if value.find('MemTotal') > -1:
            memtotal = int(value.split()[1])
        elif value.find('MemFree') > -1:
            memfree = int(value.split()[1])
        elif value.find('Buffers') > -1:
            buffers = int(value.split()[1])
        elif value.find('Cached') > -1:
            cached = int(value.split()[1])
        elif value.find('SwapTotal') > -1:
            swaptotal = int(value.split()[1])
        elif value.find('SwapFree') > -1:
            swapfree = int(value.split()[1])
        
    obj = {}
    obj['mem.memtotal']  = memtotal
    obj['mem.memfree']   = memfree
    obj['mem.buffers']   = buffers
    obj['mem.cached']    = cached
    obj['mem.memused']   = memtotal - memfree - buffers - cached
    obj['mem.swaptotal'] = swaptotal
    obj['mem.swapfree']  = swapfree
    obj['mem.swapused']  = swaptotal - swapfree

    f.close()
    
    tar = {}
    tar['endpoint']  = "endpoint"
    tar['timestamp'] = int(time.time())
    tar['step']      = 60
    
    #   cpu
    tar['dataType'] = 'cpu'
    tar['value']    = obj

    mem(tar)

if __name__ == "__main__":
    main() 