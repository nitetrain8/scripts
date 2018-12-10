
import argparse

def usage():
    print("merge [patch] [cff] [off] [nff] [outf]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("patch", help="Name of patch file")
    parser.add_argument("cff", help="Path to user config file")
    parser.add_argument("off", help="Path to default config file for user's current software version")
    parser.add_argument("nff", help="Path to new default config file")
    parser.add_argument("--outf", help="Output file")
    args = parser.parse_args()
    print(args.patch)
