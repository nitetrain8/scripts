class ConverterError(Exception):
    pass

class _RedmineConverter():
    """ Simple Newtonsoft.Json inspired 
    JSON deserializer. A fancier version is in
    a helix_client_test notebook floating around,
    but this one is good enough for Redmine. 
     
    # Unsure why I used this particular design
    (single instance of class rather than singleton)
    but it works the same. 
    """
    def __init__(self):
        self._converters = {}
        
    def Register(self, kls):
        self._converters[kls] = dict(kls._converter_table)
        return kls  # allow function use as decorator
        
    def Deserialize(self, jobj, kls):
        try:
            tbl = self._converters[kls]
        except KeyError:
            raise
        
        obj = kls()
        for key, val in jobj.items():
            conv = tbl.get(key)
            if conv:
                if conv in self._converters:
                    val = self.Deserialize(val, conv)
                else:
                    val = conv(val)
            else:
                pass
                # pass : use val as-is (string)
            setattr(obj, key, val)
            
        for key in tbl.keys():
            if key not in jobj:
                setattr(obj, key, None)
        return obj
            
RedmineConverter = _RedmineConverter()  