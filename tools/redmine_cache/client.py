import requests
import base64
import pickle

def decode(string):
    b = base64.b64decode(string)
    return pickle.loads(b)

def encode(item):
    b = pickle.dumps(item)
    return base64.b64encode(b)

def encode_str(item):
    return encode(item).decode()

class RedmineClient():
    _url = "http://localhost:11649/"
    def __init__(self, api=None):
        self.session = requests.Session()
        self.api = api
        self.headers = {'Connection': 'Keep-Alive'}
        
    def get_all(self):
        return self.get_url(self._url + "cache" + "?issues=all")
        
    def get_url(self, url):
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        issues = decode(r.content.decode())
        self._assign_api(issues.values())
        return issues
    
    def _assign_api(self, issues):
        for iss in issues:
            iss._api = self.api
            
    def get_filtered(self, filters):
        """ Filter issues on the server end, to save bandwidth. 
        Each filter is a tuple of three values:
        
        ('attribute', 'op', 'value')
        
        attribute: attribue of Issue class, obtained by getattr(issue, attribute)
                   attributes can be dotted, in which case the acquisition is chained
        op: comparison operator: ['==', '!=', '>', '<', '>=', '<=']
        value: any picklable value to compare with. Must support any operators 
               used for comparison by the filter, but does not need to support 
               any operators not used. 
        
        """
        url = self._url + "cache?issues=all&filters=" + encode_str(filters)
        return self.get_url(url)