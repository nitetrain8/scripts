""" Issuetracker API 

* TODO: Create IssueList class (?)
* Parse Gantt HTML for class 'issue-subject' using style:width to determine hierarchy
* Consider method of lazy evaluation of issue field generation by
calling back to API to download project issues CSV, and update all issues
in project. 
* Implement issue caching

Issue():
    * Add programmatic logging of all fields seen, ever.
    * Map fields seen to types and conversion functions

"""

import requests
import urllib
import pyquery
from collections import OrderedDict
import re
import dateutil.parser
import lxml
import json

uj = urllib.parse.urljoin
_sp_re = re.compile(r"(\d*?) (subproject)?(s{0,1})")
_name2id_re = re.compile(r"(.*?)\s*?#(\d*)$")

class IssuetrackerAPI():
    _login_url = "/login"
    _proj_issues_url = "/projects/%s/issues"
    _issues_url = "/issues"
    _proj_url = "/projects"
    
    def __init__(self, base_url, username, pw, login=True):
        r = urllib.parse.urlparse(base_url)
        if not r.scheme and not r.netloc:
            base_url = urllib.parse.urlunparse(("https", r.path, "", r.params, r.query, r.fragment))
        self._base_url = base_url
        self._sess = requests.Session()
        
        if username is None or pw is None:
            raise ValueError("Must have valid username and password.")
        
        self._username = None
        self._password = None
        self._auth = (None, None)
        self._cache = {}
        self._logged_in = False
        
        self._set_usrpw(username, pw)
        self._autologin = login
        self._cache['known_users'] = Users(self)
        if login:
            self.login()
            
    def _set_usrpw(self, usr, pw):
        self._username = usr
        self._password = pw
        self._auth = (usr, pw)

    @property
    def logged_in(self):
        return self._logged_in

    def maybe_login(self):
        if not self._logged_in:
            self.login()
        
    def configure_login(self, user, pw, login=True):
        self._set_usrpw(user, pw)
        if login:
            self.login()

    def clear_cache(self):
        self._cache.clear()
        
    def copy(self):
        cls = self.__class__
        new = cls(self._base_url, self._username, self._password, False)
        new._sess.cookies = self._sess.cookies.copy()
        return new

    def __getstate__(self):
        return {}

    def __getinitargs__(self):
        return self._base_url, self._username, self._password, self._autologin

    def projects(self, project_id=None):
        """ Return dict of projects if project_id is None, or project matching 
        `project_id`.
        """
        pj = self._cache.get("projects", None)
        if pj is None:
            pj = self.download_projects()
        
        if project_id is not None:
            for attr in ("id", "name", "identifier"):
                for p in pj.values():
                    if getattr(p, attr) == project_id:
                        return p
            else:
                raise ValueError("Failed to find project with id %r"%project_id)
        return pj
            
    def login(self):
        r1 = self._sess.get(self._base_url)
        r1.raise_for_status()
        q = pyquery.PyQuery(r1.content)
        data = {}
        lf = q("#login-form :input")
        if not lf:
            # not found means we're probably already
            # logged in
            if 'autologin' not in self._sess.cookies \
                or '_session_id' not in self._sess.cookies:
                raise ValueError("Something went horribly wrong trying to log in, check URL!", r1)
            else:
                return
        for td in lf:
            at = td.attrib
            if 'name' in at:
                k = at['name']
                v = at.get('value', "")
                data[k] = v
                
        data['username'] = self._username
        data['password'] = self._password
        
        body = urllib.parse.urlencode(data)
        url = uj(self._base_url, self._login_url)
        r2 = self._sess.post(url, body)
        r2.raise_for_status()
        if not pyquery.PyQuery(r2.content)("#loggedas"):
            raise ValueError("Invalid Username or Password")
        self._logged_in = True
        return r2
        
    # def download_project_issues_csv(self, project, utf8=True, columns='all'):
    #     r = self._download_project_csv(project, utf8, columns)
    #     return self._parse_proj_csv(r.content)
    
    def _download_project_csv(self, project, utf8, columns):
        if utf8:
            utf8 = "%E2%9C%93"
        else:
            utf8 = ""
        url_end = ".csv?utf8=%s&columns=%s" 
        url = (self._proj_issues_url + url_end) % (project, utf8, columns)
        url = uj(self._base_url, url)
        r = self._sess.get(url)
        r.raise_for_status()
        return r
    
    def download_issue_pdf(self, id_, **kw):
        href = self._issues_url + "/" + str(id_)
        return self.download_issue_pdf2(href, **kw)

    def download_issue_pdf2(self, href, **kw):
        """ Sometimes it is more convenient to access issue by provided 
        href. """
        typ = ".pdf"
        url = uj(self._base_url, href + typ)
        r = self._sess.get(url, **kw)
        r.raise_for_status()
        return r.content

    def add_watcher(self, iid, user_id):
        j ='{"user_id": %d}'%iid
        url = "/issues/%s/watchers.json"%iid
        url = uj(self._base_url, url)
        r = self._sess.delete(url, data=j)
        r.raise_for_status()
        return r.content

        
    # def _parse_proj_csv(self, csv, encoding='utf-8'):
    #     if not isinstance(csv, str):
    #         csv = csv.decode(encoding)
    #     sl = csv.splitlines()
    #     sl[0] = sl[0].lower().replace('"', "")
    #     lines = [l.split(",") for l in sl]
    #     issues = OrderedDict()
    #     for i, l in enumerate(lines[1:], 1):
    #         issue = Issue(line=sl[i], api=self)
    #         for key, val in zip(lines[0], l):
    #             issue[key] = val.strip('"') or "<n/a>"
    #         issue['#'] = int(issue['#'])
    #         issues[issue['#']] = issue
    #     return issues
    
#     def download_projects(self):
#         url = uj(self._base_url, self._proj_url)
#         r = self._sess.get(url)
#         r.raise_for_status()
#         c = r.content
#         q = pyquery.PyQuery(c)
#         q2 = q("#projects-index > [class='projects root']")
#         projects = _Project(self, "All", "")
#         for e in q2.children(".root"):
#             proj_ele = pyquery.PyQuery(e).children(".root > a")[0]
#             pt = proj_ele.text
#             phref = proj_ele.attrib['href'].split("/")[-1]
#             proj = projects.add(pt, phref)
#             q4 = pyquery.PyQuery(e).children("[class='more collapsed']")
#             if len(q4) and _sp_re.match(q4[0].text):
#                 q3 = pyquery.PyQuery(e)("[class='projects ']")
#                 for e2 in q3(".child > .child > a"):
#                     proj.add(e2.text, e2.attrib['href'].split("/")[-1])
#         return projects

    def download_projects(self):
        url = uj(self._base_url, self._proj_url + ".xml")
        print("Downloading projects...")
        r = self._sess.get(url, auth=self._auth)
        r.raise_for_status()
        xml = lxml.etree.XML(r.content)  #pylint: disable=E1101
        projects = {}
        for proj in xml.findall("project"):
            p = Project.from_element(self, proj)
            projects[p.name] = p
        
        # Second pass, process project subtasks
        for p in projects.values():
            if p.parent is not None:
                parent = projects[p.parent['name']]
                parent.add_subproject(p)
        self._cache['projects'] = projects
        return projects
    
    def _download_gantt_raw(self, project):
        url = (self._proj_issues_url % project) + "/gantt"
        url = uj(self._base_url, url)
        r1 = self._sess.get(url)
        r1.raise_for_status()
        return r1.content

    def download_gantt(self, project):
        project = self.projects(project).identifier
        c = self._download_gantt_raw(project)
        q = pyquery.PyQuery(c)
        q2 = q(".gantt_subjects")
        i_list = []
        for el in q2.children(".issue-subject"):
            e2 = pyquery.PyQuery(el).children("span > a")[0]
            _, id_ = _name2id_re.match(e2.text).groups()
            id_ = int(id_)
            i_list.append(id_)
        
        # try to return cached issues if possible. 
        project_issues = self.download_issues(project)
        rv = [] 
        for i in i_list:
            rv.append(project_issues[i])
            
        # sanity check list of subissues. There should be no cycles in this graph. 
        # Also this seems to run in a few ms, so no big deal.
        _map_issues(rv)
        
        return rv
    
    def _download_project_issues_iter(self, ops, limit, offset):
        ops['limit'] = limit
        ops['offset'] = offset
        url = uj(self._base_url, self._issues_url + ".json")
        url += "?" + urllib.parse.urlencode(ops)
        r = self._sess.get(url, auth=self._auth)
        r.raise_for_status()
        return r

    def download_issue(self, id, fmt="json", include=()):
        url = "%s/%s.%s"%(self._issues_url, str(id), fmt)
        if include:
            url += "?include="+",".join(include)
        url = uj(self._base_url, url)
        r = self._sess.get(url, auth=self._auth)
        r.raise_for_status()
        return Issue.from_json(self, **json.loads(r.content.decode())['issue'])

    def download_users(self, fmt='json', status=None, name=None, group_id=None):
        url = "/users."+fmt
        url = uj(self._base_url, url)
        kw = {}
        if status:
            kw['status'] = status
        if name:
            kw['name'] = name
        if group_id:
            kw['group_id'] = group_id
        if kw:
            url += "?" + urllib.parse.urlencode(kw)
        r = self._sess.get(url, auth=self._auth)
        r.raise_for_status()
        d = json.loads(r.content.decode())['user']
        rv = {}
        for user in d:
            name = user['firstname'] + " " + user['lastname']
            id = user['id']
            u = User(self, name, id)
            for k, v in user.items():
                setattr(u, k, v)
            rv[id] = u
        return rv

    @property
    def users(self):
        return self._cache['known_users']

    def get_users(self):
        return self.users

    def _add_user(self, u):
        self._cache['known_users'] = users = self._cache.get('known_users') or Users(self)
        users.add_user(u)

    def download_issues(self, project_id=None, created_on=None, modified_on=None, **filters):
        if not self._logged_in:
            self.login()
        ops = {}
        ops.update(filters)
        if project_id:
            if isinstance(project_id, str):
                project_id = self.projects(project_id).id
            ops['project_id'] = project_id
            
        # Unfortunately the api for querying dates and ranges is 
        # quite awkward to translate into a sensible python api
        
        if created_on:
            if not isinstance(created_on, str):
                raise TypeError("Argument created_on must be type" \
                     "str- try .isoformat() (got type %r)" % created_on)
            ops['created_on'] = created_on
            
        if modified_on:
            if not isinstance(modified_on, str):
                raise TypeError("Argument created_on must be type " \
                    "str- try .isoformat() (got type %r)" % modified_on)
            ops['modified_on'] = modified_on
            
        issues = {i.id: i for i in self._download_issues(ops)}
        reloop = True
        while reloop:
            reloop = False
            users = set()
            for iss in issues.values():
                if iss.parent is not None:
                    id_ = iss.parent
                    if isinstance(id_, Issue):
                        continue
                    p = issues.get(id_,None)
                    if p is None:
                        p = self.download_issue(id_)
                        issues[id_] = p
                        reloop = True
                    iss.parent = p
                    issues[id_].subtasks.append(iss)
                for u in iss._get_users():
                    users.add(u)
                if reloop:
                    break
        for u in users:
            self._add_user(u)
        return issues           
            

    def _download_issues(self, ops):
        offset = 0
        limit = 100
        limit = min(max(limit, 0), 100)
        total_count = 0
                
        print("\rDownloading issues...", end="")
        while True:
            r = self._download_project_issues_iter(ops, limit, offset)
            d = json.loads(r.content.decode())
            issues = d['issues']

            if not issues:
                break

            yield from self._parse_issues(issues)

            total_count = int(d.get('total_count', 0))
            offset += len(issues)
            print("\rDownloading issues: %d/%d      " % (offset, total_count), end="")
            if offset >= total_count:
                break
        print()

    def _parse_issues(self, issues):
        for i in issues:
            yield Issue.from_json(self, **i)

    def create_issue(self, project_id, subject, status_id, **kw):
        # these three are required (for us), others optional.
        kw['project_id'] = project_id
        kw['subject'] = subject
        kw['status_id'] = status_id
        url = uj(self._base_url, self._issues_url + ".json")
        r = self._sess.post(url, json={'issue':kw}, auth=self._auth)
        r.raise_for_status()
        return Issue.from_json(self, json.loads(r.content.decode())['issue'])

    def get_versions(self, project_id):
        url = uj(self._base_url, "/projects/%s/versions.json"%project_id)
        r = self._sess.get(url, auth=self._auth)
        r.raise_for_status()
        kw = json.loads(r.content.decode())['versions']
        return FixedVersions.from_json(self, kw)

    def get_trackers(self):
        url = uj(self._base_url, "/trackers.json")
        r = self._sess.get(url, auth=self._auth)
        r.raise_for_status()
        kw = json.loads(r.content.decode())['trackers']
        return Trackers.from_json(self, kw)
    

def _gantt_duplicate(issue, level):
    raise ValueError("Found duplicate issue at level %d: %r" % (level, issue.subject))

def _map_issues_recursive(issues, seen, level, set_issues):
    for i in issues:
        if i.parent and i.parent.id in set_issues and i.parent.id not in seen:
            continue
        if i.id in seen:
            if level == 0:
                continue
        else:    
            _gantt_duplicate(i, level)
        seen.add(i.id)
        subt = i.subtasks
        _map_issues_recursive(subt, seen, level+1, set_issues)
    return seen

def _map_issues(issues):
    set_issues = {i.id for i in issues}
    try:
        seen = _map_issues_recursive(issues, set(), 0, set_issues)
    except ValueError as e:
        e2 = ValueError()
        e2.args = e.args
        raise e2 from None
    if len(seen) != len(issues):
        raise ValueError("Internal error checking gantt integrity: len(seen) != len(issues).")
    if (set_issues - seen):
        raise ValueError("Internal error checking gantt integrity: Not all issues seen.")
    
def _parse_custom_fields(e):
    rv = {}
    for cf in e.findall("custom_field"):
        cfd = {}
        cfd.update(cf.attrib)
        v = cf.find("value")
        if v is None or v.text == 'blank':
            val = None
        else:
            val = v.text
        cfd['value'] = val
        rv[cfd['name']] = cfd
    return rv

def _parse_datetime(e):
    return dateutil.parser.parse(e.text)

def _parse_int(e):
    return int(e.text)

def _parse_bool(e):
    t = e.text.lower()
    if t == 'false':
        return False
    return True

def _parse_parent(e):
    return {k:v for k,v in e.attrib.items()}


class Trackers():
    def __init__(self, api, it=()):
        super().__init__()
        self.api = api
        self.trackers = list(it)
        self.name_to_ob = {i.name: i for i in self.trackers}
        self.id_to_ob = {i.id: i for i in self.trackers}
    
    def _from_list(self, l, *oattr):
        cls = self.__class__
        ns = cls(self.api, l)
        for a in oattr:
            setattr(ns, a, getattr(self, a))
        return ns
        
    def find(self, name=None, id=None):
        rv = []
        for t in self.trackers:
            if name is not None and name != t.name: continue
            if id is not None and id != t.id: continue
            rv.append(t)
        return self._from_list(rv)
        
    def __getitem__(self, key):
        return self.lookup(key)
    
    def lookup(self, key):
        for mp in (self.name_to_ob, self.id_to_ob):
            try:
                return mp[key]
            except KeyError:
                pass
        raise KeyError(key)

    @classmethod
    def from_json(cls, api, js):
        """ Primary public constructor """
        l = []
        for j in js:
            t = Tracker.from_json(api, j)
            l.append(t)
        return cls(api, l)

    def add_tracker(self, t):
        if t in self.trackers:
            return
        self.trackers.append(t)
        self.name_to_ob[t.name] = t
        self.id_to_ob[t.id] = t
    
    def __repr__(self):
        return "<%s>: %s" % (self.__class__.__name__, ", ".join(map(repr, self.trackers)))

class Tracker():
    def __init__(self, api, name=None, id=None, default_status=None):
        self.api = api
        self.name = name
        self.id = id
        self.default_status = default_status
        
    @classmethod
    def from_json(cls, api, js):
        return cls(api, 
                js['name'],
                js['id'],
                js['default_status'],
            )
    def __repr__(self):
        return "<%s(name=%r, id=%s)>" % (self.__class__.__name__, self.name, self.id)

class Project():
    def __init__(self, api, id=0, name="", identifier="", description="", parent=None, status=None, 
                 is_public=False, custom_fields=None, created_on=None, updated_on=None):
        self._api = api
        self.name = name
        self.id = id
        self.name = name
        self.identifier = identifier
        self.description = description
        self.parent = parent
        self.status = status
        self.is_public = is_public
        self.custom_fields = custom_fields
        self.created_on = created_on
        self.updated_on = updated_on
        self._subprojects = []
        
    def __getstate__(self):
        d = self.__dict__.copy()
        del d['_api']
        return d

    def add_subproject(self, sp):
        sp.parent = self
        if sp not in self._subprojects:
            self._subprojects.append(sp)
            
    def __repr__(self):
        return "_Project(%s)" % ', '.join("%s=%r" % \
            (k[0], _reprify(getattr(self, k[0]), self)) for k in self._proj_parse_table)
    
    def download_issues(self, utf8=True, columns='all'):
        return self._api.download_project_issues(self.identifier, utf8, columns)
    
    def download_gantt(self):
        return self._api.download_gantt(self.identifier)
        
    _proj_parse_table = [
        # e.tag attr parse function
        ("id", "id", _parse_int),
        ("name", "name", None),
        ("identifier", "identifier", None),
        ("description", "description", None),
        ("parent", "parent", _parse_parent),
        ("status", "status", _parse_int),
        ("is_public", "is_public", _parse_bool),
        ("custom_fields", "custom_fields", _parse_custom_fields),
        ("created_on", "created_on", _parse_datetime),
        ("updated_on", "updated_on", _parse_datetime),
    ]
        
    @classmethod
    def from_element(cls, api, e):
        kw = {}
        for tag, k, func in cls._proj_parse_table:
            el = e.find(tag)
            if el is None:
                continue
            if func:
                v = func(el)
            else:
                v = el.text
            if v is not None:
                kw[k] = v
        if not kw and e.tag != 'project':
            raise ValueError("Failed to parse element: element should be <project> element.")
        return cls(api, **kw)

    def create_issue(self, subject, status_id, **kw):
        self._api.create_issue(self.id, subject, status_id, **kw)

    def get_versions(self):
        return self._api.get_versions(self.identifier)
        
def _unrecognized_kw(kw):
    return ValueError("Unrecognized keywords: %s" % (', '.join(repr(s) for s in kw)))

def _iss_parse_datetime(api, a, v):
    return dateutil.parser.parse(v)

def _iss_parse_int(api, a, v):
    return int(v)

def _iss_parse_usr(api, a, v):
    name = v.pop('name')
    id = v.pop('id')
    if v:
        raise _unrecognized_kw(v)
    return User(api, name, id)

def _iss_parse_resource(api, a, v):
    name = v.pop('name')
    id = v.pop('id')
    value = v.pop('value', "")
    if v:
        raise _unrecognized_kw(v)
    return ResourceWithID(api, name, id, value)

def _iss_parse_project(api, a, v):
    return api.projects()[v['name']]

def _iss_parse_parent(api, a, v):
    if v:
        return int(v['id'])

def _iss_parse_custom_fields(api, a, v):
    fields = {}
    for d in v:
        name = d.pop('name')
        id = d.pop('id')
        val = d.pop('value', "")
        r = ResourceWithID(api, name, id, val)
        for k, v in d.items():
            setattr(r, k, v)
        fields[name] = val
    return fields


class FixedVersion():
    def __init__(self, api, created_on=None, name=None, sharing=None, status=None, updated_on=None, id=None, description=None, project=None):
        self.api = api
        self.created_on = created_on
        self.name = name
        self.sharing = sharing
        self.status = status
        self.updated_on = updated_on
        self.id = id
        self.description = description
        self.project = project

    @classmethod
    def from_json(cls, api, js):
        return cls(api, 
                dateutil.parser.parse(js['created_on']),
                js['name'],
                js['sharing'],
                js['status'],
                dateutil.parser.parse(js['updated_on']),
                js['id'],
                js['description'],
                js['project'],
            )
    def __repr__(self):
        return "<%s(name=%r, id=%s)>" % (self.__class__.__name__, 
                                        self.name, self.id)


class FixedVersions():
    def __init__(self, api, it=()):
        super().__init__()
        self.api = api
        self.fixed_versions = list(it)
        self.name_to_ob = {i.name: i for i in self.fixed_versions}
        self.id_to_ob = {i.id: i for i in self.fixed_versions}
    
    def _from_list(self, l, *oattr):
        cls = self.__class__
        ns = cls(self.api, l)
        for a in oattr:
            setattr(ns, a, getattr(self, a))
        return ns
        
    def find(self, name=None, id=None):
        rv = []
        for f in self.fixed_versions:
            if name is not None and name != f.name: continue
            if id is not None and id != f.id: continue
            rv.append(f)
        return self._from_list(rv)
        
    def __getitem__(self, key):
        return self.lookup(key)
    
    def lookup(self, key):
        for mp in (self.name_to_ob, self.id_to_ob):
            try:
                return mp[key]
            except KeyError:
                pass
        raise KeyError(key)

    @classmethod
    def from_json(cls, api, js):
        """ Primary public constructor """
        l = []
        for j in js:
            f = FixedVersion.from_json(api, j)
            l.append(f)
        return cls(api, l)

    def add_fixed_version(self, f):
        if f in self.fixed_versions:
            return
        self.fixed_versions.append(f)
        self.name_to_ob[f.name] = f
        self.id_to_ob[f.id] = f
    
    def __repr__(self):
        return "<%s>: %s" % (self.__class__.__name__, ", ".join(map(repr, self.fixed_versions)))



class ResourceWithID():
    def __init__(self, api, name, id, value=""):
        self.api = api
        self.name = name
        self.id = id
        self.value = value
        
    def __repr__(self):
        n = self.__class__.__name__
        args = ', '.join("%s=%r" % (a, getattr(self, a)) for a in ("name", 'id'))
        return "%s(%s)" % (n, args)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, ResourceWithID):
            return (self.id == other.id) and (self.name == other.name) and (self.value == other.value)
        else:
            return NotImplemented

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['api']
        return d

    def __hash__(self):
        return hash((self.id, self.name, self.value))

class User(ResourceWithID):
    @classmethod
    def from_json(cls, api, j):
        return cls(api, j['name'], j['id'])

class Users():
    def __init__(self, api, it=()):
        super().__init__()
        self.api = api
        self.users = list(it)
        self.name_to_ob = {i.name: i for i in self.users}
        self.id_to_ob = {i.id: i for i in self.users}
    
    def _from_list(self, l, *oattr):
        cls = self.__class__
        ns = cls(self.api, l)
        for a in oattr:
            setattr(ns, a, getattr(self, a))
        return ns
        
    def find(self, name=None, id=None):
        rv = []
        for u in self.users:
            if name is not None and name != u.name: continue
            if id is not None and id != u.id: continue
            rv.append(u)
        return self._from_list(rv)
        
    def __getitem__(self, key):
        return self.lookup(key)
    
    def lookup(self, key):
        for mp in (self.name_to_ob, self.id_to_ob):
            try:
                return mp[key]
            except KeyError:
                pass
        raise KeyError(key)

    @classmethod
    def from_json(cls, api, js):
        """ Primary public constructor """
        l = []
        for j in js:
            u = User.from_json(api, j)
            l.append(u)
        return cls(api, l)

    def add_user(self, u):
        self.users.append(u)
        self.name_to_ob[u.name] = u
        self.id_to_ob[u.id] = u

    def __repr__(self):
        return "<%s>: %s" % (self.__class__.__name__, ", ".join(map(repr, self.users)))
        
        
def _reprify(v, self=None):
    if isinstance(v, self.__class__):
        return "%s(...)" % self.__class__.__name__
    if isinstance(v, dict):
        return "{...}"
    if isinstance(v, list):
        return "[...]"
    if isinstance(v, str):
        if len(v) > 20:
            return repr("%.17s..."%v)
        else:
            return repr(v)
    return repr(v)

class Issue():
    
    _issue_parse_tbl = [
        ("author", "author", _iss_parse_usr),
        ("custom_fields", "custom_fields", _iss_parse_custom_fields),
        ("fixed_version", "sprint_milestone", _iss_parse_resource),  # oddly named. TODO double check this
        ("category", "category", None),
        ("status", "status", _iss_parse_resource),
        ("company", "company", None),
        ("created_on", "created_on", _iss_parse_datetime),
        ("description", "description", None),
        ("subject", "subject", None),
        ("done_ratio", "done_ratio", None),
        ("crm_reply_token", "crm_reply_token", None),
        ("updated_on", "updated_on", _iss_parse_datetime),
        ("id", "id", _iss_parse_int),
        ("project", "project", _iss_parse_project),
        ("contact", "contact", None),
        ("priority", "priority", _iss_parse_resource),
        ("due_date", "due_date", _iss_parse_datetime),
        ("estimated_hours", "estimated_hours", None),
        ("tracker", "tracker", _iss_parse_resource),
        ("parent", "parent", _iss_parse_parent),
        ("closed_on", "closed_on", _iss_parse_datetime),
        ("start_date", "start_date", _iss_parse_datetime),
        ("tracking_uri", "tracking_uri", None),
        ("assigned_to", "assigned_to", _iss_parse_usr)
    ]

    def __init__(self, api, author=None, custom_fields=None, # pylint: disable=R0913
                  sprint_milestone=None, category=None, status=None, 
                  company=None, created_on=None, description=None, 
                  subject=None, done_ratio=None, crm_reply_token=None, 
                  updated_on=None, id=None, project=None, contact=None, 
                  priority=None, due_date=None, estimated_hours=None, 
                  tracker=None, parent=None, closed_on=None, start_date=None,
                  tracking_uri=None, assigned_to=None):  
        
        self._api = api
        
        self.author = author
        self.custom_fields = custom_fields
        self.sprint_milestone = sprint_milestone  
        self.category = category
        self.status = status
        self.company = company
        self.created_on = created_on
        self.description = description
        self.subject = subject
        self.done_ratio = done_ratio
        self.crm_reply_token = crm_reply_token
        self.updated_on = updated_on
        self.id = id
        self.project = project
        self.contact = contact
        self.priority = priority
        self.due_date = due_date
        self.estimated_hours = estimated_hours
        self.tracker = tracker
        self.parent = parent
        self.closed_on = closed_on
        self.start_date = start_date
        self.tracking_uri = tracking_uri
        self.assigned_to = assigned_to
        self.modified_on = self.updated_on
        
        self.subtasks = []

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['_api']
        return d

    def __setstate__(self, state):
        self.__dict__.update(state)
            
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        na1 = object()
        na2 = object()
        for _, attr, _ in self._issue_parse_tbl:
            v1 = getattr(self, attr, na1)
            v2 = getattr(other, attr, na2)
            if v1 != v2:
                return False
        return True

    def _get_users(self):
        users = []
        for _, attr, _ in self._issue_parse_tbl:
            v = getattr(self, attr)
            if isinstance(v, User):
                users.append(v)
        return users
        
    def __hash__(self):
        s = ":".join(repr(getattr(self, a)) for _, a, _ in \
            self._issue_parse_tbl)
        return hash(s)
                

    @classmethod
    def from_json(cls, api, **kw):
        dct = {}
        absent = object()
        for k, attr, func in cls._issue_parse_tbl:
            v = kw.pop(k, absent)
            if v is absent:
                continue
            if func:
                try:
                    v = func(api, attr, v)
                except Exception:
                    print(dct, kw)
                    raise
            dct[attr] = v
        self = cls(api, **dct)
        if kw:
            for k, v in kw.items():
                setattr(self, k, v)
            #print("Warning: unrecognized keyword: %s=%s"%(k,v))
        return self
    
    def add_subtask(self, issue):
        self.subtasks.append(issue)

    def pretty_print(self):
                
        attrs = [t[1] for t in self._issue_parse_tbl]
        args = ", ".join("%s=%s" % (a, _reprify(getattr(self, a), self)) for a in attrs)
        args = args or '<empty>'
        cn = self.__class__.__name__
        return "%s(%s)" % (cn, args)

    def download(self):
        return self._api.download_issue_pdf(self.id)
    
    __str__ = __repr__ = pretty_print
