
class _TestIssue():
    def __init__(self, api, closed_on=None, parent=None, updated_on=None, assigned_to=None, priority=None, created_on=None, status=None, done_ratio=None, project=None, start_date=None, category=None, description=None, tracker=None, estimated_hours=None, due_date=None, author=None, custom_fields=None, id=None, subject=None, sprint_milestone=None, tracking_uri=None, company=None, contact=None, reply_token=None, **other):
        self.api = api
        self.closed_on = closed_on
        self.parent = parent
        self.updated_on = updated_on
        self.assigned_to = assigned_to
        self.priority = priority
        self.created_on = created_on
        self.status = status
        self.done_ratio = done_ratio
        self.project = project
        self.start_date = start_date
        self.category = category
        self.description = description
        self.tracker = tracker
        self.estimated_hours = estimated_hours
        self.due_date = due_date
        self.author = author
        self.custom_fields = custom_fields
        self.id = id
        self.subject = subject
        self.sprint_milestone = sprint_milestone
        self.tracking_uri = tracking_uri
        self.company = company
        self.contact = contact
        self.reply_token = reply_token
        for k,v in other.items():
            setattr(self, k, v)
        
    @classmethod
    def from_json(cls, api, js):
        return cls(api, 
                _iss_parse_datetime(js.get('closed_on')),
                _iss_parse_parent(js.get('parent')),
                _iss_parse_datetime(js.get('updated_on')),
                _iss_parse_user(js.get('assigned_to')),
                _iss_parse_resource(js.get('priority')),
                _iss_parse_datetime(js.get('created_on')),
                _iss_parse_resource(js.get('status')),
                js.get('done_ratio'),
                _iss_parse_project(js.get('project')),
                _iss_parse_datetime(js.get('start_date')),
                js.get('category'),
                js.get('description'),
                _iss_parse_resource(js.get('tracker')),
                js.get('estimated_hours'),
                _iss_parse_datetime(js.get('due_date')),
                _iss_parse_user(js.get('author')),
                _iss_parse_custom_fields(js.get('custom_fields')),
                _iss_parse_int(js.get('id')),
                js.get('subject'),
                _iss_parse_resource(js.get('fixed_version')),
                js.get('tracking_uri'),
                js.get('company'),
                js.get('contact'),
                js.get('reply_token'),
            )
    def __repr__(self):
        return "<%r'(id=%s, subject=%s)'>" % (self.__class__.__name__, self.id, self.subject)

class Issues():
    def __init__(self, api, it=()):
        super().__init__()
        self.api = api
        self.issues = list(it)
        self.id_to_ob = {i.id: i for i in self.issues}
    
    def _from_list(self, l, *oattr):
        cls = self.__class__
        ns = cls(self.api, l)
        for a in oattr:
            setattr(ns, a, getattr(self, a))
        return ns

    def copy(self):
        return self.__class__(self.api, self.issues)

    def __iter__(self):
        return iter(self.issues)
        
    def find(self, id=None):
        rv = []
        for i in self.issues:
            if id is not None and id != i.id: continue
            rv.append(i)
        return self._from_list(rv)
        
    def find2(self, **attr):
        rv = []
        _isinstance = isinstance
        _getattr = getattr
        _rv_append = rv.append
        for i in self.issues:
            for a,v in attr.items():
                if _isinstance(v, tuple):
                    if _getattr(i, a) in v:
                        _rv_append(i)
                else:
                    if _getattr(i, a) == v:
                        _rv_append(i)
        return self._from_list(rv)    
        
    def __getitem__(self, key):
        return self.lookup(key)

    def lookup(self, key):
        return self.id_to_ob[key]
        # return self.issues[key]

    @classmethod
    def from_json(cls, api, js):
        """ Primary public constructor """
        l = []
        for j in js:
            i = Issue.from_json(api, j)
            l.append(i)
        return cls(api, l)

    def add_issue(self, i):
        if i in self.issues:
            return
        self.issues.append(i)
        
    
    def __repr__(self):
        return "<%s Object: %d Issues>" % (self.__class__.__name__, len(self.issues))
        
    def index(self, i):
        return self.issues[i]    

    def __len__(self):
        return len(self.issues)                              
