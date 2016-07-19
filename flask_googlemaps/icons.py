"""
The idea is to implement all icons from here:
http://kml4earth.appspot.com/icons.html#mapfiles
and
http://jg.org/mapping/icons.html
and
http://mabp.kiev.ua/2010/01/12/google-map-markers/
"""

__all__ = ['dots', 'alpha']


class Icon(object):
    """Dynbamically return dot icon url"""

    def __init__(self, base_url, options=None):
        self.base_url = base_url
        self.options = options

    def __getattr__(self, item):
        return self.base_url.format(item)


dots = Icon(
    base_url='//maps.google.com/mapfiles/ms/icons/{0}-dot.png',
    options=['blue', 'yellow', 'green', 'red', 'pink', 'purple', 'red']
)

alpha = Icon(
    base_url='//www.google.com/mapfiles/marker{0}.png',
    options=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'
             'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
             'X', 'Z', 'W', 'Y']
)
