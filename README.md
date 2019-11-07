Star-Dased
==========
A quest for a stable solution to the 3-body star system problem using Design of Experiment (DOE)

motivation
----------

install
-------
Clone from Github
```bash
git clone https://github.com/jacluff1/Star-Dased.git
```
Download and install Python 3.6 or higher from www.python.org

install continued: using virtual environment (recommended)
----------------------------------------------------------
setup virtual environment, install/update dependencies, activate virtual environment, and give permissions to runit.sh. This only needs to be done once (or if you want to update virtual environment packages)
```bash
source setEnv.sh
```
install continued: secondary method
-----------------------------------
install requirements into standard python 3 libraries:
```bash
pip3 install -r requirements.txt
```

pre-run
-------
make sure and stay in the repo root directory to run
if using the virtual environment, make sure to activate it (if not already activated)
```bash
source activateEnv.sh
```
(to deactivate the virtual environment when no longer needed)
```bash
deactivate
```

run method 1 (recommended)
--------------------------
to run all the default models with default options
```bash
./runit.sh
```

run method 2
------------
to have control over what models to run and what options to use
```bash
python -B Main.py
```
to see what options are currently available, what they are for, and how they are used
```bash
python -B Main.py -h
```
EG, if you want to run the sim with early stopping, wanted a static plot with final positions and an animation for scenario 3 (0-indexed), and wanted to run random forest model with classification trees
```bash
python -B Main.py --sim --earlyStop --plot3Dpos --anim --timeIdx -1 --sampleRowIdx 2 --rfc
```
