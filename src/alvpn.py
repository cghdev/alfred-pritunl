#!/usr/bin/env python
# encoding: utf-8

from pytunl import PYtunl
import argparse
import json
import sys
from workflow import Workflow3, ICON_ERROR, ICON_WARNING
from workflow.notify import notify
from subprocess import Popen, PIPE, check_output
import os
from time import time
from datetime import datetime, timedelta

ICON_CONNECTED = 'icons/locked.png'
ICON_DISCONNECTED = 'icons/unlocked.png'
ICON_CONNECTING = 'icons/unlocked2.png'
ICON_ISSUE = 'icons/issue.png'
ICON_DISCONNECT = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarDeleteIcon.icns'

def main(wf):
    parser = argparse.ArgumentParser(description='Pritunl command line client.', formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40))
    parser.add_argument('-l', '--list', action='store_true', help='List connections.')
    parser.add_argument('-c', '--connect', metavar='<profile>', help='Connects to <profile>.')
    parser.add_argument('-d', '--disconnect', metavar='<profile>', help='Disconnects <profile> or "all".')
    parser.add_argument('-s', '--search', metavar='<profile>', help='Searchs for <profile>.')
    args = parser.parse_args()
    if not args.list and not args.connect and not args.disconnect:
        parser.print_help()
        exit(1)

    pt = PYtunl()
    if not pt.ping():
        wf.add_item(title='Pritunl service unavailable',
                        subtitle='Verify it is listening in pot 9770',
                        arg='test',
                        valid=True,
                        icon=ICON_ERROR)
        wf.send_feedback()
        return

    if args.list:
        cons = listConnections(pt, args.search)
        for c in sorted(cons,key=sortConnected):
            if c['status'] == 'Connected':
                ic = ICON_CONNECTED
                action = '--disconnect {}'.format(c['id'])
                sub = u'↩ to disconnect'
            elif c['status'] == 'Disconnected':
                ic = ICON_DISCONNECTED
                action = '--connect {}'.format(c['id'])
                sub = u'↩ to connect'
            elif c['status'] == 'Connecting':
                ic = ICON_CONNECTING
                action = '--disconnect {}'.format(c['id'])
                sub = u'Connecting... ↩ to cancel'

            it = wf.add_item(title=c['name'],
                        subtitle=sub,
                        arg=action,
                        valid=True,
                        icon=ic)
            if c['status'] == 'Connected':
                sec = timedelta(seconds=(int(time()) - c['timestamp']))
                since = ''
                d = datetime(1,1,1) + sec
                since += str(d.day-1) + ' days ' if d.day-1 else ''
                since += str(d.hour) + ' hrs ' if d.hour else ''
                since += str(d.minute) + ' mins ' if d.minute else ''
                since += str(d.second) + ' secs' if d.second else ''
                sub = 'Server: {} | Client: {} | {}'.format(c['server_addr'], c['client_addr'], since)
                m = it.add_modifier('cmd', subtitle=sub, valid=False)
        if not cons:
            wf.add_item(title=u'No matching connections ¯\_(ツ)_/¯',
            icon=ICON_WARNING)

        wf.send_feedback()

    elif args.connect:
        connect(pt, args.connect)
    elif args.disconnect:
        disconnect(pt, args.disconnect)

def sortConnected(conn):
    return conn['status'] == 'Disconnected'

def listConnections(pt, search=None):
    profs = []
    cons = pt.getConnections()
    for p in pt.profiles:
        d = {}
        d['status'] = 'Disconnected'
        d['client_addr'] = None
        d['server_addr'] = None
        d['timestamp'] = None
        if p in cons:
            d['status'] = cons[p]['status'].capitalize()
            d['server_addr'] = cons[p]['server_addr']
            d['client_addr'] = cons[p]['client_addr']
            d['timestamp'] = cons[p]['timestamp']
        if not search or search.lower() in pt.profiles[p]['name'].lower():
            d['id'] = pt.profiles[p]['id']
            d['name'] = pt.profiles[p]['name']
            profs.append(d)
        if d['status'] == 'Connecting':
            wf.rerun = 1
    return profs

def profile(pt, id):
    for p in pt.profiles:
        if id == pt.profiles[p]['name'] or id == str(pt.profiles[p]['id']):
            return p

def disconnect(pt, id):
    if id == 'all':
        pt.stopConnections()
    else:
        pt.disconnectProfile(profile(pt, id))

def connect(pt, id):
    prof = profile(pt, id)
    _, auth = pt.getProfile(prof)
    user = None
    password = None
    if auth:
        if 'pin' in auth:
            user = 'pritunl'
            if not password:
                password = popup("Enter the PIN: ", True)
                if auth == 'otp_pin':
                    password += popup("Enter the OTP code: ", True)
        if not user:
            user = popup("Enter the username: ")
        if user and not password and auth == 'creds':
            password = popup("Enter the password: ", True)
        
    pt.connectProfile(profile(pt, id), user=user, password=password)
    notify('Connecting to "{}"'.format(pt.profiles[prof]['name']))

def popup(msg, pwd=False):
    if msg:
        hidden = 'with hidden answer' if pwd else ''
        command = 'Tell application "System Events" to display dialog "{}" default answer "" {}'.format(msg, hidden)
        stdout, stderr = Popen(['osascript'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(command)
        if not stderr and stdout:
            p = stdout.split(':')
            return p[2].strip()

if __name__ == u"__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))