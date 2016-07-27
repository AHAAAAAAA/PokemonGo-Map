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

import re
import json
import requests

from auth import Auth

class AuthPtc(Auth):

    PTC_LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
    PTC_LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
    PTC_LOGIN_CLIENT_SECRET = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'

    def __init__(self):
        Auth.__init__(self)
        
        self._auth_provider = 'ptc'
        
        self._session = requests.session()
        self._session.verify = True

    def login(self, username, password):

        self.log.info('PTC login for: %s', username)

        head = {'User-Agent': 'niantic'}
        r = self._session.get(self.PTC_LOGIN_URL, headers=head)
        
        try:
            jdata = json.loads(r.content)
        except ValueError as e:
            self.log.error('{}... server seems to be down :('.format(str(e)))
            return False
            
        data = {
            'lt': jdata['lt'],
            'execution': jdata['execution'],
            '_eventId': 'submit',
            'username': username,
            'password': password[:15],
        }
        r1 = self._session.post(self.PTC_LOGIN_URL, data=data, headers=head)

        ticket = None
        try:
            ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
        except Exception,e:
            try:
                self.log.error('Could not retrieve token: %s', r1.json()['errors'][0])
            except Exception as e:
                self.log.error('Could not retrieve token! (%s)', str(e))
            return False

        data1 = {
            'client_id': 'mobile-app_pokemon-go',
            'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
            'client_secret': self.PTC_LOGIN_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'code': ticket,
        }
        
        r2 = self._session.post(self.PTC_LOGIN_OAUTH, data=data1)
        access_token = re.sub('&expires.*', '', r2.content)
        access_token = re.sub('.*access_token=', '', access_token)

        if '-sso.pokemon.com' in access_token:
            self.log.info('PTC Login successful')
            self.log.debug('PTC Session Token: %s', access_token[:25])
            self._auth_token = access_token
        else:
            self.log.info('Seems not to be a PTC Session Token... login failed :(')
            return False
        
        self._login = True
        
        return True
        
