#!/usr/bin/python
import os
import commands
from collections import namedtuple

_ntuple_executestatus = namedtuple('executestatus', 'exitcode message')

class peercontrol:

  def __init__(self):
    pass

  def get_hostname(self):
    result=commands.getoutput("hostname")
    return result

  def get_peer_hostname(self):
    if self.get_hostname() == "appliance1":
        peer = "appliance2"
    else:
        peer = "appliance1"
    return peer

  def get_frontend0ip(self):
    ip = ''
    result=commands.getoutput("cat /etc/hosts | grep `hostname` | awk '{print $1}'")
    if result.find("\n") !=-1:
        ip = result.split("\n")[0]
    else:
        ip = result
    return ip

  def get_peer_ip(self):
    ip = ''
    peer_name = self.get_peer_hostname()
    result=commands.getoutput("cat /etc/hosts | grep %s | awk '{print $1}'" % (peer_name) )
    if result.find("\n") !=-1:
        ip = result.split("\n")[0]
    else:
        ip = result
    return ip

  def execute_cmd_in_peer(self,user_cmd):
    peer = self.get_peer_hostname()
    ssh_option = '-o BatchMode=yes -o StrictHostKeyChecking=no'
    cmd_redirect = '2>&1'
    cmd = "ssh %s -l root %s '%s' %s ; echo $?" % (ssh_option,peer,user_cmd,cmd_redirect)
    print cmd
    result=commands.getoutput(cmd)
    lines = result.split("\n")
    if len(lines) > 0:
        exitcode = int(lines[len(lines)-1])
        output = ''
        for line in lines:
            output += line + "\n"
        return _ntuple_executestatus(exitcode,output)
    else:
        return _ntuple_executestatus(255,result)

  def copy_from_peer(self,src_path,des_path):
    peer = self.get_peer_hostname()
    ssh_option = '-o BatchMode=yes -o StrictHostKeyChecking=no'
    cmd_redirect = '2>&1'
    cmd = "scp %s root@%s:%s %s %s" % (ssh_option,peer,src_path,des_path,cmd_redirect)
    print cmd
    return os.system(cmd)

  def push_to_peer(self,src_path,des_path):
    peer = self.get_peer_hostname()
    ssh_option = '-o BatchMode=yes -o StrictHostKeyChecking=no'
    cmd_redirect = '2>&1'
    cmd = "scp %s %s root@%s:%s %s" % (ssh_option,src_path,peer,des_path,cmd_redirect)
    print cmd
    return os.system(cmd)
