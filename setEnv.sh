#!/bin/bash
# script tested on Ubuntu 18.04.3 LTS using Python 3.6.8

# set Star-Dased directory
home=$PWD
printf "\ninstalling in $home\n"

# if there is no python virtual environment set up, set it up
if [ ! -d "$home/StarDasedVenv" ]; then
    printf "\ninstalling venv ..\n"
    sudo apt install python3-venv
    printf "setting up virtual environment 'StarDasedVenv' in $home...\n"
    python3 -m venv StarDasedVenv
fi

# sourrce the virtual environment
venvSource="$home/StarDasedVenv/bin/activate"
printf "activating vertial environment in $venvSource;\ntype 'deactivate' to leave virtual environment\n"
source ${venvSource}

# install/upgrade packages
declare -a packages="pip ipython numpy pandas scipy matplotlib sklearn torch tqdm"
for i in ${packages[@]}; do
    printf "\ninstalling/upgrading $i\n"
    pip install -U $i
done

# give permisions to run runit.sh
chmod 755 runit.sh
