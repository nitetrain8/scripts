"""

Created by: Nathan Starkweather
Created on: 02/05/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import re

__VARS_FILE__ = "C:\\Users\\PBS Biotech\\Documents\\Personal\\test files\\logger settings.cfg"
VARS_FILE = __VARS_FILE__


def load_logger_vars(file: str=VARS_FILE) -> list:

    """
    @param file: file containing an example logger file,
                        from which to extract all settings.
    @return: list of all settings, as would be found in a recipe.
    """

    with open(file, 'r') as f:
        f.readline()  # discard header
        body = f.read()

    # tab delimited columns
    line_start_to_tab = r"^([^\t]*)"
    vars = [v for v in re.findall(line_start_to_tab, body, re.MULTILINE) if v.strip()]
    return vars


def raw_to_pynames(vars: list) -> dict:
    """
    @param vars: list of strings representing vars
    @return: dict mapping python-legal name to var

    Map raw variable names to a python-legal and
    relatively equivalent name.
    """

    # match whitespace, periods, "&", stuff in parenthesis
    str_to_pyname = r"[\s*\.\&]|\(.*?\)"
    pynames = {re.sub(str_to_pyname, '', var) : var for var in vars}
    return pynames


class RecipeVariable():
    """
    @param recipe_var_name: name of property

    Create an object that returns a string
    corresponding to a recipe step for
    "wait until" steps.

     ex: temppv = LoggerProp("TempPV(C)")
         print(temppv > 5)
         >>> "wait until 'TempPV(C)' > 5"
    """

    step_template = 'Wait until "{var}" {cmp} {val}'

    def __init__(self, recipe_var_name: str):
        self._name = recipe_var_name

    @property
    def Name(self):
        """
         @rtype: str
        """
        return self._name

    name = Name

    def wait_until(self, cmp: str, val) -> str:
        return self.step_template.format(
                                        var=self._name,
                                        cmp=cmp,
                                        val=val
                                        )

    def __lt__(self, val):
        """ < """

        return self.wait_until("<", val)

    def __le__(self, val):
        """ <= """
        return self.wait_until("<=", val)

    def __eq__(self, val):
        """ == """
        return self.wait_until("=", val)

    def __ne__(self, val):
        """ != """
        return self.wait_until("!=", val)

    def __gt__(self, val):
        """ > """
        return self.wait_until(">", val)

    def __ge__(self, val):
        """ >= """
        return self.wait_until(">=", val)

__vars = load_logger_vars()
__pynames = raw_to_pynames(__vars)
__pydict = {pyname : RecipeVariable(varname) for pyname, varname in __pynames.items()}


# debug
if __name__ == '__main__':

    from os.path import split
    base, name = split(__file__)
    outfile = '/'.join((base, 'vartest.txt'))
    # outfile = "C:\\Users\\PBS Biotech\\Documents\\Personal\\test files\\vartest.txt"
    # globals().update(__pydict)
    # with open(outfile, 'w') as f:
    #     for k in __pydict:
    #         print(k, eval("%s > 5" % k), file=f)

    from collections import OrderedDict
    __jsondict = OrderedDict(((k, v) for k, v in sorted(__pynames.items())))
    # # pynames: dict pyname : varname
    # more = {}
    # for pyname, varname in __jsondict.items():
    #     more[pyname.lower()] = varname
    #     more[pyname.upper()] = varname
    #
    # __jsondict.update(more)
    __jsondict = list(__jsondict.items())
    __jsondict.sort(key=lambda x: x[1])
    from pysrc.snippets import safe_json
    safe_json(__jsondict, outfile)
    from officelib.nsdbg import npp_open
    npp_open(outfile)
