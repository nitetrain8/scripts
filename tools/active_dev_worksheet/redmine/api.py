import dateutil
import requests
import urllib
import threading
import asyncio
import aiohttp
import pytz

from .converter import RedmineConverter

_urljoin = urllib.parse.urljoin
_urlencode = urllib.parse.urlencode

def resource_attrib(obj, attr):
    if obj is None:
        return None
    return getattr(obj, attr)  


# pylint: disable=maybe-no-member
@RedmineConverter.Register
class Resource():
    _converter_table = [
        ("name", str),
        ("id", int),
        ("value", str)
    ]
    def __str__(self):
        return f"<{self.__class__.__name__} {self.name}, id={self.id}, v={repr(self.value)}>"
    __repr__ = __str__
    
    
# pylint: disable=maybe-no-member
@RedmineConverter.Register
class SimpleResource():
    _converter_table = [
        ("name", str),
        ("id", int)
    ]
    def __str__(self):
        return f"<{self.__class__.__name__} {self.name}, id={self.id}>"
    __repr__ = __str__


@RedmineConverter.Register
class User(SimpleResource):
    pass

    
def Datetime(d):
    return dateutil.parser.parse(d).astimezone(pytz.timezone("US/Pacific"))


def CustomFields(cf):
    fields = {}
    for f in cf:
        fields[f['name']] = RedmineConverter.Deserialize(f, Resource)
    return fields


def Parent(p):
    return p['id']


@RedmineConverter.Register
class Issue():
    
    _converter_table = [
        ("author", User),
        ("custom_fields", CustomFields),
        ("fixed_version", Resource),
        ("status", Resource),
        ("created_on", Datetime),
        ("updated_on", Datetime),
        ("id", int),
        ("project", Resource),
        ("priority", Resource),
        ("due_date", Datetime),
        ("tracker", Resource),
        ("parent", Parent),
        ("closed_on", Datetime),
        ("start_date", Datetime),
        ("assigned_to", User),
        ("estimated_hours", float)
    ]
    
    def __init__(self):
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self.subject}'>"


@RedmineConverter.Register
class Project():
    _converter_table = [
        ("id", int),
        ("name", str),
        ("identifier", str),
        ("description", str),
        ("status", int),
        ("is_public", bool),
        ("custom_fields", CustomFields),
        ("created_on", Datetime),
        ("updated_on", Datetime)
    ]

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self.name} ({self.identifier})'>"


@RedmineConverter.Register
class Version():
    _converter_table = [
        ("id", int),
        ("name", str),
        ("project", SimpleResource),
        ("description", str),
        ("status", str),
        ("due_date", Datetime),
        ("sharing", str),
        ("created_on", Datetime),
        ("updated_on", Datetime)
    ]

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self.name}'>"


class Client():
    def __init__(self, url, key):
        if not url.startswith("http"):
            url = "https://"+url
        self._url = url
        self._key = key
        self._sess = requests.Session()
        self._headers = {'X-Redmine-API-Key': self._key}
        self._Issues = None
        self._Projects = None
        
    def _rawget(self, url, headers):
        r = self._sess.get(url, headers=headers)
        r.raise_for_status()
        return r
    
    def _prep(self, path, opts):
        base = _urljoin(self._url, path)
        qs = _urlencode(opts)
        url = f"{base}?{qs}"
        return url, self._headers
    
    def get(self, path, opts):
        url, headers = self._prep(path, opts)
        return self._rawget(url, headers)
    
    async def get_async(self, session, path, opts):
        url, headers = self._prep(path, opts)
        async with session.get(url, headers=headers) as r:
            r.raise_for_status()
            return await r.json()
        
    def superget(self, key, path, opts=None):
        base = _urljoin(self._url, path)
        opts = opts or {}
        pool = RedmineSuperPool(self._headers, key, base, opts)
        results = pool.wait()
        count = pool.total_count()
        assert len({x['id'] for x in results}) == count
        return results
            
    @property
    def Issues(self):
        if self._Issues is None:
            self._Issues = IssuesClient(self)
        return self._Issues

    @property
    def Projects(self):
        if self._Projects is None:
            self._Projects = ProjectsClient(self)
        return self._Projects
    
    def close(self):
        self._Issues = None



def _step_range(start, total_count, step):
        end = total_count - 1
        
        # extra is the amount needed to ensure
        # the final iteration includes the "end"
        # value
        extra = step - (end - start) % step 
        stop = end + extra
        return range(start, stop, step)

# XXX Move to unit test or something
def _test_step_range():
    def test_step_range(start=None, limit=100, total_count=1021):
        if start is None:
            start = limit
        for i in _step_range(start, total_count, limit):
            pass
        ilast = total_count - 1
        assert (i + limit > ilast)
        assert (i + limit <= ilast + limit)
    
    for start in (0, None):
        for l in (99, 100, 101):
            for i in range(900, 1100):
                test_step_range(start, l, i)
_test_step_range()
    
    
class RedmineSuperPool:
    """
    Spawns a thread with a new asyncio event loop.

    Gathers paginated results from redmine based on the standard
    pagination scheme:
    {
        'offset': <offset>,
        'limit': <limit>,
        'total_count': <total>,
        '<key>': {
            ...
        }
    }

    The first call is used to determine the number of pages.
    All remaining pages are then downloaded in parallel using
    asyncio tasks, and appended to a list of results.

    The results list is returned using RedmineSuperPool.wait().
    """
    def __init__(self, headers, key, path, opts):
        """Create a new SuperPool and start running the request.

        Args:
            headers (dict): request headers. Must include authentication.
            key (string): Object key for the requested resource. 
            path (string): Request URL, not including query string.
            opts (dict): Common query string parameters.
        """        
        self._headers = headers
        self._path = path
        self._opts = opts
        self._key = key
        
        self._thread = threading.Thread(None, target=self._run, daemon=True)
        self._stop = False
        self._results = []
        self._total_count = 0
        self._thread.start()
        
    def _run(self):
        self._stop = False
        main = self._main()
        asyncio.run(main)
        
    def wait(self, timeout=None):
        """Wait for the pool to finish running and return
        the results list.

        Returns:
            List[object]: List of results.
        """
        self._thread.join(timeout)
        if not self._thread.is_alive():
            return self._results
    
    def total_count(self):
        return self._total_count
        
    def _urlify(self, path, opts):
        return f"{path}?{_urlencode(opts)}"
        
    async def _main(self):
        loop = asyncio.get_running_loop()
        
        # don't choke the network :)
        concurrent_connection_limit = 100
        sem = asyncio.Semaphore(concurrent_connection_limit)
        
        async with aiohttp.ClientSession(headers=self._headers) as session:
            
            # first call gets total count. It is probably not possible
            # to avoid this unless the number of issues is known in advance.
            opts = self._opts
            opts['limit'] = limit = 100
            opts['offset'] = offset = 0
            url = self._urlify(self._path, opts)
            j = await self._fetch_result(session, url, sem)
            
            self._total_count = total_count = j['total_count']
            
            tasks = []
            for offset in _step_range(limit, total_count, limit):
                opts['offset'] = offset
                url = self._urlify(self._path, opts)
                task = loop.create_task(self._fetch_result(session, url, sem))
                tasks.append(task)
            await asyncio.gather(*tasks)
            assert len(self._results) == total_count, (len(self._results), total_count)
                
    async def _fetch_result(self, session, url, sem):
        async with sem:
            j = await self._fetch(session, url)
            self._results.extend(j[self._key])
            return j
            
    async def _fetch(self, session, url):
        ret = await session.get(url)
        ret.raise_for_status()
        return await ret.json()
        
    
class IssuesClient():
    def __init__(self, client):
        self._client = client
        
    def filter(self, /, **opts):
        raw = self._client.superget("issues", "/issues.json", opts)
        def parse(x):
            return RedmineConverter.Deserialize(x, Issue)
        return [parse(x) for x in raw]
    

class ProjectsClient():
    def __init__(self, client):
        self._client = client

    def filter_versions(self, project, /, **opts):
        raw = self._client.superget("versions", f"/projects/{project}/versions.json", opts)
        def parse(x):
            return RedmineConverter.Deserialize(x, Version)
        return [parse(x) for x in raw]

    