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
    type=str)
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
    runner.handle_scheme(args.scheme)
elif args.install is not None and args.dir is not None and args.venv is not None:
    if args.install == "scheme":
        desktop.create_application(args.dir, args.venv)
    elif args.install == "launcher":
        desktop.create_handler(args.dir, args.venv)
    else:
        parser.print_help()
elif args.run:
    runner.try_acquire()
    pass
else:
    parser.print_help()