""" Simple recipe maker module.
"""


class Recipe():

    """
    Recipe maker.
    """

    def __init__(self):
        self.buffer = []

    def write(self, code):
        """

        @param code:
        """
        self.buffer.append('\n' + code)

    def set(self, param, value):
        """

        @param param:
        @param value:
        """
        self.write("Set \"%s\" to " % param + str(value))

    Set = set

    def waituntil(self, param, op, val):
        """

        @param param:
        @param op:
        @param val:
        """
        self.write("Wait until \"%s\" %s " % (param, op) + str(val))

    def wait(self, sec):
        """

        @param sec:
        """
        self.write("Wait %d seconds" % sec)

    def __str__(self):
        return ''.join(self.buffer)


# noinspection PyDocstring
def make_recipe(pgain, itime, dtime):

    recipe = Recipe()
    recipe.set("TempHeatDutyControl.PGain(min)", pgain)
    recipe.set("TempHeatDutyControl.ITime(min)", itime)
    recipe.set("TempHeatDutyControl.DTime(min)", dtime)
    recipe.set("TempSP(C)", 39)
    recipe.waituntil('TempPV(C)', ">=", 39)
    recipe.wait(1200)
    recipe.set("TempSP(C)", 37)
    recipe.waituntil("TempPV(C)", "<=", 37)
    recipe.wait(1200)
    return recipe


def make_long_recipe(settings: list) -> str:
    """
    @param settings: iterable of tuples of (p, i, d) settings.
    @return:
    """
    recipes = []
    for p, i, d in settings:
        recipe = make_recipe(p, i, d)
        recipes.append(str(recipe))

    return ''.join(recipes)


def test_d_settings():
    """
    @return: List of settings for this test
    """
    ds = (0.1, 0.05, 0.01, 0.005, 0.001, 0.0005)
    settings = [(32.5, 3.25, d) for d in ds]
    settings.append((50, 5, 0))
    settings.append((60, 6, 0))
    return settings


def test_ratio_no_d():
    """
    @return: list of settings with constant
             ratio.
    """
    ps = [5 * i for i in range(1, 10)]
    settings = ((p, p / 10, 0) for p in ps)
    return settings

if __name__ == '__main__':
    settings = test_d_settings()
    recipe = make_long_recipe(settings)

    settings = test_ratio_no_d()
    recipe = make_long_recipe(settings)
    outfile = "C:\\Users\\Public\\Documents\\PBSSS\\Functional Testing\\tpid.txt"
    print(recipe, file=open(outfile, 'w'))
