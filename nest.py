#!/usr/bin
# -*- coding:utf-8 -*-
#
#   xianwen.zhang
#   2017-12-10

import os,time
import json
import demjson
from socketserver import TCPServer, ForkingMixIn, StreamRequestHandler
from smtants.nest.include import log
from smtants.nest.include import mariadbfunc 
from smtants.nest.target import cpu
from smtants.nest.target import mem


BUF_SIZE = 1024
history  = 1

class NestServer(ForkingMixIn, TCPServer) : pass

class Handler(StreamRequestHandler):
    def handle(self):
        data = self.request.recv(BUF_SIZE)
        addr = self.request.getpeername()
        # current_process_id = os.getpid()

        dataJson = demjson.decode(data)
        dataType = dataJson['dataType']

        switch = {
            "cpu": cpu.cpu,
            "mem": mem.mem
        }

        endpointId = mariadbfunc.get_endpoint_id(dataJson['endpoint'])
        if endpointId > 0:
            switch[dataType](endpointId, dataJson)
        
        self.delete_history()
        return

    #   delete history before history
    def delete_history(self):
        try:
            sql = 'delete from ops_history where timestamp < ' + str(int(time.time()) - history * 24 * 3600)
            mariadbfunc.execute(sql)
        except Exception as e:
            log.lg_write_nest(' ==nest.nest== delete history failed !')

def nest():
    if not os.path.exists('cfg.json'):
        log.lg_write_nest(' ==nest.nest== cfg.json file is not exists !')
        exit()

    f = open('cfg.json',encoding='utf-8') 
    data = json.load(f)

    if not data['socket']['post']:
        log.lg_write_nest(' ==nest.nest== please enter the correct port !')
        exit()

    if not data['history']:
        log.lg_write_nest(' ==nest.nest== please enter the history !')
        exit()
    history = data['history']

    try:    
        server = NestServer((data['socket']['host'],data['socket']['post']),Handler)
        server.serve_forever()
    except Exception as e:
        log.lg_write_nest(' ==nest.nest== ' + str(e))
        exit()

if __name__ == "__main__":
    nest()