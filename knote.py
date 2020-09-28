import sys
import argparse

from knote_cmds import new_cmd, remove_cmd, edit_cmd, open_cmd, list_cmd, configure_cmd, open_current_cmd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="knote")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-n", "--new", action="store_true", help="add new subject")
    group.add_argument("-r", "--remove", nargs=1, help="remove a subject")
    group.add_argument("-e", "--edit", nargs=1, help="edit a subject")
    group.add_argument("-o", "--open", nargs=1, help="open a specific subject")
    group.add_argument("-l", "--list", action="store_true", help="list all subjects" )
    group.add_argument("-c", "--configure", action="store_true", help="configure json file")
    
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as exc:
        print(exc.message)

    if args.new:
        new_cmd()
    elif args.remove != None:
        remove_cmd(args.remove[0])
    elif args.edit != None:
        edit_cmd(args.edit[0])
    elif args.open != None:
        open_cmd(args.open[0])
    elif args.list:
        list_cmd()
    elif args.configure:
        configure_cmd()
    else:
        open_current_cmd()

    sys.exit(0)
