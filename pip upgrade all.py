import pip
from io import StringIO
from contextlib import redirect_stdout


def update(package_name):
    if package in ['numpy', 'scipy']:
        print("Package %s is skipped for compatibility issues on windows\n" % package)
        return False
    print("Updating %s..." % package_name)
    f = StringIO()
    with redirect_stdout(f):
        pip.main(['install', '--upgrade', package_name])
    output = f.getvalue().split('\n')
    print(output)
    print("Update Complete")
    return True


def update_all(outdated_packages):
    for package in outdated_packages:
        update(package)
    print("All packages are updated")

if __name__ == "__main__":
    print("Searching for outdated packages...")
    f = StringIO()
    with redirect_stdout(f):
        pip.main(['list', '--outdated', '--format=columns'])
    output = f.getvalue().split('\n')
    header = output[0:2]
    del output[0:2]
    del output[-1]
    index = 1

    print("Outdated packages: ")
    outdated = []
    for package in output:
        package = package.split()
        print('%d) %s\t\t\t%s --> %s (%s)' % (index, package[0], package[1], package[2], package[3]))
        outdated.append(package[0])
        index += 1

    while True:
        choice = input("\nWhich library do you want to update? [all,<number>,exit] ")
        if choice == 'exit':
            break
        if choice == 'all':
            choice = input("\nAre you sure to update all outdated packages? [y,<else>] ")
            if choice == 'y':
                update_all(outdated)
                break
        choices = choice.split(',')
        for choice in choices:
            update(outdated[int(choice)-1])
