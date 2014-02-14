"""

Created by: Nathan Starkweather
Created on: 02/13/2014
Created in: PyCharm Community Edition


"""
from scripts.recipemaker import Recipe, LongRecipe

FULL_TEST_START_TEMP = 28


def make_auto2auto(pgain, itime, dtime):

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


def make_full_test_body(pgain, itime, dtime, sp):
    """
    @param pgain: pgain
    @type pgain: float | int
    @param itime: itime
    @type itime: float | int
    @param dtime: dtime
    @type dtime: float | int
    @param sp: temp setpoint
    @type sp: float | int
    @return: Recipe
    @rtype: Recipe
    """
    recipe = Recipe()
    recipe.set("TempHeatDutyControl.PGain(min)", pgain)
    recipe.set("TempHeatDutyControl.ITime(min)", itime)
    recipe.set("TempHeatDutyControl.DTime(min)", dtime)
    recipe.set("TempSP(C)", sp)
    recipe.wait(5)
    recipe.set("TempModeUser", "Auto")
    recipe.waituntil('TempPV(C)', ">=", sp)
    recipe.wait(3600)
    recipe.set("TempSP(C)", sp + 2)
    recipe.wait(5)
    recipe.waituntil("TempPV(C)", ">=", sp + 2)
    recipe.wait(3600)
    recipe.set("TempModeUser", "Off")
    recipe.wait(5)
    recipe.waituntil("TempPV(C)", "<=", FULL_TEST_START_TEMP)
    return recipe

__long_recipe_start = Recipe()
__long_recipe_start.set("TempModeUser", "Off")
__long_recipe_start.wait(5)
__long_recipe_start.set("TempSP(C)", FULL_TEST_START_TEMP + 2)
__long_recipe_start.wait(5)
__long_recipe_start.set("TempModeUser", "Auto")
__long_recipe_start.wait(5)
__long_recipe_start.waituntil("TempPV(C)", ">", FULL_TEST_START_TEMP + 1)
__long_recipe_start.set("TempModeUser", "Off")
__long_recipe_start.waituntil("TempPV(C)", "<=", FULL_TEST_START_TEMP)

LONG_RECIPE_START_STEPS = len(__long_recipe_start)


def get_long_recipe_start():
    """
    @return: long recipe's buffer list
    @rtype: list[str]
    """
    return __long_recipe_start.buffer.copy()


def make_long_recipe(settings):
    """
    @param settings: iterable of tuples of (p, i, d) settings.
    @type settings: collections.Iterable[(int | float, int | float, int | float)]
    @return:
    """
    recipes = [make_full_test_body(p, i, d, 37) for p, i, d in settings]

    long = LongRecipe()
    long.add_recipe(__long_recipe_start)
    long.extend_recipes(recipes)
    long_recipe = str(long)

    return long_recipe


if __name__ == '__main__':

    # functions to generate specific recipes
    def test_ratio_no_d() -> list:
        """
        @return: list of settings with constant ratio.
        """
        ps = [p for p in range(40, 65, 5)]
        settings = [(p, p / 10, 0) for p in ps]
        return settings

    def test_d_settings():
        """
        @return: List of settings for this test
        """
        ds = (0.1, 0.05, 0.01, 0.005, 0.001, 0.0005)
        settings = [(32.5, 3.25, d) for d in ds]
        settings.append((50, 5, 0))
        settings.append((60, 6, 0))
        return settings

    # settings = test_d_settings()
    # recipe = make_long_recipe(settings)
    settings = test_ratio_no_d()
    recipe = make_long_recipe(settings)
    outfile = "C:\\Users\\Public\\Documents\\PBSSS\\Functional Testing\\tpid.txt"
    from officelib.nsdbg import npp_open
    print(recipe, file=open(outfile, 'w'))
    npp_open(outfile)


    # print(recipe)
