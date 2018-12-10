
# coding: utf-8

from exceptions import MergeError, SanityError
from lv_parse import fromfn, flatten
from os.path import basename as _bn

class NotFound(KeyError):
    """ Signal that variable was not found in the list.
    To be raised by user code as a signal to `compare_lists`. 
    """
    pass

NotFoundErrors = (NotFound, KeyError, IndexError)

# Ongoing TODO is convert everything to class based system.
# Originally everything was done on a per file basis, but
# as the project has developed, common code can be merged
# together to sensibly form a class-based scheme to simplify
# some of the boilerplate. 

class OutFormatter():
    """ Rather than having the _merge() function 
    do the outputting itself, it turns out to be a bit neater for 
    complex subclassing (cough merge_recipes cough) to keep
    the logging info around to adjust later. 

    This means that to keep things simplest, the line
    lengths are determined when the print function is called,
    rather than ahead of time. 
    """
    def __init__(self, lines=()):
        self.lines = lines or []

    def print(self, print_func=print):
        wv, w1, w2, w3, w4 = self.calc_widths()
        return self.print2(wv, w1, w2, w3, w4, print_func)
    
    def calc_widths(self):
        wvar = len("Variable")
        w1 = w2 = w3 = w4 = 10  # defaults
        for a, b, c, d, e, _ in self.lines:
            wvar = max(wvar, len(a))
            w1   = max(w1, len(b))
            w2   = max(w2, len(c))
            w3   = max(w3, len(d))
            w4   = max(w4, len(e))
        return wvar, w1, w2, w3, w4

    def print2(self, wvar, w1, w2, w3, w4, print_func=print):
        linefmt = "%%-%ds: %%-%ds| %%-%ds| %%-%ds| %%-%ds| %%s " % (wvar + 1, w1, w2, w3, w4)
        header1 = "%-*s  %-*s  %-*s  %-*s  %-*s  " % (wvar + 1, "", w1, "", w2, "Contents", w3, "", w4, "Matches") + "Restore"
        header2 = linefmt%("Variable", "Cust File", "Old File", "New File", "USR  OLD", "Action")
        header3 = len(header2) * "-"

        print_func(header1)
        print_func(header2)
        print_func(header3)

        for l in self.lines:
            print_func(linefmt%l)

class CSVFormatter(OutFormatter):
    def print(self, print_func=print):
        header = ",".join(("Variable", "Customer File", "Old Defaults", "New Defaults", "USR OLD", "Action"))
        print_func(header)
        for l in self.lines:
            print_func(",".join(map(str, l)))


class Merger():
    """
    Class based file merging.

    Overrides for subclassing - 

        var handling:
            getvar
            setvar
            v2s
            notfound
            vequal
            force_handler
        io: 
            parse
            sanitycheck
            output

    """
    FormatterClass = CSVFormatter

    def __init__(self, options):
        self.options = options
        self.cf = None
        self.of = None
        self.nf = None
        self.out = self.options.v
        self.outlogger = None
        if isinstance(self.options.logfile, str) and self.options.logfile.endswith(".csv"):
            self.FormatterClass = CSVFormatter
            self.fn_full_fn = True
        else:
            self.FormatterClass = OutFormatter
            self.fn_full_fn = False

    @classmethod
    def run_merge(cls, options):
        """ 
        Create & run class in one function call,
        e.g. pass to file_types.register()
        """
        return cls(options).merge()

    # callbacks
    def getvar(self, f, name):
        if f == self.nf:
            return f[name]
        else:
            if name in f:
                n = name
            else:
                n = self.options.translate_new[name]
                if n not in f:
                    raise KeyError(n)
            return f[n]

    def write_file(self):
        """ Boilerplate code to handle message & opening
        file. Can be overridden if you really need...
        """
        # self.out("\nWriting output to \"%s\"" % self.options.outf)
        output = self.output(self.nf)
        with open(self.options.outf, 'w') as f:
            f.write(output)

    def output(self, f):
        raise NotImplementedError()

    def notfound(self, _):
        return None

    def setvar(self, f, name, value):
        f[name] = value

    def v2s(self, name, v):
        return str(v)

    def vequal(self, a,b):
        return a == b

    def force_handler(self, n):
        setvar = self.setvar
        getvar = self.getvar
        v2s = self.v2s
        # handle force & such here
        if n in self.options.use_new:
            skip = (v2s(n, getvar(self.cf, n)), v2s(n, getvar(self.of, n)), v2s(n, getvar(self.nf, n)), "", "new") 
        elif n in self.options.use_user:
            v = getvar(self.nf, n)
            cv = getvar(self.cf, n)
            skip = (v2s(n, cv), v2s(n, getvar(self.of, n)), v2s(n, v), "", "usr")
            setvar(self.nf, n, getvar(self.cf, n))
        elif n in self.options.force:
            setvar(self.nf, n, self.options.force[n])
            skip = ("", "", v2s(n, getvar(self.nf, n)), "", "force")
        elif n in self.options.newvar:
            skip = ("", "", v2s(n, getvar(self.nf, n)), "", "")
        else:
            skip = None
        return skip

    def parse(self, ff):
        raise NotImplementedError()

    def sanitycheck(self):
        """ Default sanity checks 
        If this is overridden, the new implementation can probably
        still call this default before implementing custom behavior. 
        """
        # like for _merge(), unpack here to ease migration
        cf = self.cf
        of = self.of
        nf = self.nf
        new = self.options.use_new
        user = self.options.use_user
        force = self.options.force
        tn = self.options.translate_new
        to = self.options.translate_old
        newvar = self.options.newvar
        depr = self.options.depreciated

        def dup(c, *others):
            for n in c:
                for o in others:
                    if n in o:
                        raise SanityError("Got duplicate variable: %s"%n)
        def check(c):
            for n in c:
                if n not in nf:
                    raise SanityError("Bad variable for new file: %r"%n)
        def check2(c):
            for n in c:
                if n not in of:
                    raise SanityError("Bad variable for old file: %r"%n)

        check(new)
        check(user)
        check(force)
        check(tn)
        check(newvar)
        check2(to)
        check2(depr)
        check2(cf)
        dup(new, user, force)
        dup(user, new, force)
        dup(force, new, user)

    def post_parse(self):
        pass  # hook

    def merge(self):
        self.cf = self.parse(self.options.cff)
        self.of = self.parse(self.options.off)
        self.nf = self.parse(self.options.nff)
        self.post_parse()
        self.sanitycheck()
        self._merge()
        self.write_log()
        self.write_file()

    def write_log(self):
        self.outlogger.print(self.out)

    def _merge(self):
        # some attribute unpacking here will simplify
        # the process of migrating this from the merge_lists2
        # function
        cf               = self.cf
        of               = self.of
        nf               = self.nf
        getvar           = self.getvar
        force_handler    = self.force_handler
        vequal           = self.vequal
        notfound         = self.notfound
        setvar           = self.setvar
        var2str          = self.v2s

        self.outlogger = self.FormatterClass()
        olines = self.outlogger.lines
        
        if self.fn_full_fn:
            olines.append(("Filename", self.options.cff, self.options.off, self.options.nff, "", ""))
        else:
            olines.append(("Filename", _bn(self.options.cff), _bn(self.options.off), _bn(self.options.nff), "", ""))

        for name in nf:
            msg = force_handler(name)
            if msg:
                cs, os, ns, m, a = msg
            else:
                nv = getvar(nf, name)
                try:
                    cv = getvar(cf, name)
                    ov = getvar(of, name)
                except NotFoundErrors:
                    msg = notfound(name)
                    if msg is not None:
                        cs, os, ns, m, a = msg
                    else:
                        # XXX Refactor this so it doesn't look like ass
                        try:
                            cs = var2str(name, getvar(cf, name))
                        except NotFoundErrors:
                            cs = "???"
                        try:
                            os = var2str(name, getvar(of, name))
                        except NotFoundErrors:
                            os = "???"
                        ns = var2str(name, nv)
                        m = "NOTFOUND"
                        a = "new"
                else:

                    # this logic can be reduced into less than 10
                    # lines if the logging wasn't needed,
                    # but it makes it hard to get the correct logic
                    # or output, since the sequence of conditions
                    # is somewhat important.

                    # I actually tried to re-write it making smart use of 
                    # nested if statements instead of repeatedly checking
                    # the same conditions over and over, but it actually 
                    # ended up being one line longer. 

                    cs = os = ns = ""
                    nv_ov = vequal(nv, ov)
                    nv_cv = vequal(nv, cv)
                    cv_ov = vequal(cv, ov)
                    
                    if nv_ov and cv_ov:                
                        m  = "No Change"
                        a  = "new"
                    elif not nv_ov and cv_ov:
                        cs = var2str(name, cv)
                        os = var2str(name, ov)
                        ns = var2str(name, nv)
                        m  = "N    N"     
                        a  = "new"    
                    elif nv_ov and not cv_ov:          
                        # Conflict
                        cs = var2str(name, cv)
                        os = var2str(name, ov)
                        ns = var2str(name, nv)
                        m  = "N    Y"
                        a  = "usr"
                        setvar(nf, name, cv)
                    elif nv_cv and not cv_ov:
                        cs = var2str(name, cv)
                        os = var2str(name, ov)
                        ns = var2str(name, nv)
                        m  = "Y    N"
                        a  = "new"
                    elif not nv_cv and not cv_ov:
                        # Conflict
                        cs = var2str(name, cv)
                        os = var2str(name, ov)
                        ns = var2str(name, nv)
                        m  = "N    N"
                        a  = "usr"
                        setvar(nf, name, cv)
                    else:
                        # should be unreachable
                        raise SanityError("Unreachable code for %r"%name)
            olines.append((name, cs, os, ns, m, a))


class LVXMLMerger(Merger):
    """ The same code should be usable for 
    any and all files that use LabVIEW's
    bastardized XML scheme. 

    Currently used only for System Variables
    and Cal Factors. 
    """
    def parse(self, ff):
        LV = fromfn(ff)
        d  = flatten(LV)

        # keep this reference around for
        # outputting to file. The merge 
        # algorithm modifies the mutable 
        # LVType objects directly, which
        # avoids needing to convert the
        # flattened list back to an LVType
        # hierarchy in the output function. 

        # note this works because flatten
        # returns an ordered dict - builtin
        # dict can't assign arbitrary attr.
        # create a subclass of dict here 
        # if this changes.

        d.LV = LV
        return d

    def post_parse(self):
        # convert values in the force 
        # dict to LVTypes.
        frc = self.options.force
        for n, v in frc.items():
            v2 = self.nf[n]
            new = v2.__class__(v2.type, v2.name, v)
            frc[n] = new

    def v2s(self, n, v):
        return v.tostr()

    def setvar(self, f, n, v):
        f[n].val = v.val

    def vequal(self, a, b):
        return a.tostr() == b.tostr()

    def output(self, f):
        return f.LV.toxml()

