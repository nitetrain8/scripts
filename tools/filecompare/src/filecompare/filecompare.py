import comparer
from comparer import compare
import argparse
import sys
import os


def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument("type", help="Type of argument", choices=comparer.get_types())
    p.add_argument("--log", "--logfile", help="output file for log")
    p.add_argument("--fmt", "--outfmt", help="type of output format", choices=comparer.get_out_fmts(), default="txt")
    p.add_argument("--values", "--always_values", "--always_show_values", help="always show values in columns " \
                                                "even if they match the reference", 
                                                action="store_true", default=False)
    p.add_argument("--names", "--always_names", "--always_show_names", help="always show output for variables even if " \
                                             "every files' value matches the reference file.",
                                             action="store_true", default=False)
    p.add_argument("--err", "--err_on_notfound", help="Throw an error if a variable isn't found in one of the "\
                                             "test files. Otherwise, just print an error message.",
                                             action="store_true", default=False)
    p.add_argument("--verbose", "--v", help="verbose", action="store_true", default=False)
    p.add_argument("--minw", help="Min column width", type=int, default=10)
    p.add_argument("--maxw", help="Max column width for value columns", type=int, default=20)
    p.add_argument("--ignore", help="Comma separated string of names to ignore", default="")
    args, remaining = p.parse_known_args(args)

    p2 = argparse.ArgumentParser()
    p2.add_argument("ref", help="Reference file")
    p2.add_argument("files", help="Files to compare", nargs="+")
    args2 = p2.parse_args(remaining)
    return args, args2.ref, args2.files

def main_from_argv(args, ref, files):
    try:
        diff, res = compare(args.type, ref, *files, 
                        always_show_names=args.names,
                        always_show_values=args.values, 
                        err_on_notfound=args.err, 
                        outfmt=args.fmt,
                        minw=args.minw,
                        maxw=args.maxw)
        if not diff:
            _fn = os.path.basename
            res = "%-40s '%s', %s" %(args.type.title()+" identical: ", _fn(ref), ', '.join(("'%s'"%_fn(fi) for fi in files)))
            rv = 0
        else:
            rv = 1
        if args.log:
            with open(args.log, 'w') as f:
                f.write(res)
        if args.verbose:
            print(res)
    except Exception as e:
        print("ERROR: %s"%(e.args[0]))
        rv = -1
    return rv


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == 'batchmode':
        with open(sys.argv[2], 'r') as batchfile:
            largs = [s.split(',') for s in batchfile.read().splitlines()]
    else:
        largs=[sys.argv[1:]]
        if not largs:
            sys.exit(-2)
    retcode = 0
    for argv in largs:
        args, rf, files = parse_args(argv)
        res = main_from_argv(args, rf, files)
        if res < 0:
            print("ERROR(%d): Exiting"%res)
            sys.exit(res)
        else:
            retcode += res
        print()
    sys.exit(retcode)