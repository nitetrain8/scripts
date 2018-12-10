"""
Recipe merging follows very different rules from the other 
config files. 

While some of it can be abstracted to use the same machinery, 
it is easier to just rewrite (most) of the logic and handle
the differences manually. It can be refactored later if need
be.

The high level approach to merging recipes uses basically
the same logic as other merge scripts, with the recipe name
as the 'key' and the steps within the recipe as the 'value'. 
The biggest difference is migrating a user's custom recipes 
from their old file to the new one. 

The biggest challenge with this process is ensuring that all
global names are actually valid. The easiest way to do this 
requires having a copy of the logger settings file, which 
contains all global names. This requires an extra command 
line argument, which doesn't play nicely with the 
rest of the cli, and requires special handling in merge.py. 

The way I decided to do this was to use parse_known_args()
instead of parse_args(), and attach the remainder of the 
un-parsed arguments to the options object. This file can
then use a second parser on the remaining argument(s) to
extract the logger settings file reference. 

One subtlety that arises is that there doesn't seem to be a 
restriction on recipe names, so we need to check for duplicate
names in the recipe list and bail if we encounter that. Since
only a super dumb ass would actually do that, this shouldn't
be a problem for real-world, but is trivial to implement. 

"""

import argparse
from cfg_compare import Merger
from collections import OrderedDict
from exceptions import SanityError
from itertools import zip_longest


class BaseStep():
    def __init__(self, var):
        self.var = var

    def tostr(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.tostr() == other.tostr()


class WaitStep(BaseStep):
    def __init__(self, time, unit):
        super().__init__(None)
        self.time = time
        self.unit = unit

    def tostr(self):
        return "Wait %s %s" % (self.time, self.unit)


class WaitUntilStep(BaseStep):
    def __init__(self, var, op, val):
        super().__init__(var)
        self.op = op
        self.val = val

    def tostr(self):
        return "Wait until \"%s\" %s %s"%(self.var, self.op, self.val)


class SetStep(BaseStep):
    def __init__(self, var, val):
        super().__init__(var)
        self.val = val

    def tostr(self):
        return "Set \"%s\" to %s"%(self.var, self.val)


class Recipe():
    def __init__(self, name, lines):
        self.name = name
        self.lines = lines
        self.steps = []
        for l in lines:
            self.create_step(l)

    def steps_with_vars(self):
        for step in self:
            if step.var is not None:
                yield step

    def __iter__(self):
        return iter(self.steps)

    def create_step(self, l):

        # fancy unpacking is like cheating
        # for splitting and rejoining strings
        # with known beginning and middle but
        # unknown number of middle segments. 
        # otherwise you'd need a bunch of code
        # or a regex to do this so easily

        svar = None
        if l.startswith("Wait"):
            if l.startswith("Wait until"):
                _, _, *var, op, val = l.split()
                svar = " ".join(var)
                s = WaitUntilStep(svar.strip('"'), op, val)
            else:
                _, time, unit = l.split()
                s = WaitStep(time, unit)
        elif l.startswith("Set"):
            _, *var, _, val = l.split()
            svar = " ".join(var)
            s = SetStep(svar.strip('"'), val)
        else:
            raise SanityError("Unknown step type for line: '%s'"%l)

        if svar is not None and (svar[0] != '"' or svar[-1] != '"'):
            raise SanityError("Parse failed for line: '%s'"%l)

        self.steps.append(s)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.name != other.name:
            return False
        return self.steps == other.steps

def _parse_recipes(recipes, lit, ff):
    while True:
        l = next(lit)
        if l == "":
            continue
        func, name = l.split(" ", 1)
        if func != "Func":
            raise SanityError("malformed file: '%s'"%ff)
        lines = []
        while True:
            l = next(lit, None)
            if not l:
                break
            lines.append(l)
        if not lines:
            continue
            #raise SanityError("Empty recipe in '%s': '%s'"%(ff, name))
        recipes[name] = Recipe(name, lines)


def _parse_logger(ff):
    # no sanity checking here since the
    # logger settings file is just for 
    # reference, not validation. 
    # Just don't retard. 
    with open(ff, 'r') as f:
        _ = f.readline()  # header
        lines = f.read().splitlines()
    settings = set()
    for l in lines:
        name, _ = l.split("\t", 1)
        settings.add(name)
    return settings


class RecipeMerger(Merger):

    def parse(self, ff):
        with open(ff, 'r') as f:
            lines = f.read().splitlines()
        recipes = OrderedDict()
        lit = iter(lines)
        try:
            _parse_recipes(recipes, lit, ff)
        except StopIteration:
            pass
        return recipes

    def sanitycheck(self):

        # other sanity checking is done during
        # the parsing phase
        out = self.options.v
        def check(file, fn, warning=False):
            for recipe in file.values():
                for i, step in enumerate(recipe.steps, 1):
                    if step.var is None:
                        continue
                    if step.var not in self.settings:
                        if warning:
                            out("Unknown variable '%s' in recipe '%s' line %d"%(step.var, recipe.name, i))
                        else:
                            raise SanityError("Invalid variable '%s' in file '%s'"%(step.var, fn))
        def checkvars(container):
            for var in container:
                if var not in self.settings:
                    raise SanityError("Bad variable name: '%s'"%var)
        check(self.cf, 'user', True)
        check(self.of, 'old')
        check(self.nf, 'new')
        checkvars(self.options.translate_new)
        checkvars(self.options.use_new)
        checkvars(self.options.use_user)
        checkvars(self.options.force)

    def convert_vars(self, f):
        
        # translate renamed variables to 
        # their new names and remove any
        # depreciated variables. 
        # Issue a warning whenever a depreciated
        # variable step is removed from a recipe

        # make a copy of the list for iteration
        # and remove steps from the original when
        # identified. Mutate step.var in place 
        # when translating names. 

        told = self.options.translate_old
        depr = self.options.depreciated
        out  = self.options.v
        for recipe in f.values():
            steps = recipe.steps.copy()
            for j, step in enumerate(steps, 1):
                var = step.var
                if var in depr:
                    out("Removing '%s' step %d with depreciated variable: '%s'"%(recipe.name, j, var))
                    recipe.steps.remove(step)
                else:
                    var = told.get(var, None)  # get told
                    if var is not None:
                        out("Translating '%s' step %d '%s' -> '%s'"%(recipe.name, j, step.var, var))
                        step.var = var

    def post_parse(self):
        """ Load the settings file and use
        the translate_old dict to translate names
        now rather than waiting. 

        When the files are sanity checked, they will
        all have the updated variable names (assuming
        of course that the patch file is correct :).     
        """
        self.settings = _parse_logger(self.options.loggersettings)
        self.convert_vars(self.cf)
        self.convert_vars(self.of)

    def _merge(self):
        """
        The merge logic here is somewhat different from
        the standard, since we expect customers to have
        their own custom recipes. 

        Perform merge in two passes:
        1. Fix the standard recipes by running through
        the default merge logic.

        2. Loop through customer's file for any non-default
        recipes and merge them into the new file. Skip 
        a recipe IF:
            * The user's copy is present in the old reference
            * The user's copy is not present in the new reference
            * the user's copy matches the old reference
        """
        super()._merge()
        cf = self.cf
        of = self.of
        nf = self.nf
        ol = self.outlogger.lines
        for name in cf:
            if name in nf:
                continue
            elif name in of:
                cv = cf[name]
                if cv == of[name]:
                    ol.append((name, "", "", "", "deprec", "skip"))
                    continue
                else:
                    ol.append((name, "", "", "N   N", "user"))
                    nf[name] = cv
            else:
                ol.append((name, "", "", "", "custom", "user"))
                nf[name] = cf[name]


    def v2s(self, name, v):
        return "Recipe('%s')"%v.name

    def output(self, f):
        buf = []
        for name, recipe in f.items():
            buf.append("Func %s"%name)
            for step in recipe:
                buf.append(step.tostr())
            buf.append("")
        buf.append("")  # files end with two blanks for some reason
        return "\n".join(buf)


def merge_recipes(options):
    p = argparse.ArgumentParser()
    p.add_argument("--loggersettings")
    args, other = p.parse_known_args(options.other)
    options.loggersettings = args.loggersettings
    options.other = other
    return RecipeMerger(options).merge()


from file_types import register
register("recipes", merge_recipes)