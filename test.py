import os

# Get the list of all installed packages
packages = os.popen('pip freeze').read().splitlines()

# Uninstall each package
for package in packages:
    os.system(f"pip uninstall -y {package.split('==')[0]}")