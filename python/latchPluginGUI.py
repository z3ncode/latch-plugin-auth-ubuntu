#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set fileencoding=utf-8
# run as root

'''
 This plugin allows to pair and upair our application with Latch in some UNIX systems (like Linux)
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
import urllib.request
import latch

from latchHelper import *



def pair_gui():

    secret_key = getConfigParameter("secret_key")
    app_id = getConfigParameter("app_id")

    if app_id == None or secret_key == None:
        print("Can't read config file")
        exit();

    api = latch.Latch(app_id, secret_key)
    latch.Latch.set_host(LATCH_HOST)

    reply = eg.enterbox(msg='Token', title='Pair', default='', strip=True, image=None, root=None);
    if reply == None:
        exit()

    if reply == "":
        eg.msgbox(msg="You didn't put a token",title='Error')
        return

    if len(reply) != 6:
        eg.msgbox(msg="Token not found",title='Error')
        return

    token = urllib.request.pathname2url(reply)
    try:
        res = api.pair(token)
    except:
        eg.msgbox(msg="Some exception happened",title='Error')
        return

    responseData = res.get_data();
    responseError = res.get_error();

    if 'accountId' in responseData:
        user = os.getlogin()
        accountId = responseData["accountId"]
        addAccount(user, accountId)
        eg.msgbox(msg='Paired',title='Pair');
    elif responseError != "":
        title_error = 'Error - ' + str(responseError.get_code())
        if responseError.get_message() == 'Invalid application signature':
            eg.msgbox(msg="Settings error: Bad secret key or application id",title=title_error)
        else:
            eg.msgbox(msg=responseError.get_message(),title=title_error)
        

def unpair_gui():

    secret_key = getConfigParameter("secret_key");
    app_id = getConfigParameter("app_id");

    if app_id == None or secret_key == None:
        print("Can't read config file");
        exit();

    api = latch.Latch(app_id, secret_key);
    latch.Latch.set_host(LATCH_HOST)
    
    user = os.getlogin()
    accountId = getAccountId(user)
    if accountId == None:
        eg.msgbox(msg="Can't read latch_accounts file",title='Error')
        return;

    accountIdUrl = urllib.request.pathname2url(accountId)
    try:
        res = api.unpair(accountIdUrl)
    except:
        eg.msgbox(msg="Some exception happened",title='Error')
        return

    responseError = res.get_error()

    if responseError != "" and responseError.get_message() != 'Account not paired':
        title_error = 'Error - ' + str(responseError.get_code())
        if responseError.get_message() == 'Invalid application signature':
            eg.msgbox(msg="Settings error: Bad secret key or application id",title=title_error)
        else:
            eg.msgbox(msg=responseError.get_message(),title=title_error)
    else:
        deleteAccount(accountId)
        eg.msgbox(msg='Unpaired',title='Unpair')




operations = ["Pair","Unpair","Exit"]
user = os.getlogin()

while 1:
    if isPair(user):
        operations = ["Unpair","Exit"]
    else:
        operations = ["Pair","Exit"]

    reply = eg.buttonbox(msg='Operation', title=PLUGIN_NAME,image=None, choices=operations)

    if reply == "Pair":
        pair_gui()
    elif reply == "Unpair":
        unpair_gui()
    elif reply == "Exit":
        exit();

