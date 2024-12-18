import argparse
from install import desktop
from steam import runner

parser = argparse.ArgumentParser(
    prog='Path of Kakao',
    description='Acquire Kakao POE2 token',
    epilog='thx to pepsizerosugar from poe2 gallery'
    )
parser.add_argument(
    '-i', 
    '--install', 
    type=str,
    description='(scheme|desktop)')
parser.add_argument(
    '-s', 
    '--scheme', 
    type=str)
parser.add_argument(
    '-d', 
    '--dir', 
    type=str)
parser.add_argument(
    '-v', 
    '--venv',
    type=str)
parser.add_argument('-r', '--run', action='store_true')

args = parser.parse_args()

print(args)

if args.scheme is not None:
    runner.handle_scheme()
elif args.install is not None and args.dir is not None and args.venv is not None:
    match (args.install):
        case ["scheme"]:
            desktop.create_handler(args.dir, args.venv)
        case ["desktop"]:
            desktop.create_handler(args.dir, args.venv)
elif args.run:
    runner.try_acquire()
    pass
else:
    parser.print_help()