#!/usr/bin
# -*- coding:utf-8 -*-
#
#   xianwen.zhang
#   2017-12-10

import os
import json
import demjson
from socketserver import TCPServer, ForkingMixIn, StreamRequestHandler
from smtants.nest.include import log
from smtants.nest.include import mariadbclass 
from smtants.nest.target import cpu
from smtants.nest.target import mem


BUF_SIZE    = 1024

mariadbclass = mariadbclass.init('ops_nest')

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

        isOK = self.endpoint_exists(dataJson['endpoint'])
        
        if isOK:
            switch[dataType](dataJson)
        return

    # check endpoint is exists and add endpoint
    # @return  bool
    # 
    def endpoint_exists(self, endpoint):
        isOk = False
        try:
            sql = 'select count(1) from ops_nest_endpoint where endpoint="' + endpoint + '"'
            if  mariadbclass.query(sql)[0][0] < 1:
                sql = "insert into ops_nest_endpoint (endpoint,createdate) values('"
                sql += str(endpoint) + "'," 
                sql += "unix_timestamp(now()))"
                mariadbclass.execute(sql)
            isOk = True
        except Exception as e:
            log.lg_write_nest(" ==nest.endpoint_exists== " + str(e))
        return isOk

def nest():
    if not os.path.exists('cfg.json'):
        log.lg_write_nest(' ==nest.nest== cfg.json file is not exists !')
        exit()

    f = open('cfg.json',encoding='utf-8') 
    data = json.load(f)

    if not data['socket']['post']:
        log.lg_write_nest(' ==nest.nest== please enter the correct port !')
        exit()

    try:    
        server = NestServer((data['socket']['host'],data['socket']['post']),Handler)
        server.serve_forever()
    except Exception as e:
        log.lg_write_nest(' ==nest.nest== ' + str(e))
        exit()

if __name__ == "__main__":
    nest()