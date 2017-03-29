#!/usr/bin/env python3

# __PROGRAM_NAME__ __PROGRAM_VERSION__
#
# __PROGRAM_COPYRIGHT__ __PROGRAM_AUTHOR__ __PROGRAM_AUTHOR_EMAIL__
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Checks mail for incoming messages.

If some mail has come it prints number of messages in the box and some
their headers like sender address and subject.

"""

__version__ = '__PROGRAM_VERSION_NO_V__'
__date__ = '__PROGRAM_DATE__'
__author__ = '__PROGRAM_AUTHOR__ __PROGRAM_AUTHOR_EMAIL__'
__license__ = 'GNU GPLv3'


PROG = '__PROGRAM_NAME__'
VERSION = '__PROGRAM_VERSION__'

import sys
import argparse
import os
import csv
import math
import getpass
import hashlib
import Crypto.Cipher.AES
import base64
import poplib
import email.header
import socket
import re


class ProgError(Exception):
    pass


class ProgMessage(Exception):
    pass


class MenuCtrlDMsg(ProgMessage):
    pass


class MenuCtrlCMsg(ProgMessage):
    pass


class CheckEmptyBoxMsg(ProgMessage):
    pass


class CheckIncorrectMsgRange(ProgError):
    pass


class LastNoCheckYet(ProgMessage):
    pass


class LastEmptyBoxMsg(ProgMessage):
    pass


class AccFileNoFileError(ProgError):
    pass


class AccFileNotFileError(ProgError):
    pass


class AccFileFieldsError(ProgError):
    pass


class InputNumNone(ProgError):
    pass


class InputNumError(ProgError):
    pass


class InputNumRangeError(ProgError):
    pass


class PswDecryptError(ProgError):
    pass


class CheckAccEmptyError(ProgError):
    pass


class ConnectionRangeError(ProgError):
    pass


class Pop3ConnectServerError(ProgError):
    pass


class Pop3ConnectPortError(ProgError):
    pass


class Pop3ConnectTimeoutError(ProgError):
    pass


class Pop3LoginError(ProgError):
    pass


class Pop3LoginTimeoutError(ProgError):
    pass


class Pop3TopTimeoutError(ProgError):
    pass


class Pop3CantDecodeHeaders(ProgError):
    pass


class SaveAccEmptyError(ProgError):
    pass


class ModeMessageRangeRangeError(ProgError):
    pass


class MailChecker:

    def __init__(self, prog, version, conflst):
        # дано    : имя программы, версия и список параметров
        #           для AccFileHandler
        # получить: имя программы, версия и разделённый список
        #           параметров сохранены; создан AccFileHandler
        self._prog = prog
        self._version = version
        (self._confname,
         self._confenc,
         self._confcmnt,
         self._confsep,
         self._confnfld,
         self._confpsw,
         self._confpswhlen) = conflst
        self._afh = AccFileHandler(self._prog, self._version,
                                   self._confname, self._confenc,
                                   self._confcmnt, self._confsep,
                                   self._confnfld,
                                   self._confpsw, self._confpswhlen)

    def start(self):
        # дано    : AccFileHandler выключен
        # получить: AccFileHandler включён
        self._afh.start()

    def checkmail_menu(self):
        # дано    : имя программы, версия и AccFileHandler
        # получить: почта проверена с помощью меню, которое
        #           выводит заголовок с именем программы и версией
        #           и может загружать учётные записи из файла
        mh = MenuHandler(self._prog, self._version, self._afh)
        mh.start()
        mh.run()
        mh.end()

    def end(self):
        # дано    : AccFileHandler включён
        # получить: AccFileHandler выключен
        self._afh.end()


class MenuHandler:

    def __init__(self, prog, version, conf):
        # дано    : имя программы, версия и AccFileHandler
        # получить: имя программы, версия и AccFileHandler сохранены;
        #           составлен заголовок меню, установлена
        #           статусная строка, создан AccountHandler;
        #           установлено время ожидания в секундах,
        #           размер страницы и ширина номера записи
        #           для учётных записей и пар адрес-тема
        self._prog = prog
        self._version = version
        self._afh = conf
        self._header = '{0} {1}'.format(self._prog, self._version)
        self._status = ''
        self._ah = AccountHandler()
        self._mh = ModesHandler()
        self._pop3_timeout = 20
        self._accv_psize = 5
        self._accv_nwidth = 8
        self._msgv_psize = 5
        self._msgv_nwidth = 4
        self._last_check_lst = None

    def start(self):
        # дано    : AccountHandler и ModesHandler выключены
        # получить: AccountHandler и ModesHandler включёны
        self._ah.start()
        self._mh.start()

    def run(self):
        # дано    : статусная строка
        # получить: выполнены переходы по пунктам меню
        #           с изменением статусной строки
        state = 'main'
        while True:
            if state == 'main':
                try:
                    retval = self._main()
                except MenuCtrlDMsg:
                    state = 'quit'
                    continue
                if retval == '1':
                    self._status = ''
                    state = 'set_config'
                elif retval == '2':
                    self._status = ''
                    state = 'check_mail'
                elif retval == '3':
                    self._status = ''
                    state = 'show_last_check'
                elif retval == 'q':
                    state = 'quit'

            elif state == 'set_config':
                try:
                    retval = self._set_config()
                except MenuCtrlDMsg:
                    self._status = 'Set config: returned (Ctrl + D)'
                    state = 'main'
                    continue
                if retval == '1':
                    self._status = ''
                    state = 'set_account'
                elif retval == '2':
                    self._status = ''
                    state = 'set_modes'
                elif retval == 'b':
                    self._status = 'Set config: returned'
                    state = 'main'

            elif state == 'set_account':
                try:
                    retval = self._setacc()
                except MenuCtrlDMsg:
                    self._status = 'Set account: returned (Ctrl + D)'
                    state = 'set_config'
                    continue
                if retval == '1':
                    self._status = ''
                    state = 'config_file'
                elif retval == '2':
                    self._status = ''
                    state = 'interactive'
                elif retval == 'b':
                    self._status = 'Set account: returned'
                    state = 'set_config'

            elif state == 'interactive':
                try:
                    retval = self._interact()
                except MenuCtrlDMsg:
                    self._status = 'Interactive: returned (Ctrl + D)'
                    state = 'set_account'
                    continue
                if retval == '1':
                    state = 'inter_name'
                elif retval == '2':
                    state = 'inter_server'
                elif retval == '3':
                    state = 'inter_port'
                elif retval == '4':
                    state = 'inter_user'
                elif retval == '5':
                    state = 'inter_password'
                elif retval == 's':
                    state = 'inter_show'
                elif retval == 'c':
                    state = 'inter_clear'
                elif retval == 'b':
                    self._status = 'Interactive: returned'
                    state = 'set_account'

            elif state == 'inter_name':
                try:
                    self._inter_name()
                except MenuCtrlDMsg:
                    self._status = 'Name: cancel (Ctrl + D)'
                    state = 'interactive'
                    continue
                self._status = 'Name - OK'
                state = 'interactive'

            elif state == 'inter_server':
                try:
                    self._inter_server()
                except MenuCtrlDMsg:
                    self._status = 'Server: cancel (Ctrl + D)'
                    state = 'interactive'
                    continue
                self._status = 'Server - OK'
                state = 'interactive'

            elif state == 'inter_port':
                try:
                    self._inter_port()
                except MenuCtrlDMsg:
                    self._status = 'Port: cancel (Ctrl + D)'
                    state = 'interactive'
                    continue
                except InputNumError:
                    self._status = 'Port: not a number - FAIL'
                    state = 'interactive'
                    continue
                except InputNumRangeError:
                    self._status = 'Port: wrong range - FAIL'
                    state = 'interactive'
                    continue
                self._status = 'Port - OK'
                state = 'interactive'

            elif state == 'inter_user':
                try:
                    self._inter_user()
                except MenuCtrlDMsg:
                    self._status = 'User: cancel (Ctrl + D)'
                    state = 'interactive'
                    continue
                self._status = 'User - OK'
                state = 'interactive'

            elif state == 'inter_password':
                try:
                    self._inter_password()
                except MenuCtrlDMsg:
                    self._status = 'Password: cancel (Ctrl + D)'
                    state = 'interactive'
                    continue
                self._status = 'Password - OK'
                state = 'interactive'

            elif state == 'inter_show':
                try:
                    self._inter_show()
                except MenuCtrlDMsg:
                    self._status = 'Show: cancel (Ctrl + D)'
                    state = 'interactive'
                    continue
                self._status = 'Show - OK'
                state = 'interactive'

            elif state == 'inter_clear':
                self._inter_clear()
                self._status = 'Clear - OK'
                state = 'interactive'

            elif state == 'config_file':
                try:
                    retval = self._conffile()
                except MenuCtrlDMsg:
                    self._status = 'Config file: returned (Ctrl + D)'
                    state = 'set_account'
                    continue
                if retval == '1':
                    self._status = ''
                    state = 'load_account'
                elif retval == '2':
                    self._status = ''
                    state = 'save_account'
                elif retval == 'b':
                    self._status = 'Config file: returned'
                    state = 'set_account'

            elif state == 'load_account':
                try:
                    retval = self._loadacc()
                except MenuCtrlDMsg:
                    self._status = 'Load account: returned (Ctrl + D)'
                    state = 'config_file'
                    continue
                if retval == '1':
                    self._status = ''
                    state = 'load_account_view'
                elif retval == '2':
                    self._status = ''
                    state = 'load_account_select'
                elif retval == 's':
                    self._status = ''
                    state = 'load_account_show'
                elif retval == 'b':
                    self._status = 'Load account: returned'
                    state = 'config_file'

            elif state == 'load_account_view':
                try:
                    retval = self._loadacc_view()
                except MenuCtrlDMsg:
                    self._status = 'Load account: cancel (Ctrl + D)'
                    state = 'load_account'
                    continue
                except AccFileNoFileError:
                    self._status = 'Load account: no file - FAIL'
                    state = 'load_account'
                    continue
                except AccFileNotFileError:
                    self._status = 'Load account: is not a file - FAIL'
                    state = 'load_account'
                    continue
                except AccFileFieldsError:
                    self._status = 'Load account: incorrect account - FAIL'
                    state = 'load_account'
                    continue
                self._status = 'View - OK'
                state = 'load_account'

            elif state == 'load_account_select':
                try:
                    self._loadacc_select()
                except MenuCtrlDMsg:
                    self._status = 'Select: cancel (Ctrl + D)'
                    state = 'load_account'
                    continue
                except AccFileNoFileError:
                    self._status = 'Select: no file - FAIL'
                    state = 'load_account'
                    continue
                except AccFileNotFileError:
                    self._status = 'Select: is not a file - FAIL'
                    state = 'load_account'
                    continue
                except AccFileFieldsError:
                    self._status = 'Select: incorrect account - FAIL'
                    state = 'load_account'
                    continue
                except InputNumNone:
                    self._status = 'Select: empty number - FAIL'
                    state = 'load_account'
                    continue
                except InputNumError:
                    self._status = 'Select: not a number - FAIL'
                    state = 'load_account'
                    continue
                except InputNumRangeError:
                    self._status = 'Select: wrong range - FAIL'
                    state = 'load_account'
                    continue
                except PswDecryptError:
                    self._status = 'Select: wrong password - FAIL'
                    state = 'load_account'
                    continue
                self._status = 'Select: {0} - OK'.format(self._ah.get_name())
                state = 'load_account'

            elif state == 'load_account_show':
                try:
                    self._loadacc_show()
                except MenuCtrlDMsg:
                    self._status = 'Show: cancel (Ctrl + D)'
                    state = 'load_account'
                    continue
                self._status = 'Show - OK'
                state = 'load_account'

            elif state == 'save_account':
                try:
                    self._saveacc()
                except MenuCtrlDMsg:
                    self._status = 'Save account: cancel (Ctrl + D)'
                    state = 'config_file'
                    continue
                except SaveAccEmptyError:
                    self._status = 'Save account: account is empty - FAIL'
                    state = 'config_file'
                    continue
                self._status = 'Save account - OK'
                state = 'config_file'

            elif state == 'set_modes':
                try:
                    retval = self._set_modes()
                except MenuCtrlDMsg:
                    self._status = 'Set modes: returned (Ctrl + D)'
                    state = 'set_config'
                    continue
                if retval == '1':
                    self._status = ''
                    state = 'set_mode_message_range'
                elif retval == 's':
                    self._status = ''
                    state = 'set_modes_show'
                elif retval == 'b':
                    self._status = 'Set modes: returned'
                    state = 'set_config'

            elif state == 'set_mode_message_range':
                try:
                    self._set_mode_message_range()
                except MenuCtrlDMsg:
                    self._status = 'Message range: returned (Ctrl + D)'
                    state = 'set_modes'
                    continue
                except InputNumError:
                    self._status = 'Message range: not a number - FAIL'
                    state = 'set_modes'
                    continue
                except InputNumRangeError:
                    self._status = 'Message range: wrong number - FAIL'
                    state = 'set_modes'
                    continue
                except ModeMessageRangeRangeError:
                    self._status = 'Message range: wrong range - FAIL'
                    state = 'set_modes'
                    continue
                self._status = 'Range - OK'
                state = 'set_modes'

            elif state == 'set_modes_show':
                try:
                    self._set_modes_show()
                except MenuCtrlDMsg:
                    self._status = 'Show: cancel (Ctrl + D)'
                    state = 'set_modes'
                    continue
                self._status = 'Show - OK'
                state = 'set_modes'

            elif state == 'check_mail':
                try:
                    print('Press Ctrl + C for cancel...')
                    self._checkmail()
                except MenuCtrlCMsg:
                    self._status = 'Check mail: cancel (Ctrl + C)'
                    state = 'main'
                    continue
                except MenuCtrlDMsg:
                    self._status = 'Check mail: cancel (Ctrl + D)'
                    state = 'main'
                    continue
                except CheckEmptyBoxMsg:
                    self._status = 'Check mail: no messages - OK'
                    state = 'main'
                    continue
                except CheckIncorrectMsgRange:
                    self._status = 'Check mail: range is greater than box' \
                                   ' - FAIL'
                    state = 'main'
                    continue
                except CheckAccEmptyError:
                    self._status = 'Check mail: empty field in account - FAIL'
                    state = 'main'
                    continue
                except Pop3ConnectServerError:
                    self._status = 'Check mail: can\'t connect to server' \
                                   ' - FAIL'
                    state = 'main'
                    continue
                except Pop3ConnectPortError:
                    self._status = 'Check mail: can\'t connect to port - FAIL'
                    state = 'main'
                    continue
                except Pop3ConnectTimeoutError:
                    self._status = 'Check mail: can\'t connect by timeout' \
                                   ' - FAIL'
                    state = 'main'
                    continue
                except Pop3LoginError:
                    self._status = 'Check mail: can\'t login - FAIL'
                    state = 'main'
                    continue
                except Pop3LoginTimeoutError:
                    self._status = 'Check mail: can\'t login by timeout - FAIL'
                    state = 'main'
                    continue
                except Pop3TopTimeoutError:
                    self._status = 'Check mail: can\'t receive a message by ' \
                                   'timeout - FAIL'
                    state = 'main'
                    continue
                self._status = 'Check mail - OK'
                state = 'main'

            elif state == 'show_last_check':
                try:
                    self._show_last_check()
                except MenuCtrlDMsg:
                    self._status = 'Show last: cancel (Ctrl + D)'
                    state = 'main'
                    continue
                except LastNoCheckYet:
                    self._status = 'Show last: not checked yet - OK'
                    state = 'main'
                    continue
                except LastEmptyBoxMsg:
                    self._status = 'Show last: no messages - OK'
                    state = 'main'
                    continue
                self._status = 'Show last - OK'
                state = 'main'

            elif state == 'quit':
                print('Bye')
                break

    def _main(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "главное",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu'
        account_name = self._ah.get_name()
        account_part = ' ({})'.format(account_name) if account_name else ''
        items = (('1', 'Set config'),
                 ('2', 'Check mail' + account_part),
                 ('3', 'Show last'),
                 ('q', 'Quit'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _set_config(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "установить конфигурацию",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu -> Set config'
        items = (('1', 'Set account'),
                 ('2', 'Set modes'),
                 ('b', 'Back'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _setacc(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "установить учётную запись",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu -> Set config -> Set account'
        items = (('1', 'Config file'),
                 ('2', 'Interactive'),
                 ('b', 'Back'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _interact(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "установить интерактивно",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu -> Set config -> Set account -> Interactive'
        items = (('1', 'Name'),
                 ('2', 'Server'),
                 ('3', 'Port'),
                 ('4', 'User'),
                 ('5', 'Password'),
                 ('s', 'Show'),
                 ('c', 'Clear'),
                 ('b', 'Back'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _inter_name(self):
        # дано    : AccountHandler включён
        # получить: в AccountHandler сохранено/удалено имя
        #           учётной записи, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        ih = InputHandler()
        ih.start()
        try:
            res = ih.input_string('Name: ')
            if res:
                self._ah.set(name=res)
            else:
                self._ah.unset(name=True)
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _inter_server(self):
        # дано    : AccountHandler включён
        # получить: в AccountHandler сохранён/удалён сервер,
        #           либо при нажатии Ctrd + D возникло
        #           MenuCtrlDMsg
        ih = InputHandler()
        ih.start()
        try:
            res = ih.input_string('Server: ')
            if res:
                self._ah.set(server=res)
            else:
                self._ah.unset(server=True)
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _inter_port(self):
        # дано    : AccountHandler включён
        # получить: в AccountHandler сохранён/удалён порт,
        #           при нажатии Ctrd + D возникло MenuCtrlDMsg;
        #           если порт - не число, возникло InputNumError,
        #           если порт не входит в диапазон, возникло
        #           InputNumRangeError
        ih = InputHandler()
        ih.start()
        try:
            port_number = ih.input_number(1, 65535, 'Port: ')
            self._ah.set(port=str(port_number))
        except InputNumNone:
            self._ah.unset(port=True)
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _inter_user(self):
        # дано    : AccountHandler включён
        # получить: в AccountHandler сохранено/удалено имя
        #           пользователя, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        ih = InputHandler()
        ih.start()
        try:
            res = ih.input_string('User: ')
            if res:
                self._ah.set(user=res)
            else:
                self._ah.unset(user=True)
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _inter_password(self):
        # дано    : AccountHandler включён
        # получить: в AccountHandler сохранён/удалён пароль,
        #           либо при нажатии Ctrd + D возникло
        #           MenuCtrlDMsg
        ih = InputHandler()
        ih.start()
        try:
            res = ih.input_password('Password: ')
            if res:
                self._ah.set(password=res)
            else:
                self._ah.unset(password=True)
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _inter_show(self):
        # дано    : AccountHandler включён
        # получить: на экран выведены отформатированные поля
        #           учётной записи, либо при нажатии Ctrl + D
        #           возникло MenuCtrlDMsg
        fmt = '    Name: {0:20}\n' \
              '  Server: {1:20}     Port: {2}\n' \
              '    User: {3:20} Password: {4}\n'
        name, server, port, user, password = (
            self._ah.get_name(),
            self._ah.get_server(),
            self._ah.get_port(),
            self._ah.get_user(),
            self._ah.get_password()
        )
        if name is not None:
            name = "'" + name + "'"
        if server is not None:
            server = "'" + server + "'"
        if port is not None:
            port = "'" + port + "'"
        if user is not None:
            user = "'" + user + "'"
        if password is not None:
            password = "'" + password + "'"
        print(fmt.format(name, server, port, user, password), end='')
        try:
            input()
        except EOFError:
            raise MenuCtrlDMsg

    def _inter_clear(self):
        # дано    : AccountHandler
        # получить: в AccFileHandler пустая учётная запись
        self._ah.end()
        self._ah.start()

    def _conffile(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "установить из файла",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu -> Set config -> Set account -> Config file'
        items = (('1', 'Load account'),
                 ('2', 'Save account'),
                 ('b', 'Back'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _loadacc(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "из файла загрузить",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu -> Set config -> Set account -> Config file -> Load'
        items = (('1', 'View'),
                 ('2', 'Select'),
                 ('s', 'Show'),
                 ('b', 'Back'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _loadacc_view(self):
        # дано    : заголовок, AccFileHandler, размер страницы
        #           и ширина номера записи
        # получить: на экран постранично выведены пронумерованные
        #           учётные записи;
        #           если нажато Ctrl + D, то возникло MenuCtrlDMsg
        header = '\n  {0}\n'.format(self._header)
        message = 'press any key...\n'
        avh = AccViewerHandler()
        avh.start(header, self._accv_psize, self._accv_nwidth, message)
        try:
            account_list = [(i[0], i[1], i[3])
                            for i in self._afh.load_accounts()]
            avh.print_pages(account_list)
        except EOFError:
            avh.end()
            print()
            raise MenuCtrlDMsg
        avh.end()

    def _loadacc_select(self):
        # дано    :
        # получить: введён номер учётной записи и пароль для
        #           расшифровки, в текущую учётную запись
        #           загружены поля выбранной учётной записи
        #           (с расшифрованным полем пароля);
        #           если номер или пароль введены неверно,
        #           то возникло соответствующее исключение;
        #           если нажато Ctrl + D, то возникло MenuCtrlDMsg
        accounts = self._afh.load_accounts()
        ih = InputHandler()
        ih.start(number_prompt='number: ', password_prompt='password: ')
        try:
            number = ih.input_number(1, len(accounts))
            account = accounts[number - 1]
            if account[4] is None:
                print('Empty password')
                input()
            else:
                password = ih.input_password()
                if password:
                    self._afh.decrypt_account(account, password)
                else:
                    self._afh.decrypt_account(account)
            self._ah.end()
            self._ah.start()
            if account[0]:
                self._ah.set(name=account[0])
            if account[1]:
                self._ah.set(server=account[1])
            if account[2]:
                self._ah.set(port=account[2])
            if account[3]:
                self._ah.set(user=account[3])
            if account[4]:
                self._ah.set(password=account[4])
            assert '' not in self._ah.get()
        except (InputNumError, InputNumRangeError,
                PswDecryptError):
            ih.end()
            print()
            raise
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _loadacc_show(self):
        # дано    : AccountHandler включён
        # получить: на экран выведены отформатированные поля
        #           учётной записи, пароль скрыт; либо при
        #           нажатии Ctrl + D возникло MenuCtrlDMsg
        fmt = '    Name: {0:20}\n' \
              '  Server: {1:20}     Port: {2}\n' \
              '    User: {3:20} Password: {4}\n'
        name, server, port, user, password = (
            self._ah.get_name(),
            self._ah.get_server(),
            self._ah.get_port(),
            self._ah.get_user(),
            self._ah.get_password()
        )
        if name is not None:
            name = "'" + name + "'"
        if server is not None:
            server = "'" + server + "'"
        if port is not None:
            port = "'" + port + "'"
        if user is not None:
            user = "'" + user + "'"
        if password is not None:
            password = "'" + '*' * 8 + "'"
        print(fmt.format(name, server, port, user, password), end='')
        try:
            input()
        except EOFError:
            raise MenuCtrlDMsg

    def _saveacc(self):
        # дано    : AccountHandler и AccFileHandler включены
        # получить: данные учётной записи сохранены в конце
        #           файла учётных записей;
        #           если учётная запись пуста, возникло
        #           SaveAccEmptyError
        if self._ah.is_empty():
            raise SaveAccEmptyError
        ih = InputHandler()
        ih.start()
        try:
            account = list(self._ah.get())
            accounts = self._afh.load_accounts()
            if account[4]:
                password = ih.input_password('password: ')
                if password:
                    self._afh.encrypt_account(account, password)
                else:
                    self._afh.encrypt_account(account)
            accounts.append(account)
            self._afh.save_accounts(accounts)
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()

    def _set_modes(self):
        # дано    : заголовок и статусная строка
        # получить: на экране отобразилось подменю "установить режимы",
        #           ответ = выбор пункта, либо при нажатии Ctrd + D
        #           возникло MenuCtrlDMsg
        name = 'Main menu -> Set config -> Set modes'
        items = (('1', 'Message range'),
                 ('s', 'Show modes'),
                 ('b', 'Back'))
        mih = MenuItemHandler(self._header,
                              name, items,
                              self._status)
        mih.start()
        mih.show()
        try:
            retval = mih.ask()
        except EOFError:
            mih.end()
            print()
            raise MenuCtrlDMsg
        mih.end()
        return retval

    def _set_mode_message_range(self):
        # дано    : ModesHandler включён
        # получить: в ModesHandler сохранён диапазон сообщений;
        #           при нажатии Ctrd + D возникло MenuCtrlDMsg;
        #           если начало или конец - не число, возникло InputNumError;
        #           если конец или начало не входит в диапазон, возникло
        #           InputNumRangeError
        ih = InputHandler()
        ih.start()
        try:
            start_number = ih.input_number(1, None, 'Start: ')
        except InputNumNone:
            start_number = None
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        try:
            end_number = ih.input_number(1, None, 'End: ')
        except InputNumNone:
            end_number = None
        except EOFError:
            ih.end()
            print()
            raise MenuCtrlDMsg
        ih.end()
        if start_number is None:
            self._mh.unset_range(start=True)
        if end_number is None:
            self._mh.unset_range(end=True)
        if start_number is None or \
           end_number is None or \
           start_number <= end_number:
            self._mh.set_range(start=start_number, end=end_number)
        else:
            raise ModeMessageRangeRangeError

    def _set_modes_show(self):
        # дано    :   ModesHandler включён
        # получить:   на экран выведен диапазон сообщений;
        #             либо при нажатии Ctrl + D возникло MenuCtrlDMsg
        fmt = 'Message range: from {} to {}\n'
        message_start = self._mh.get_range_start() or 'min'
        message_end = self._mh.get_range_end() or 'max'
        print(fmt.format(message_start, message_end), end='')
        try:
            input()
        except EOFError:
            raise MenuCtrlDMsg

    def _checkmail(self):
        # дано    : ModesHandler включён
        # получить: приняты пары адрес-тема и выведены на экран;
        #           при приёме или выводе может породиться исключение
        if not self._mh.is_enabled_range():
            addr_subj_lst = self._checkmail_load_no_range()
            self._checkmail_print_no_range(addr_subj_lst)
        else:
            start, end = self._mh.get_range()
            addr_subj_lst = self._checkmail_load_range(start, end)
            self._checkmail_print_range(addr_subj_lst)

    def _checkmail_load_no_range(self):
        # дано    : AccountHandler, ModesHandler, время ожидания
        #           в секундах
        # получить: создано соединение, приняты пары адрес-тема;
        #           если в учётной записи есть пустое поле или ящик пуст,
        #           то возникло исключение
        server, port, user, password = (
            self._ah.get_server(),
            self._ah.get_port(),
            self._ah.get_user(),
            self._ah.get_password()
        )
        if None in (server, port, user, password):
            raise CheckAccEmptyError
        ch = ConnectionHandler(server, port, user, password,
                               self._pop3_timeout)
        ch.start()
        try:
            addr_subj_lst = ch.get_pop3_addrsubj()
            self._last_check_lst = addr_subj_lst
            if not addr_subj_lst:
                raise CheckEmptyBoxMsg
        except KeyboardInterrupt:
            ch.end()
            print()
            raise MenuCtrlCMsg
        ch.end()
        return addr_subj_lst

    def _checkmail_print_no_range(self, addr_subj_lst):
        # дано    : список пар адрес-тема, заголовок, размер страницы
        #           и ширина номера записи
        # получить: пары адрес-тема пронумерованы и выведены на экран
        header = '\n  {0}\n'.format(self._header)
        message = 'press any key...\n'
        mvh = MsgViewerHandler(header, self._msgv_psize,
                               self._msgv_nwidth, message)
        mvh.start()
        try:
            mvh.print_pages_addrsubj(addr_subj_lst)
        except EOFError:
            mvh.end()
            print()
            raise MenuCtrlDMsg
        mvh.end()

    def _checkmail_load_range(self, start, end):
        # дано    : AccountHandler, ModesHandler, время ожидания в секундах,
        #           номер первой и номер последней пары адрес-тема
        # получить: создано соединение, приняты пары адрес-тема;
        #           если в учётной записи есть пустое поле, ящик пуст или
        #           диапазон начинается за ящиком, то возникло исключение
        server, port, user, password = (
            self._ah.get_server(),
            self._ah.get_port(),
            self._ah.get_user(),
            self._ah.get_password()
        )
        if None in (server, port, user, password):
            raise CheckAccEmptyError
        ch = ConnectionHandler(server, port, user, password,
                               self._pop3_timeout)
        ch.start()
        try:
            addr_subj_lst = ch.get_pop3_addrsubj_range(start, end)
            self._last_check_lst = addr_subj_lst
            if not addr_subj_lst:
                raise CheckEmptyBoxMsg
        except ConnectionRangeError:
            raise CheckIncorrectMsgRange
        except KeyboardInterrupt:
            ch.end()
            print()
            raise MenuCtrlCMsg
        ch.end()
        return addr_subj_lst

    def _checkmail_print_range(self, addr_subj_lst):
        # дано    : список пар адрес-тема, заголовок, размер страницы
        #           и ширина номера записи
        # получить: пары адрес-тема пронумерованы и выведены на экран
        header = '\n  {0}\n'.format(self._header)
        message = 'press any key...\n'
        mvh = MsgViewerHandler(header, self._msgv_psize,
                               self._msgv_nwidth, message)
        mvh.start()
        try:
            mvh.print_pages_addrsubj(addr_subj_lst)
        except EOFError:
            mvh.end()
            print()
            raise MenuCtrlDMsg
        mvh.end()

    def _show_last_check(self):
        # дано    : список сообщений из последней проверки
        # получить: список сообщений выведен на экран;
        #           если списка нет или он пуст, возникло исключение
        if self._last_check_lst is None:
            raise LastNoCheckYet
        if not self._last_check_lst:
            raise LastEmptyBoxMsg
        header = '\n  {0}\n'.format(self._header)
        message = 'press any key...\n'
        mvh = MsgViewerHandler(header, self._msgv_psize,
                               self._msgv_nwidth, message)
        mvh.start()
        try:
            mvh.print_pages_addrsubj(self._last_check_lst)
        except EOFError:
            mvh.end()
            print()
            raise MenuCtrlDMsg
        mvh.end()

    def end(self):
        # дано    : AccountHandler и ModesHandler включёны
        # получить: AccountHandler и ModesHandler выключены
        self._mh.end()
        self._ah.end()


class MenuItemHandler:

    def __init__(self, header, name, items, status):
        # дано    : заголовок, имя, элементы, статусная строка;
        #           элементы содержат номера и названия
        # получить: заголовок, имя, элементы, статусная строка сохранены
        self._header = header
        self._name = name
        self._items = items
        self._status = status

    def start(self):
        # дано    :
        # получить:
        pass

    def show(self):
        # дано    : заголовок, имя, элементы, статусная строка
        # получить: экран очищен, выведено подменю с заголовком,
        #           именем, элементами (номерами и названиями)
        #           и статусной строкой, если она не пустая;
        self._clear()
        print('\n  {0}'.format(self._header))
        print('\n  [ {0} ]\n'.format(self._name))
        for n, i in self._items:
            print('  {0:>2}) {1}'.format(n, i))
        if self._status:
            print('\n  * {0} *\n'.format(self._status))
        else:
            print('\n\n')

    def ask(self):
        # дано    :
        # получить: запрошено значение и возвращено
        try:
            reply = input('> ')
        except UnicodeDecodeError:
            # When input ф and press Ctrl+D three times
            # this error raises because of some bug in Python 3.3-3.5
            reply = None
        return reply

    def _clear(self):
        # дано    :
        # получить: экран очищен
        os.system('clear')

    def end(self):
        # дано    :
        # получить:
        pass


class AccViewerHandler:

    def __init__(self):
        self._header = None
        self._page_size = None
        self._number_width = None
        self._message = None

    def start(self, header, page_size, number_width, message):
        # дано    : заголовок, размер страницы,
        #           ширина номера записи и сообщение
        # получить: заголовок, размер страницы,
        #           ширина номера записи и сообщение сохранены
        self._header = header
        if page_size <= 0:
            raise ValueError('page size should be >0')
        self._page_size = page_size
        if number_width < 0:
            raise ValueError('number width should be >=0')
        self._number_width = number_width
        self._message = message

    def print_pages(self, accounts):
        # дано    : заголовок, размер страницы, ширина номера записи,
        #           сообщение и учётные записи
        # получить: на экран постранично выведены учётные записи
        #           в отформатированном виде;
        #           заголовок, тело страницы, сообщение
        accounts = tuple(accounts)

        fmt = ('{0:{width}d} {1}\n'
               '         {3} at {2}\n\n')
        empty = '\n' * len(fmt.splitlines())

        header = self._header
        page_size = self._page_size

        total_number_of_accounts = len(accounts)
        if total_number_of_accounts > 0:
            number_of_pages = math.ceil(
                total_number_of_accounts / page_size)
        else:
            number_of_pages = 1

        for i_nop in range(number_of_pages):

            self._clear()
            print(header)

            account_index = i_nop * page_size
            page_accounts = \
                accounts[account_index:account_index + page_size]
            number_of_page_accounts = len(page_accounts)

            for i_ps in range(page_size):
                if i_ps < number_of_page_accounts:
                    name, server, user = page_accounts[i_ps]
                    if name is None:
                        name = 'Unknown'
                    if server is not None:
                        server = '"' + server + '"'
                    if user is not None:
                        user = '"' + user + '"'
                    record = fmt.format(
                        account_index + i_ps + 1,
                        name,
                        server,
                        user,
                        width=self._number_width
                    )
                    record_line = record
                else:
                    record_line = empty
                print(record_line, end='')
            print()

            status_line = '  page {0}/{1} of {2}'.format(
                i_nop + 1,
                number_of_pages,
                total_number_of_accounts
            )
            print(status_line)

            print(self._message)
            input()

    def _clear(self):
        # дано    :
        # получить: экран очищен
        os.system('clear')

    def end(self):
        # дано    :
        # получить: заголовок, размер страницы,
        #           ширина номера записи и сообщение очищены
        self._header = self._page_size = None
        self._number_width = self._message = None


class AccFileHandler:

    def __init__(self, prog, version, confname,
                 encoding, cmntchar, delimiter, nfields,
                 password, pswhashlen):
        # дано    : имя программы, версия, имя файла учётных записей,
        #           кодировка файла, признак комментария, разделитель
        #           полей, количество полей учётной записи, пароль
        #           для шифрования, длина хеша шифруемого пароля
        # получить: имя программы, версия, имя файла учётных записей,
        #           кодировка файла, признак комментария, разделитель
        #           полей, количество полей учётной записи, пароль
        #           для шифрования и длина хеша шифруемого пароля
        #           сохранены;
        #           составлен неизменный комментарий с именем
        #           и версией программы, создан PasswordHandler,
        #           и сохранёны
        self._prog = prog
        self._version = version
        self._confname = confname
        self._encoding = encoding
        self._cmntchar = cmntchar
        self._delimiter = delimiter
        if nfields >= 0:
            self._nfields = nfields
        else:
            raise ValueError('Number of fields should be >= 0')
        self._pfn = 5
        self._password = password
        self._pswhashlen = pswhashlen
        self._immut_comment = \
            '{0} This is the config file of ' \
            '{1} {2}\n'.format(self._cmntchar,
                               self._prog, self._version)
        self._ph = PasswordHandler(self._password, self._pswhashlen)

    def start(self):
        # дано    : PasswordHandler выключен
        # получить: PasswordHandler включён
        self._ph.start()

    def load_accounts(self):
        # дано    : имя файла с учётными записями, кодировка файла,
        #           разделитель полей и количество полей учётной записи,
        #           признак комментария
        # получить: ответ = список учётных записей вида
        #           [поле1, поле2, ... ] либо пустой список;
        #           пустые поля представлены в виде None
        if not os.path.exists(self._confname):
            raise AccFileNoFileError
        elif not os.path.isfile(self._confname):
            raise AccFileNotFileError
        accounts = []

        def is_whitespace(row):
            if not row:
                return True
            if re.match(r'^\s+$', row[0]):
                return True
            if re.match(r'^\s*{}'.format(self._cmntchar), row[0]):
                return True
            return False

        with open(self._confname, encoding=self._encoding) as fin:
            reader = csv.reader(fin, delimiter=self._delimiter)
            for row in reader:
                if is_whitespace(row):
                    continue
                for i in range(len(row)):
                    if row[i] == '':
                        row[i] = None
                if len(row) != self._nfields:
                    raise AccFileFieldsError
                accounts.append(row)
        assert all(len(i) == self._nfields for i in accounts), \
            'wrong number of fields in account'
        return accounts

    def save_accounts(self, accounts):
        # дано    : имя файла с учётными записями, кодировка файла,
        #           неизменный комментарий, разделитель полей и
        #           количество полей учётной записи,
        #           список учётных записей вида [поле1, поле2, ... ]
        # получить: в файл сохранён неизменный комментарий и
        #           после него учётные записи из списка, либо пустота
        if not all(len(i) == self._nfields for i in accounts):
            raise AccFileFieldsError
        with open(self._confname, "w", encoding=self._encoding) as fout:
            print(self._immut_comment, file=fout)
            writer = csv.writer(fout, delimiter=self._delimiter,
                                lineterminator='\n')
            writer.writerows(accounts)

    def encrypt_account(self, account, password=None):
        # дано    : учётная запись и пароль
        # получить: пароль учётной записи зашифрован паролем
        #           (если он задан), либо паролем по умолчанию
        i = self._pfn - 1
        encrypted = self._ph.encrypt_sum(account[i], password)
        account[i] = self._ph.encode(encrypted)

    def decrypt_account(self, account, password=None):
        # дано    : учётная запись и пароль
        # получить: пароль учётной записи расшифрован паролем
        #           (если он задан), либо паролем по умолчанию
        i = self._pfn - 1
        decoded = self._ph.decode(account[i])
        account[i] = self._ph.decrypt_sum(decoded, password)

    def end(self):
        # дано    : PasswordHandler включён
        # получить: PasswordHandler выключен
        self._ph.end()


class InputHandler:

    def __init__(self):
        # дано    :
        # получить:
        self._number_prompt = None
        self._password_prompt = None
        self._string_prompt = None

    def start(self,
              number_prompt=None,
              password_prompt=None,
              string_prompt=None):
        # дано    : приглашения числа, пароля, строки
        # получить: приглашения числа, пароля, строки сохранены
        if number_prompt is not None:
            self._number_prompt = number_prompt
        else:
            self._number_prompt = ''
        if password_prompt is not None:
            self._password_prompt = password_prompt
        else:
            self._password_prompt = ''
        if string_prompt is not None:
            self._string_prompt = string_prompt
        else:
            self._string_prompt = ''

    def input_number(self,
                     number_min=None,
                     number_max=None,
                     prompt=None):
        # дано    : минимальное число, максимальное число и
        #           приглашение числа
        # получить: ответ = введённое число;
        #           возникло InputNumNone, если ничего не введено;
        #           возникло InputNumError, если введено не число;
        #           возникло InputNumRangeError, если число за пределами
        #           диапазона
        try:
            if prompt is not None:
                res = input(prompt)
            else:
                res = input(self._number_prompt)
            if not res:
                raise InputNumNone
            number = int(res)
            if number_min is not None and number < number_min:
                raise InputNumRangeError
            if number_max is not None and number > number_max:
                raise InputNumRangeError
        except ValueError:
            raise InputNumError
        return number

    def input_password(self, prompt=None):
        # дано    : приглашение пароля
        # получить: ответ = введённая строка пароля
        if prompt is not None:
            res = getpass.getpass(prompt)
        else:
            res = getpass.getpass(self._password_prompt)
        return res

    def input_string(self, prompt=None):
        # дано    : приглашение строки
        # получить: ответ = введённая строка
        if prompt is not None:
            res = input(prompt)
        else:
            res = input(self._string_prompt)
        return res

    def end(self):
        # дано    :
        # получить:
        self._number_prompt = None
        self._password_prompt = None
        self._string_prompt = None


class PasswordHandler:

    def __init__(self, defpassword, hashlen):
        # дано    : пароль по умолчанию и длина хеша
        # получить: пароль по умолчанию и длина хеша сохранёны
        self._defpassword = defpassword
        self._hashlen = hashlen
        if not 0 <= hashlen <= 32:
            raise ValueError('hash length should be in '
                             '[{};{}]'.format(0, 32))

    def start(self):
        # дано    :
        # получить:
        pass

    def encrypt_sum(self, s, password=None):
        # дано    : строка, пароль, пароль по умолчанию, длина хеша
        # получить: ответ = строка, зашифрованная паролем (если он задан),
        #           либо паролем по умолчанию; к незашифрованной строке
        #           слева дописан её md5-хеш заданной длины
        if password is None:
            password = self._defpassword
        md5hash = hashlib.md5(s.encode('utf-8')).hexdigest()
        cs = self._aes_encrypt(md5hash[:self._hashlen] + s, password)
        return cs

    def decrypt_sum(self, s, password=None):
        # дано    : строка, пароль, пароль по умолчанию, длина хеша
        # получить: ответ = строка, расшифрованная паролем (если он задан),
        #           либо паролем по умолчанию;
        #           либо возникло PswDecryptError, если md5-хеш заданной
        #           длины, стоящий слева от строки, не совпал с её хешем
        hashlen = self._hashlen
        if password is None:
            password = self._defpassword
        try:
            csum_ds = self._aes_decrypt(s, password)
        except UnicodeDecodeError:
            raise PswDecryptError
        csum, ds = csum_ds[:hashlen], csum_ds[hashlen:]
        md5hash = hashlib.md5(ds.encode('utf-8')).hexdigest()
        if not md5hash.startswith(csum):
            raise PswDecryptError
        return ds

    def encode(self, s):
        # дано    : строка
        # получить: ответ = строка, закодированная в base64
        b = s.encode('latin1')
        eb = base64.b64encode(b)
        es = eb.decode('latin1')
        return es

    def decode(self, s):
        # дано    : строка в base64
        # получить: ответ = строка, раскодированная из base64
        b = s.encode('latin1')
        db = base64.b64decode(b)
        ds = db.decode('latin1')
        return ds

    def _aes_encrypt(self, s, p):
        # дано    : строка и пароль
        # получить: ответ = строка, зашифрованная с помощью
        #           aes-ecb по паролю
        cryptor = AesCryptor()
        e = cryptor.encrypt(s, p)
        return e

    def _aes_decrypt(self, s, p):
        # дано    : зашифрованная в aes-ecb строка и пароль
        # получить: ответ = строка, расшифрованная с помощью
        #           пароля
        cryptor = AesCryptor()
        d = cryptor.decrypt(s, p)
        return d

    def end(self):
        # дано    :
        # получить:
        pass


class AesCryptor:

    """Simple encryptor/decryptor in aes-ecb mode"""

    def __init__(self):
        pass

    @staticmethod
    def _align(b, n):
        """Align byte sequence by zeros to blocks of some length."""
        if len(b) == n:
            return b
        else:
            return b + bytes(n - len(b) % n)

    def encrypt(self, s, p):
        """Encrypt plain string with password."""
        bs = s.encode('utf-8')
        bp = p.encode('utf-8')
        c = Crypto.Cipher.AES.new(self._align(bp, 16))
        be = c.encrypt(self._align(bs, 16))
        e = be.decode('latin1')
        return e

    def decrypt(self, s, p):
        """Decrypt crypted string with password."""
        bs = s.encode('latin1')
        bp = p.encode('utf-8')
        c = Crypto.Cipher.AES.new(self._align(bp, 16))
        bd = c.decrypt(bs)
        d = bd.rstrip(b'\x00').decode('utf-8')
        return d


class AccountHandler:

    def __init__(self):
        # дано    :
        # получить: создана учётная запись
        self._account = None

    def start(self):
        # дано    :
        # получить: учётная запись пуста
        self._account = {'name': None,
                         'server': None,
                         'port': None,
                         'user': None,
                         'password': None}

    def set(self,
            name=None, server=None, port=None,
            user=None, password=None):
        # дано    : учётная запись и поля (любое поле может отсутствовать)
        # получить: в учётной записи установлены заданные поля
        if name is not None:
            self._account['name'] = name
        if server is not None:
            self._account['server'] = server
        if port is not None:
            self._account['port'] = port
        if user is not None:
            self._account['user'] = user
        if password is not None:
            self._account['password'] = password

    def unset(self,
              name=False,
              server=False, port=False,
              user=False, password=False):
        # дано    : учётная запись и поля вида True/False
        # получить: в учётной записи истинные поля сделаны пустыми
        if name:
            self._account['name'] = None
        if server:
            self._account['server'] = None
        if port:
            self._account['port'] = None
        if user:
            self._account['user'] = None
        if password:
            self._account['password'] = None

    def get(self):
        # дано    : учётная запись
        # получить: ответ = (имя, сервер, порт, пользователь, пароль)
        return (self._account['name'], self._account['server'],
                self._account['port'], self._account['user'],
                self._account['password'])

    def get_name(self):
        # дано    : учётная запись
        # получить:
        return self._account['name']

    def get_server(self):
        # дано    : учётная запись
        # получить: ответ = сервер
        return self._account['server']

    def get_port(self):
        # дано    : учётная запись
        # получить: ответ = порт
        return self._account['port']

    def get_user(self):
        # дано    : учётная запись
        # получить: ответ = пользователь
        return self._account['user']

    def get_password(self):
        # дано    : учётная запись
        # получить: ответ = пароль
        return self._account['password']

    def is_empty(self):
        # дано    : учётная запись
        # получить: ответ = учётная запись пуста
        return all(i is None for i in self._account.values())

    def has_empty(self):
        # дано    : учётная запись
        # получить: ответ = среди полей есть пустое
        return None in self._account.values()

    def end(self):
        # дано    :
        # получить:
        pass


class ModesHandler:

    def __init__(self):
        # дано    :
        # получить: созданы режимы
        self._modes_dict = None

    def start(self):
        # дано    :
        # получить: установлены все пустые режимы
        self._modes_dict = {'message_range': [None, None]}

    def is_enabled_range(self):
        # дано    : режим диапазона сообщений
        # получить: ответ = установлен ли диапазон (да/нет)
        return self._modes_dict['message_range'] != [None, None]

    def set_range(self, start=None, end=None):
        # дано    : режим диапазона сообщений и поля
        #           (любое поле может отсутствовать)
        # получить: в режиме диапазона сообщений установлены
        #           заданные поля
        mode = self._modes_dict['message_range']
        if start is not None:
            mode[0] = start
        if end is not None:
            mode[1] = end

    def unset_range(self, start=False, end=False):
        # дано    : режим диапазона сообщений и поля вида True/False
        # получить: в режиме диапазона сообщений истинные поля сделаны пустыми
        mode = self._modes_dict['message_range']
        if start:
            mode[0] = None
        if end:
            mode[1] = None

    def get_range(self):
        # дано    : режим диапазона сообщений
        # получить: ответ = (start, end)
        mode = self._modes_dict['message_range']
        return tuple(mode)

    def get_range_start(self):
        # дано    : режим диапазона сообщений
        # получить: ответ = нижняя граница диапазона
        mode = self._modes_dict['message_range']
        return mode[0]

    def get_range_end(self):
        # дано    : режим диапазона сообщений
        # получить: ответ = верхняя граница диапазона
        mode = self._modes_dict['message_range']
        return mode[1]

    def end(self):
        # дано    :
        # получить:
        pass


class ConnectionHandler:

    def __init__(self, server, port, user, password, waitsec):
        # дано    : сервер, порт, имя, пароль и время ожидания
        #           в секундах
        # получить: сервер, порт, имя, пароль и время ожидания
        #           в секундах сохранены;
        #           создан Pop3Handler с этими параметрами
        self._server = server
        self._port = port
        self._user = user
        self._password = password
        self._waitsec = waitsec
        self._p3h = Pop3Handler(self._server, self._port,
                                self._user, self._password,
                                self._waitsec)
        self._recv_try_max = 3
        self._default_range_start = 1
        self._default_range_end = 1000000

    def start(self):
        # дано    : Pop3Handler выключен
        # получить: Pop3Handler включён
        self._p3h.start()

    def get_pop3_addrsubj(self):
        # дано    : Pop3Handler включён
        # получить: Pop3Handler подключился к серверу,
        #           получил список пар адрес-тема и отключился;
        #           ответ = список пар адрес-тема
        addr_subj_out = []
        self._p3h.login()
        number_of_messages = self._p3h.count_messages()
        for i in range(1, number_of_messages + 1):
            for _ in range(self._recv_try_max):
                try:
                    addr_subj = self._p3h.get_message_headers(
                        i, ('From', 'Subject'))
                    break
                except Pop3TopTimeoutError:
                    addr_subj = ('unknown', 'can\'t receive headers')
                except Pop3CantDecodeHeaders:
                    addr_subj = ('unknown', 'can\'t decode headers')
                    break
            addr_subj_out.append(addr_subj)
        self._p3h.disconnect()
        return addr_subj_out

    def get_pop3_addrsubj_range(self, range_start, range_end):
        # дано    : Pop3Handler включён, заданы начало и конец
        #           диапазона писем
        # получить: Pop3Handler подключился к серверу, получил список
        #           пар адрес-тема из диапазона писем и отключился;
        #           ответ = список пар адрес-тема из диапазона писем
        range_start = range_start or self._default_range_start
        range_end = range_end or self._default_range_end
        addr_subj_out = []
        self._p3h.login()
        number_of_messages = self._p3h.count_messages()
        if number_of_messages > 0 and range_start > number_of_messages:
            raise ConnectionRangeError
        if range_end > number_of_messages:
            range_end = number_of_messages
        for i in range(range_start, range_end + 1):
            for _ in range(self._recv_try_max):
                try:
                    addr_subj = self._p3h.get_message_headers(
                        i, ('From', 'Subject'))
                    break
                except Pop3TopTimeoutError:
                    addr_subj = ('unknown', 'can\'t receive headers')
                except Pop3CantDecodeHeaders:
                    addr_subj = ('unknown', 'can\'t decode headers')
                    break
            addr_subj_out.append(addr_subj)
        self._p3h.disconnect()
        return addr_subj_out

    def end(self):
        # дано    : Pop3Handler включён
        # получить: Pop3Handler выключен
        self._p3h.end()


class Pop3Handler:

    def __init__(self, server, port, user, password, waitsec):
        # дано    : сервер, порт, имя, пароль, время ожидания
        #           в секундах
        # получить: сервер, порт, имя, пароль и время ожидания
        #           в секундах сохранены;
        #           создано пустое соединение
        self._server = server
        self._port = port
        self._user = user
        self._password = password
        self._waitsec = waitsec
        self._conn = None

    def start(self):
        # дано    :
        # получить:
        pass

    def login(self):
        # дано    : сервер, порт, имя, пароль
        # получить: выполнено подключение к серверу на порт
        #           и вход с именем и паролем
        try:
            self._conn = poplib.POP3_SSL(self._server, self._port,
                                         timeout=self._waitsec / 10)
        except socket.gaierror:
            raise Pop3ConnectServerError
        except ConnectionRefusedError:
            raise Pop3ConnectPortError
        except socket.timeout:
            raise Pop3ConnectTimeoutError
        try:
            self._conn.user(self._user)
            self._conn.pass_(self._password)
        except poplib.error_proto:
            raise Pop3LoginError
        except socket.timeout:
            raise Pop3LoginTimeoutError

    def count_messages(self):
        # дано    : открытое соединение
        # получить: ответ = количество писем в ящике
        n = int(self._conn.list()[0].split()[1])
        return n if n >= 0 else 0

    def get_message_headers(self, message_number, header_names):
        # дано    : номер сообщения и упорядоченный список заголовков
        # получить: ответ = кортеж из значений заголовков
        try:
            headers = self._conn.top(message_number, 30)[1]
        except socket.timeout:
            raise Pop3TopTimeoutError
        try:
            headers_selected = self._filter_headers(headers, header_names)
        except UnicodeDecodeError:
            raise Pop3CantDecodeHeaders
        return headers_selected

    def _filter_headers(self, headers, select):
        # дано    : заголовки и список заголовков для выбора
        # получить: ответ = список выбранных и раскодированных
        #           заголовков
        hh = HeadersHandler()
        hh.start(headers)
        lst = hh.filter(select)
        hh.end()
        return lst

    def disconnect(self):
        # дано    : открытое соединение
        # получить: выполнено отключение от сервера
        self._conn.quit()

    def end(self):
        # дано    :
        # получить:
        pass


class HeadersHandler:

    def start(self, headers):
        # дано    : список email-заголовков
        # получить: создано сообщение из заголовков,
        #           получена кодировка сообщения, и сохранены
        base = b'\n'.join(headers)
        msg = email.message_from_bytes(base)
        self._charset = msg.get_charsets()[0]
        self._msg = email.message_from_string(
            base.decode(self._charset or 'latin1'))

    def filter(self, select):
        # дано    : список заголовков для выбора из сообщения
        # получить: ответ = кортеж выбранных раскодированных
        #           заголовков
        return tuple(self._decode_header(self._msg.get(i))
                     for i in select)

    def _decode_header(self, header):
        # дано    : заголовок и кодировка сообщения
        # получить: ответ = раскодированный заголовок
        #           (если раскодирование невозможно,
        #           ответ = первоначальный заголовок)
        res = ''
        defenc = 'latin1'
        for i in email.header.decode_header(header):
            t, e = i
            if e:
                if e != 'unknown-8bit':
                    s = t.decode(e)
                else:
                    s = t.decode(self._charset or defenc)
            else:
                if isinstance(t, str):
                    s = t
                elif re.search(br'\\u[\da-f]{4}', t):
                    s = t.decode('unicode_escape')
                else:
                    s = t.decode(defenc)
            res += s
        return res

    def end(self):
        # дано    :
        # получить: внутренние поля очищены
        self._msg = self._charset = None


class MsgViewerHandler:

    def __init__(self, header, psize, nwidth, message):
        # дано    : заголовок, размер страницы, ширина номера
        #           записи и сообщение
        # получить: заголовок, размер страницы, ширина номера
        #           записи и сообщение сохранены
        self._header = header
        self._psize = psize
        self._nwidth = nwidth
        self._message = message

    def start(self):
        # дано    :
        # получить:
        pass

    def print_pages_addrsubj(self, aslst):
        # дано    : заголовок, размер страницы, ширина номера записи,
        #           сообщение и список пар адрес-тема
        # получить: на экран постранично выведены пары адрес-тема,
        #           в отформатированном виде;
        #           заголовок, тело страницы, сообщение
        fmt = '    {0:0{width}d}\n' \
              '  address: "{1[0]}"\n' \
              '  subject: "{1[1]}"\n'
        empty = '\n' * 3
        psize = self._psize
        npages = math.ceil(len(aslst) / psize)
        ntotas = len(aslst)
        for i in range(npages):
            self._clear()
            print(self._header)
            index = i * psize
            pas = aslst[index:index + psize]
            nas = len(pas)
            for j in range(psize):
                if j < nas:
                    print(fmt.format(
                        index + j + 1, pas[j], width=self._nwidth),
                        end=''
                    )
                else:
                    print(empty, end='')
                if j + 1 < psize:
                    print()
            print('\n  page {0}/{1} of {2}\n'.format(i + 1, npages, ntotas))
            input(self._message)

    def _clear(self):
        # дано    :
        # получить: экран очищен
        os.system('clear')

    def end(self):
        # дано    :
        # получить:
        pass


def mailchecker():
    # дано    : MailChecker выключен
    # получить: MailChecker включён, выполнен с
    #           именем программы, версией, списком параметров
    #           для файла учётных записей и выключен
    filename = '.checkmail-account'
    filepath = os.path.join(os.getenv('HOME'), filename)
    mc = MailChecker(PROG, VERSION,
                     [filepath,
                      'utf-8', '#', ':', 5,
                      'password', 4])
    mc.start()
    try:
        mc.checkmail_menu()
    except KeyboardInterrupt:
        mc.end()
        print()
        print('Bye')
    mc.end()


def get_prog_args():
    """Parse command line arguments to a handy object with attributes."""
    desc = """\
Checks mail for incoming messages.

If some mail has come it prints number of messages in the box and some
their headers like sender address and subject."""
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--version', '-V',
                        action='version',
                        version='%(prog)s ' + 'v' + __version__)
    parser.add_argument('--license',
                        action='version',
                        version='License: ' + __license__ +
                        ', see more details in file LICENSE'
                        ' or at <http://www.gnu.org/licenses/>.',
                        help='show program\'s license and exit')
    return parser.parse_args()

def main():
    args = get_prog_args()
    mailchecker()
    return 0

if __name__ == '__main__':
    sys.exit(main())
