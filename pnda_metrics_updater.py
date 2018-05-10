import ansible.runner
import ansible.inventory
import sys
import os
import re
import json
import time
import requests
import socket
import subprocess

def getNodeIP():
    ips = []
    try:
        localip = socket.gethostbyname(socket.gethostname())
        cmd = [ 'consul', 'members', '--http-addr' , 'http://'+localip+':8500']
        output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
        linestr = output.split("\n")
        for i in range(1,len(linestr) -1 ):
            ips.append(linestr[i].split()[1].split(":")[0])
    except Exception as error:
        print "Error retrieving node ip " + str(error)
    return ips

def postMetrics(jsonstr,url):
    r = None
    try:
        r = requests.post(url, data=jsonstr)
        if r.status_code == 200:
            print "Metrics Updated Successfully"
        else:
            print "Metrics update failed - "+str(r.reason)
    except Exception as error:
        print "Error posting the metrics "+str(error)


class AnsibleRunner(object):
    def __init__(self,
                 host=None,
                 remote_user=None,
                 remote_pass=None,
                 pkey=None,
                 sudo=False):
        self.host_list = host
        self.remote_user = remote_user
        self.remote_pass = remote_pass
        self.sudo = sudo
        self.inventory = ansible.inventory.Inventory(self.host_list)
        self.private_key_file = pkey


    def do_reboot(self):
        runner = ansible.runner.Runner(
            module_name='command',
            module_args='reboot -f',
            remote_user=self.remote_user,
            remote_pass=self.remote_pass,
            private_key_file = self.private_key_file,
            inventory = self.inventory,
        )
        out = runner.run()
        if out['dark'].get(self.host_list[0],{}).get('msg') !=None and out['dark'].get(self.host_list[0],{}).get('failed') == True:
            sys.stderr.write('Error, %s\n'%out['dark'].get(self.host_list[0]).get('msg'))
            raise Exception(out['dark'].get(self.host_list[0]).get('msg'))
            # return
            # sys.exit()
        return out

    def execute_on_remote(self):
        yml = os.getcwd()+os.sep+'configs'+os.sep+'jump.yaml'
        out = os.system('ansible-playbook %s'%yml)
        return out

    def copy(self,filename,src,dest):
        if containerized:
            runner = self.container_copy(src,dest,container_name)
        runner = ansible.runner.Runner(
            module_name='copy',
            module_args='src=%s%s dest=%s'%(src,filename,dest),
            remote_user=self.remote_user,
            remote_pass=self.remote_pass,
            private_key_file = self.private_key_file,
            inventory = self.inventory,
        )
        out = runner.run()
        return out

    def fetch(self,filename,src,dest,flat='yes'):
        runner = ansible.runner.Runner(
            module_name='fetch',
            module_args='src=%s%s dest=%s flat=%s'%(src,filename,dest,flat),
            remote_user=self.remote_user,
            remote_pass=self.remote_pass,
            private_key_file = self.private_key_file,
            inventory = self.inventory,
        )
        out = runner.run()
        return out

    # can perform all shell operations Ex: rm /tmp/output
    def shell(self,command):
        runner = ansible.runner.Runner(
            module_name='shell',
            module_args=command,
            remote_user=self.remote_user, 
            remote_pass=self.remote_pass,
            private_key_file = self.private_key_file,
            inventory = self.inventory,
        )
        out = runner.run()
        return out 


ips = getNodeIP()
print ips
nodestatuslst = []
for ip in ips:
    print ip
    controller_hosts = [ip]
    ansi_runner = AnsibleRunner(controller_hosts,'cuser',None,'mirror.pem')
    out = ansi_runner.shell('cat /var/run/reboot-required')
    print out
    stdout = out['contacted'][ip]['stdout']
    if stdout != None and stdout.strip():
        reason = stdout.strip()
        data = {}
        data['source'] = ip
        data['metric'] = ip+".restart"
        data['value'] = 'true'
        data['causes'] = reason
        data['timestamp'] = time.time() * 1000
        nodestatuslst.append(data)

alldata = {}
alldata['data'] = nodestatuslst
alldata['timestamp'] = time.time() * 1000

payloadjson = json.dumps(alldata)
print payloadjson
# Hard coded url should replaced with edge node url which should be identified dynamically 
# Or run the script from edge node and replace hostname as localhost
postMetrics(payloadjson,'http://localhost:3001/metrics');

