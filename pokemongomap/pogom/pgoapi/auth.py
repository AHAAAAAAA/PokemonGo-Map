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

class Auth:

    def __init__(self):
        self.log = logging.getLogger(__name__)
        
        self._auth_provider = None
        
        self._login = False
        self._auth_token = None
        
        self._ticket_expire = None
        self._ticket_start = None
        self._ticket_end = None
    
    def get_name(self):
        return self._auth_provider
    
    def is_login(self):
        return self._login
        
    def get_token(self):
        return self._auth_token
        
    def has_ticket(self):
        if self._ticket_expire and self._ticket_start and self._ticket_end:
            return True
        else:
            return False
       
    def set_ticket(self, params):
        self._ticket_expire, self._ticket_start, self._ticket_end = params
    
    def get_ticket(self):
        if self.has_ticket():
            return (self._ticket_expire, self._ticket_start, self._ticket_end)
        else:
            return False