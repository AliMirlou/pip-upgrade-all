#!/bin/python3
import platform
import pip
import sys
from argparse import ArgumentParser
from io import StringIO
from contextlib import redirect_stdout

outdated = []
args = None


def check_outdated_packages():
    f = StringIO()
    with redirect_stdout(f):
        pip.main(['list', '--outdated', '--format=columns'])
    return f.getvalue().split('\n')[3:-1]


def update(package_index):
    package = outdated[package_index]
    package_name = package[0]
    package_new_version = package[1]
    if platform.system() == 'Windows' and package_name in ['numpy', 'scipy']:
        print("Error: Package %s is skipped for compatibility issues on windows\n" % package_name)
        return False
    print("Updating %s to version %s... " % (package_name, package_new_version), end='')
    sys.stdout.flush()
    f = StringIO()
    options = ['--upgrade']
    if args.ignore_stdout:
        options.append('--no-progress-bar')
    with redirect_stdout(f):
        pip.main(['install', *options, '%s==%s' % (package_name, package_new_version)])
    print("Completed")
    if not args.ignore_stdout:
        print(f.getvalue())
    return True


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
    choice = input("\nWhich package do you want to update? [all,<number,>,exit] ")
    if choice == 'exit':
        return False
    if choice == 'all':
        choice = input("\nAre you sure to update all outdated packages? [y,<else>] ")
        if choice == 'y':
            update_all()
            return True
    choices = choice.split(',')
    for choice in choices:
        try:
            update(int(choice) - 1)
        except IndexError:
            print('Error: Choice out of range')


if __name__ == "__main__":
    parser = ArgumentParser(prog='pip-upgrade-all',
                            description='Gives you the ability to update all or some packages '
                                        'installed on pip with interactive menu',
                            epilog='Created by Ali Mirlou')
    parser.add_argument('-s', '--ignore_stdout', help="Silences the output of pip's logging of upgrade progress.",
                        action='store_true')
    parser.add_argument('-i', '--interactive', help='Runs the app in a loop till exit or keyboard interrupt.',
                        action='store_true')
    parser.add_argument('-e', '--exclude', nargs='+', help='Excludes the entered package names from updating.',
                        dest='package_name')  # TODO
    args = parser.parse_args()

    print("Searching for outdated packages... ", end='')
    sys.stdout.flush()
    output = check_outdated_packages()
    print("Completed")

    print("Outdated packages: ")
    create_outdated_list(output)

    while choice_menu():
        if not args.interactive:
            break
