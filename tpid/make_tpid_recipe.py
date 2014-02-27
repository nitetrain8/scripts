"""

Created by: Nathan Starkweather
Created on: 02/26/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from pbslib.recipemaker.tpid_recipes import *

if __name__ == '__main__':
    pgains = [30 + i / 10 for i in range(0, 200, 25)]
    print(pgains)

    itimes = (3, 3.5, 4, 4.5, 5, 6, 7)

    settings = []
    for p in pgains:
        for i in itimes:
            settings.append((p, i, 0))

    print(len(settings))

    settings = [(40, i, 0) for i in (5.5, 6, 6.5, 7)]

    r = many_with_pumps(settings)
    f = save_recipe(r)
    from os import startfile
    startfile(f)
