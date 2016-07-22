"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

import logging
import re
import requests

from utilities import f2i, h2f

from rpc_api import RpcApi
from auth_ptc import AuthPtc
from auth_google import AuthGoogle
from exceptions import AuthException, NotLoggedInException, ServerBusyOrOfflineException

import protos.RpcEnum_pb2 as RpcEnum

logger = logging.getLogger(__name__)

class PGoApi:

    API_ENTRY = 'https://pgorelease.nianticlabs.com/plfe/rpc'

    def __init__(self):
    
        self.log = logging.getLogger(__name__)

        self._auth_provider = None
        self._api_endpoint = None
        
        self._position_lat = 0
        self._position_lng = 0
        self._position_alt = 0

        self._req_method_list = []
        
    def call(self):
        if not self._req_method_list:
            return False
        
        if self._auth_provider is None or not self._auth_provider.is_login():
            self.log.info('Not logged in')
            return False
        
        player_position = self.get_position()
        
        request = RpcApi(self._auth_provider)
        
        if self._api_endpoint:
            api_endpoint = self._api_endpoint
        else:
            api_endpoint = self.API_ENTRY
        
        self.log.info('Execution of RPC')
        response = None
        try:
            response = request.request(api_endpoint, self._req_method_list, player_position)
        except ServerBusyOrOfflineException as e:
            self.log.info('Server seems to be busy or offline - try again!')
        
        # cleanup after call execution
        self.log.info('Cleanup of request!')
        self._req_method_list = []
        
        return response
    
    #def get_player(self):
    
    def list_curr_methods(self):
        for i in self._req_method_list:
            print("{} ({})".format(RpcEnum.RequestMethod.Name(i),i))
    
    def set_logger(self, logger):
        self._ = logger or logging.getLogger(__name__)

    def get_position(self):
        return (self._position_lat, self._position_lng, self._position_alt)

    def set_position(self, lat, lng, alt):   
        self.log.debug('Set Position - Lat: %s Long: %s Alt: %s', lat, lng, alt)
        
        self._position_lat = f2i(lat)
        self._position_lng = f2i(lng)
        self._position_alt = f2i(alt)

    def __getattr__(self, func):
        def function(**kwargs):
        
            if not self._req_method_list:
                self.log.info('Create new request...')
        
            name = func.upper()
            if kwargs:
                self._req_method_list.append( { RpcEnum.RequestMethod.Value(name): kwargs } )
                self.log.info("Adding '%s' to RPC request including arguments", name)
                self.log.debug("Arguments of '%s': \n\r%s", name, kwargs)
            else:
                self._req_method_list.append( RpcEnum.RequestMethod.Value(name) )
                self.log.info("Adding '%s' to RPC request", name)
   
            return self
   
        if func.upper() in RpcEnum.RequestMethod.keys():
            return function
        else:
            raise AttributeError
            
        
    def login(self, provider, username, password):
    
        if not isinstance(username, basestring) or not isinstance(password, basestring):
            raise AuthException("Username/password not correctly specified")
        
        if provider == 'ptc':
            self._auth_provider = AuthPtc()
        elif provider == 'google':
            self._auth_provider = AuthGoogle()
        else:
            raise AuthException("Invalid authentication provider - only ptc/google available.")
            
        self.log.debug('Auth provider: %s', provider)
        
        if not self._auth_provider.login(username, password):
            self.log.info('Login process failed') 
            return False
        
        self.log.info('Starting RPC login sequence (app simulation)')
        
        # making a standard call, like it is also done by the client
        self.get_player()
        self.get_hatched_eggs()
        self.get_inventory()
        self.check_awarded_badges()
        self.download_settings(hash="4a2e9bc330dae60e7b74fc85b98868ab4700802e")
        
        response = self.call()
        
        if not response: 
            self.log.info('Login failed!') 
            return False
        
        if 'api_url' in response:
            self._api_endpoint = ('https://{}/rpc'.format(response['api_url']))
            self.log.debug('Setting API endpoint to: %s', self._api_endpoint)
        
        elif 'auth_ticket' in response:
            auth_ticket = response['auth_ticket']
            self._auth_provider.set_ticket([auth_ticket['expire_timestamp_ms'], auth_ticket['start'], auth_ticket['end']])

        else:
            self.log.error('Login failed - unexpected server response!')
            return False
        
        self.log.info('Finished RPC login sequence (app simulation)')
        self.log.info('Login process completed') 
        
        return True
        
