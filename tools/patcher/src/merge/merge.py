
import os
import os.path
import argparse
import sys

from parse_config import parse_config

# The merge handlers file is an auto-generated list of all
# files which (should) contain handlers to register with
# file-types. Importing it causes the other modules to be
# imported. On import, each module registers any handlers
# it has with file_types. 

# enforce the proper load order
from file_types import get_types, load_function
import exceptions
import merge_handlers
import mlogger

def main(options):
    if not options.sanitycheck(get_types()):
        if options.verbose:
            print("Error: failed sanity check")
        return -3

    func = load_function(options.type)
    logger = mlogger.Logger(options.verbose, options.logfile)
    options.v = logger.log
    try:
        return func(options)
    except exceptions.SanityError as e:
        logger.log("Error: %s"%e.args[0])
        return -3
    except exceptions.MergeError as e:
        logger.log("Error: %s"%e.args[0])
        return -1


def batch_mode_main1(metafile):
    # batch mode where each line in the input file 
    # is a patch file containing ALL information
    with open(metafile, 'r') as f:
        lines = f.read().splitlines()
    rv = 0
    for patch in lines:
        options = parse_config(patch)
        if options.verbose:
            print("Running batch mode for type '%s'..."%options.type)
        res = main(options)
        if res:
            if options.verbose:
                print("Error(%d) running file '%s'"%(res, patch))
            rv = -4
    return rv


def batch_mode_main2(metafile):
    
    """ Batch mode where each line in the input file
    is a comma separated list of input args 
    aka sys.argv[1:] = line.split(",")
    note that CSV format is not RFC compliant, commas
    in filenames will cause problems
    """

    with open(metafile, 'r') as f:
        lines = f.read().splitlines()
    rv = 0
    for argstr in lines:
        args = argstr.split(",")
        #print(args)
        ops = parse_args(args)
        if ops.verbose:
            print("Running batch mode for type '%s'..."%ops.type)
        res = main(ops)
        if res:
            rv = -5
            if ops.verbose:
                print("Error(%d) running batch mode"%res)
    return rv

# def fix(arg,unkn):
#     if unkn:
#         ext1 = os.path.splitext(arg.new_defaults)[1]
#         ext2 = os.path.splitext(arg.user_file)[1]
#         maybe = arg.user_file + "," + arg.old_defaults
#         if os.path.exists(maybe):
#             d = arg.__dict__.copy()
#             d['new_defaults'] = unkn[0]
#             d['user_file'] = maybe
#             d['old_defaults'] = arg.new_defaults
#             return argparse.Namespace(**d)
#     return arg

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("patch",        help="Name of patch file")
    parser.add_argument("user_file",    help="Path to user config file")
    parser.add_argument("old_defaults", help="Path to default config file for user's current software version")
    parser.add_argument("new_defaults", help="Path to new default config file")
    parser.add_argument("--outf",       help="Output file")
    parser.add_argument("--type",       help="File type. Values are %s"%", ".join("'%s'"%v for v in get_types()), choices=get_types())
    parser.add_argument("--verbose",    help="Verbose", action='store_true')
    parser.add_argument("--logfile",    help="Log file")
    args, unkn = parser.parse_known_args(args)

    # add command line arguments to options.
    # command line overrides defaults set by patch file

    options             = parse_config(args.patch, unkn)
    options.outf        = args.outf or options.outf.format(filename=os.path.basename(args.user_file))
    options.logfile     = args.logfile or options.logfile
    if options.logfile:
        options.logfile = options.logfile.format(filename=os.path.basename(args.user_file))
    options.cff         = args.user_file or options.cff
    options.off         = args.old_defaults or options.off
    options.nff         = args.new_defaults or options.nff
    options.type        = args.type or options.type
    options.verbose     = args.verbose or options.verbose
    return options

if __name__ == "__main__":
    # Support special batch modes.
    # Because the PyInstaller EXE has to unzip
    # and delete temporary files each time it runs,
    # allowing batch modes to run can eliminate
    # a lot of time. It turns out to take ~0.5-0.8
    # seconds even on my machine to run a single test
    # case in EXE mode from the unittest suite, so in
    # production, this option may greatly speed up 
    # the process if it is used.
    if len(sys.argv) == 3:
        if sys.argv[1] == "batchmode1":
            sys.exit(batch_mode_main1(sys.argv[2]) or 0)
        elif sys.argv[1] == "batchmode2":
            sys.exit(batch_mode_main2(sys.argv[2]) or 0)
    ops = parse_args(sys.argv[1:])
    sys.exit(main(ops) or 0)
