#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set fileencoding=utf-8
# Run as root

'''
 This script allows to pair our application with Latch in some UNIX systems (like Linux)
 Copyright (C) 2013 Eleven Paths

 This library is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 2.1 of the License, or (at your option) any later version.
 
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public
 License along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
'''


import sys
import os
import urllib.request
import latch

from latchHelper import *


if len(sys.argv) == 4 and sys.argv[2] == "-f":
    secret_key = getConfigParameter("secret_key", sys.argv[3])
    app_id = getConfigParameter("app_id", sys.argv[3])
    if app_id == None or secret_key == None:
        print("Can't read config file");
        exit()

    replaceConfigParameters(app_id, secret_key)

elif len(sys.argv) != 2:
    print("use 'pair.py <TOKEN> [ -f <file.conf> ]'");
    exit();

secret_key = getConfigParameter("secret_key");
app_id = getConfigParameter("app_id");

if app_id == None or secret_key == None:
    print("Can't read config file");
    exit()

user = os.getlogin()
if isPair(user):
    print("User '"+ user + "' is already paired")
    exit()

api = latch.Latch(app_id, secret_key)
latch.Latch.set_host(LATCH_HOST)

reply = sys.argv[1]

if len(reply) != 6:
    print("Token not found")
    exit()

token = urllib.request.pathname2url(reply);
try:
    res = api.pair(token)
except:
    print("Error: Some exception happened")
    exit()

responseData = res.get_data()
responseError = res.get_error()

if 'accountId' in responseData:
    accountId = responseData["accountId"] 
    addAccount(user, accountId)   
    print("Paired");
elif responseError != "":
    title_error = 'Error - ' + str(responseError.get_code())
    if responseError.get_message() == 'Invalid application signature':
        print("Settings error: Bad secret key or application id")
    else:
        print(responseError.get_message())
