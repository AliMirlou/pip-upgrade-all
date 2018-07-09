#!/bin/python3
from pip._internal import main
import sys
from argparse import ArgumentParser
from io import StringIO
from contextlib import redirect_stdout

outdated = []
exclude = []
global_options = ['--disable-pip-version-check']
args = None


def check_outdated_packages():
    f = StringIO()
    with redirect_stdout(f):
        main(['list', '--outdated', '--format=columns'] + global_options)
    return f.getvalue().split('\n')[3:-1]


def update(package_index):
    package = outdated[package_index]
    package_name = package[0].lower()
    package_new_version = package[1]
    if package_name in exclude:
        raise Exception("Package is excluded" % package_name)
    sys.stdout.flush()
    options = ['--upgrade'] + global_options
    if args.ignore_stdout:
        print("Updating %s to version %s... " % (package_name, package_new_version), end='')
        options.append('--no-progress-bar')
    f = StringIO()
    with redirect_stdout(f):
        a = main(['install', *options, '%s==%s' % (package_name, package_new_version)])
    if a == 2:
        choice = input("Python needs to be elevated with UAC in order to continue. "
                       "Do you want to give access? [y,N] ")
        if choice.lower() == 'y':
            import pyuac
            a = pyuac.run_as_admin()
            if a != 0:
                raise PermissionError("There seems to be a problem elevating python with UAC!")
        else:
            raise PermissionError("Permission Denied")
    if not args.ignore_stdout:
        print(f.getvalue())
    else:
        print("Completed")


def update_all():
    for package_index in range(len(outdated)):
        update(package_index)
    print("All packages are updated")


def create_outdated_list(_list):
    index = 1
    for package in _list:
        package = package.split()
        print('%d) %s\t\t\t%s --> %s (%s)' % (index, package[0], package[1], package[2], package[3]))
        outdated.append([package[0], package[2]])
        index += 1


def choice_menu():
    choice = input("\nWhich package do you want to update? [all,<number,>,NONE] ")
    if choice == 'exit':
        return False
    if choice == 'all':
        choice = input("\nAre you sure to update all outdated packages? [y,N] ")
        if choice == 'y':
            update_all()
            return True
    choices = map(int, choice.split(','))
    for choice in choices:
        try:
            update(choice - 1)
        except IndexError:
            print("Error: Choice out of range")
        except Exception as e:
            print(e)
    return True


if __name__ == "__main__":
    parser = ArgumentParser(prog='pip-upgrade-all',
                            description='Gives you the ability to update all or some packages '
                                        'installed on pip with interactive menu',
                            epilog='Created by Ali Mirlou')
    parser.add_argument('-s', '--ignore_stdout', help="Silences the output of pip's logging of upgrade progress.",
                        action='store_true')
    parser.add_argument('-i', '--interactive', help='Runs the app in a loop till exit or keyboard interrupt.',
                        action='store_true')
    parser.add_argument('-backup', '--backup', help='Backs up all installed packages.',
                        action='store_true')  # TODO
    parser.add_argument('-e', '--exclude', nargs='+', help='Excludes the entered package names from updating.',
                        dest='package_name')  # TODO
    args = parser.parse_args()

    try:
        exclude_file = open("exclude.txt").readlines()
        for i in exclude_file:
            exclude.append(i.lower())
    except FileNotFoundError:
        pass

    print("Searching for outdated packages... ", end='')
    sys.stdout.flush()
    output = check_outdated_packages()
    print("Completed")

    print("Outdated packages: ")
    create_outdated_list(output)

    while choice_menu():
        if not args.interactive:
            break
