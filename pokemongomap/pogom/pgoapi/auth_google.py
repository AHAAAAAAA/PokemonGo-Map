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

from auth import Auth
from gpsoauth import perform_master_login, perform_oauth

class AuthGoogle(Auth):

    GOOGLE_LOGIN_ANDROID_ID = '9774d56d682e549c'
    GOOGLE_LOGIN_SERVICE= 'audience:server:client_id:848232511240-7so421jotr2609rmqakceuu1luuq0ptb.apps.googleusercontent.com'
    GOOGLE_LOGIN_APP = 'com.nianticlabs.pokemongo'
    GOOGLE_LOGIN_CLIENT_SIG = '321187995bc7cdc2b5fc91b11a96e2baa8602c62'

    def __init__(self):
        Auth.__init__(self)
        
        self._auth_provider = 'google'

    def login(self, username, password):
        self.log.info('Google login for: {}'.format(username))
        login = perform_master_login(username, password, self.GOOGLE_LOGIN_ANDROID_ID)
        login = perform_oauth(username, login.get('Token', ''), self.GOOGLE_LOGIN_ANDROID_ID, self.GOOGLE_LOGIN_SERVICE, self.GOOGLE_LOGIN_APP,
            self.GOOGLE_LOGIN_CLIENT_SIG)
            
        self._auth_token = login.get('Auth')
        
        if self._auth_token is None:
            self.log.info('Google Login failed.')
            return False
        
        self._login = True
            
        self.log.info('Google Login successful.')
        self.log.debug('Google Session Token: %s', self._auth_token[:25])

        return True