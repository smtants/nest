#! /usr/bin python
# -*- coding:utf-8 -*-
#
#   do cpu related indicators
#   xianwen.zhang
#   2017-12-12

import os
import time
from smtants.nest.include import log 
from smtants.nest.include import mariadbfunc

def cpu(endpointId, obj):
    try:
        tarItems      = obj['value']
        user          = float(tarItems['cpu.user'])
        nice          = float(tarItems['cpu.nice'])
        system        = float(tarItems['cpu.system'])
        idle          = float(tarItems['cpu.idle'])
        iowait        = float(tarItems['cpu.iowait'])
        irq           = float(tarItems['cpu.irq'])
        softirq       = float(tarItems['cpu.softirq'])
        stealstolen   = float(tarItems['cpu.stealstolen'])
        guest         = float(tarItems['cpu.guest'])
        total         = user + nice + system + idle + iowait + irq + softirq + stealstolen + guest

        for key in dict(tarItems).keys():
            itemId = mariadbfunc.get_item_id(endpointId, key)
            if itemId > 0:
                precent = round(float(tarItems[key]) / total , 3)
                sql = 'insert into ops_history (itemid, value, precent, timestamp, step) values('
                sql += str(itemId) + ',"'
                sql += str(tarItems[key]) + '",'
                sql += str(precent) + ','
                sql += str(obj['timestamp']) + ','
                sql += str(obj['step']) + ')'
                mariadbfunc.execute(sql)
            else:
                log.lg_write_nest(" ==cpu.cpu== " + str(tarItems) + " item id get failed")
        
    except Exception as e:
        log.lg_write_nest(" ==cpu.cpu== " + str(e))

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

    cpu(1,tar)

if __name__ == "__main__":
    main() 