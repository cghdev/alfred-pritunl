#!/usr/bin/env python

import requests
import base64
import os
import platform
import glob
import json
import getpass
import subprocess

class PYtunl:
    def __init__(self):
        if platform.system() != 'Darwin':
            print("[!] There was an error. This module is only supported in MacOS/OSx at the moment.")
            return None
        self.authKey = self.__getKey()
        self.profPath = self.__getProfilePath()
        self.serviceSck = 'localhost:9770'
        self.profiles = {}
        self.loadProfiles()

        if not self.authKey:
            print("[!] There was an error. Auth file was not found.")
            return None

        if not self.profPath:
            print("[!] There was an error. Profiles directory does not exist.")
            return None


    def __getKey(self):
        keyPath = '/Applications/Pritunl.app/Contents/Resources/auth'
        if os.path.isfile(keyPath):
            key = open(keyPath,'r').read()
            return key
        else:
            # auth file doesn't exist
            return None

    def __getProfilePath(self):
        if 'HOME' in os.environ:
            HOME = os.environ['HOME']
            profPath = '{}/Library/Application Support/pritunl/profiles'.format(HOME)
            if os.path.isdir(profPath):
                return profPath
        # Path doesn't exist
        return None

    def makeReq(self, verb='GET', endpoint=None, data={}):
        URL = 'http://{}/{}'.format(self.serviceSck, endpoint)
        headers = {'Auth-Key': self.authKey, 'User-Agent': 'pritunl'}
        try:
            if verb == 'GET':
                res = requests.get(URL, headers=headers)
            elif verb == 'POST':
                res = requests.post(URL, headers=headers, json=data)
            else:
                res = requests.delete(URL, headers=headers, json=data)

            if res.status_code != 200:
                raise Exception("Status code returned: {}".format(res.status_code))
            return res.text
        except Exception as err:
            return None

    def checkStatus(self):
        res = self.makeReq('GET', 'status')
        if res:
            try:
                status = json.loads(res)
                return status['status']

            except ValueError as err:
                return None

    def ping(self):
        res = self.makeReq('GET', 'ping')
        if res == None:
            return False
        else:
            return True

    def getConnections(self):
        cons = self.makeReq('GET', 'profile')
        if cons:
            try:
                return json.loads(cons)
            except ValueError as err:
                return cons

    def stopConnections(self):
        self.makeReq('POST', 'stop')

    def loadProfiles(self):
        files = glob.glob(self.profPath + '/*.conf')
        c = 1
        for f in files:
            profile = os.path.basename(f).split('.')[0]
            data = json.loads(open(f,'r').read())
            self.profiles[profile] = {'path': f, 'name': data['name'], 'id': c}
            c += 1

    def getProfile(self, id):
        profile = self.profiles[id]
        auth = None
        confFile = profile['path']
        ovpnFile = profile['path'].replace('.conf','.ovpn')
        conf = json.loads(open(confFile, 'r').read())
        ovpn = open(ovpnFile, 'r').read()
        for l in ovpn.split('\n'):
            if 'auth-user-pass' in l and len(l) <= 17: # check if it needs credentials and they are not provided as parameter
                auth = 'creds'
        if 'password_mode' in conf and conf['password_mode']:
            auth = conf['password_mode']
        command = 'security find-generic-password -w -s pritunl -a {}'.format(id).split() # loads key material from keychain
        try:
            res = subprocess.check_output(command)
            res = base64.b64decode(res)
            ovpn += '\n' + res
        except Exception as err:
            res = None
            print("There was an error: {}".format(err))
               
        return conf, ovpn, auth
                

    def connectProfile(self, id, user=None, password=None):
        data = {'id': id, 'reconnect': True, 'timeout': True}
        conf, ovpn, auth = self.getProfile(id)
        if auth:
            if 'pin' in auth:
                user = 'pritunl'
                if not password:
                    password = getpass.getpass("Enter the PIN: ")
                    if auth == 'otp_pin':
                        password += getpass.getpass("Enter the OTP code: ")
            if not user:
                user = raw_input("Enter the username: ")
            if not password:
                password = getpass.getpass("Enter the password: ")

            data['username'] = user
            data['password'] = password

        data['data'] = ovpn
        self.makeReq('POST', 'profile', data)


    def disconnectProfile(self, id):
        self.makeReq('DELETE', 'profile', {"id":"{}".format(id)})