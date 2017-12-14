#! /usr/bin python
# -*- coding:utf-8 -*-
#
#   do cpu related indicators
#   xianwen.zhang
#   2017-12-12

import os
import time
from smtants.nest.include import log 
from smtants.nest.include import mariadbclass 

DATABASE = 'ops_cpu'
mariadbclass = mariadbclass.init(DATABASE)

def cpu(obj):
    try:
        tarItems = obj['value']
        for key in tarItems: 
            tar = {}
            tar['dataType']  = key
            tar['endpoint']  = obj['endpoint']
            tar['timestamp'] = obj['timestamp']
            tar['value']     = tarItems[key]
            tar['step']      = obj['step'] 

            cpu_add(tar)
        
    except Exception as e:
        log.lg_write_nest(" ==cpu.cpu== " + str(e))
        exit()

def cpu_add(tar):
    try:
        table = DATABASE + '_' + tar['dataType'].split('.')[1]
        sql = 'insert into ' + table + ' (endpoint, value, timestamp, step) values("'
        sql += str(tar['endpoint']) + '","'
        sql += str(tar['value']) + '",'
        sql += str(tar['timestamp']) + ','
        sql += str(tar['step']) + ')'
        mariadbclass.execute(sql)
    except Exception as e:
        log.lg_write_nest(" ==cpu.cpu_add== " + str(e))
        exit()

def main():
    if not os.path.exists('/proc/stat'):
        log.lg_write_nest(" ==cpu.main== /proc/stat is not exists !")
        exit()
    
    f = open('/proc/stat', 'r', 1)
    cpuTarList = f.readline().split()

    obj = {}
    obj['cpu.user']        = cpuTarList[1]
    obj['cpu.nice']        = cpuTarList[2]
    obj['cpu.system']      = cpuTarList[3]
    obj['cpu.idle']        = cpuTarList[4]
    obj['cpu.iowait']      = cpuTarList[5]
    obj['cpu.irq']         = cpuTarList[6]
    obj['cpu.softirq']     = cpuTarList[7]
    obj['cpu.stealstolen'] = cpuTarList[8]
    obj['cpu.guest']       = cpuTarList[9]

    f.close()
    
    tar = {}
    tar['endpoint']  = "endpoint"
    tar['timestamp'] = int(time.time())
    tar['step']      = 60
    
    #   cpu
    tar['dataType'] = 'cpu'
    tar['value']    = obj

    cpu(tar)

if __name__ == "__main__":
    main() 