import argparse

parser = argparse.ArgumentParser(prog='funds-rank', description='Show rank result of bond funds.')
parser.add_argument('-n', default=100, type=int, help='candidate funnds count, default is 100.')

parser.print_help()
args = parser.parse_args()
print(args.n)