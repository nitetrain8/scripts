""" Simple recipe maker module.
"""


class Recipe():
    """ Recipe maker."""
    def __init__(self):
        self.buffer = []

    def write(self, code):
        """
        @param code: code to write
        @type code: str
        """
        self.buffer.append(code)

    def set(self, param, value):
        """
        @param param: variable to set
        @type param: str
        @param value: value to set it to
        @type value: str | int | float
        """
        self.write("Set \"%s\" to %s" % (param, str(value)))

    # alias
    Set = set

    def waituntil(self, param, op, val):
        """
        @param param: parameter to wait for
        @type param: str
        @param op: wait operation
        @type op: str
        @param val: value to wait for
        @type val: str | int | float
        """
        self.write("Wait until \"%s\" %s %s" % (param, op, str(val)))

    def wait(self, sec):
        """
        @param sec: seconds to wait
        @type sec: int
        """
        self.write("Wait %d seconds" % sec)

    def __str__(self):
        return '\n' + '\n'.join(self.buffer)

    def __len__(self):
        return len(self.buffer)


class LongRecipe(Recipe):
    """ Chain together multiple recipes
    """

    def add_recipe(self, recipe):
        """
        @param recipe: recipe to add
        @type recipe: Recipe
        @return: None
        @rtype: None
        """
        self.buffer.extend(recipe.buffer)

    def extend_recipes(self, recipe_list):
        """
        @param recipe_list: list of recipes to add
        @type recipe_list: collections.Iterable[Recipe]
        @return: None
        @rtype: None
        """
        for recipe in recipe_list:
            self.buffer.extend(recipe.buffer)
