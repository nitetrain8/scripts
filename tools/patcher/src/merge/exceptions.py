
class MergeError(Exception):
    """ Base Exception """

class SanityError(MergeError):
    """ Failed sanity check """