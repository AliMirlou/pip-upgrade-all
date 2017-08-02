import platform
import sys
import pip
from io import StringIO
from contextlib import redirect_stdout

outdated = []
ignore_stdout = False


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
    print("Updating %s to version %s..." % (package_name, package_new_version))
    f = StringIO()
    with redirect_stdout(f):
        pip.main(['install', '--upgrade', '%s==%s' % (package_name, package_new_version)])
    if not ignore_stdout:
        print(f.getvalue().split('\n'))
        print("Update Complete")
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
    choice = input("\nWhich library do you want to update? [all,<number,>,exit] ")
    if choice == 'exit':
        return
    if choice == 'all':
        choice = input("\nAre you sure to update all outdated packages? [y,<else>] ")
        if choice == 'y':
            update_all()
            return
    choices = choice.split(',')
    for choice in choices:
        try:
            update(int(choice)-1)
        except IndexError:
            print('Error: Choice out of range')

if __name__ == "__main__":
    print("Searching for outdated packages...")
    output = check_outdated_packages()

    print("Outdated packages: ")
    create_outdated_list(output)

    options = sys.argv
    if len(options) > 1:
        if '--ignore_stdout' in options or options[1].find('s') != -1:
            ignore_stdout = True
        if '--interactive' in options or options[1].find('i') != -1:
            while True:
                choice_menu()
    else:
        choice_menu()
