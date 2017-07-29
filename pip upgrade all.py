import pip
from subprocess import run, PIPE


def update(package_name):
    if package in ['numpy', 'scipy']:
        print("Package %s is skipped for compatibility issues\n" % package)
        return False
    print("Updating %s..." % (package_name))
    print(run("pip install --upgrade %s" % (package_name), shell=True, stdout=PIPE).stdout.decode('utf-8'))
    print("Update Complete")
    return True


def update_all(outdated_packages):
    for package in outdated_packages:
        update(package)
    print("All packages are updated")


print("Searching for outdated packages...")
outdated = []
output = run("pip list --outdated --format=columns", shell=True, stdout=PIPE).stdout.decode('utf-8').split('\r\n')
header = output[0:2]
del output[0:2]
del output[-1]
index = 1
print("Outdated packages: ")
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

input("Press Enter to exit...")
