#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=utf-8
# run as root

'''
 This plugin allows to config latch settings in some UNIX systems (like Linux)
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


import easygui as eg
import sys
import os

from latchHelper import *


 
secret_key = getConfigParameter("secret_key");
app_id = getConfigParameter("app_id");

if app_id == None or secret_key == None:
    print("Can't read config file");
    exit();

msg = "Identify your application"
title = PLUGIN_NAME + " settings"
fieldNames = ["Application ID","Secret key"]
fieldValues = [app_id, secret_key]  # we start with blanks for the values
fieldValues = eg.multenterbox(msg,title, fieldNames, fieldValues)
 
# make sure that none of the fields was left blank
while 1:
    if fieldValues == None: break
    errmsg = ""
    for i in range(len(fieldNames)):
        if fieldValues[i].strip() == "":
            errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "":
        replaceConfigParameters(fieldValues[0], fieldValues[1])
        secret_key = fieldValues[1]
        app_id = fieldValues[0]
        break # no problems found
    fieldValues = eg.multenterbox(errmsg, title, fieldNames, fieldValues)




