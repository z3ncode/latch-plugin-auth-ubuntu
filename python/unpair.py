#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=utf-8
# Run as root

'''
 This script allows to unpair our application in some UNIX systems (like Linux)
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
import latch

from latchHelper import *



if len(sys.argv) == 3 and sys.argv[1] == "-f":
    secret_key = getConfigParameter("secret_key", sys.argv[2])
    app_id = getConfigParameter("app_id", sys.argv[2])
    if app_id == None or secret_key == None:
        print("Can't read config file");
        exit()

    replaceConfigParameters(app_id, secret_key)
elif len(sys.argv) != 1:
    print("use 'unpair.py [ -f <file.conf> ]'");
    exit();

secret_key = getConfigParameter("secret_key");
app_id = getConfigParameter("app_id");

if app_id == None or secret_key == None:
    print("Can't read config file");
    exit();

user = os.getlogin()
accountId = getAccountId(user);
if accountId == None:
    print("User '" + user + "' not paired");
    exit();

api = latch.Latch(app_id, secret_key);
latch.Latch.set_host(LATCH_HOST);

try:
    res = api.unpair(accountId);
except:
    print("Error: Some exception happened")
    exit()

responseError = res.get_error();

if responseError != "" and responseError.get_message() != 'Account not paired':
    if responseError.get_message() == 'Invalid application signature':
        print("Settings error: Bad secret key or application id")
    else:
        print(responseError.get_message())
else:
    deleteAccount(accountId)
    print("Unpaired");
