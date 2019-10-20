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

install requirements into standard python 3 libraries:
```bash
pip3 install -r requirements.txt
```
OR
setup virtual environment, install/update dependencies, activate virtual environment, and give permissions to runit.sh
```bash
source setEnv.sh
```
to activate virtual environment without updating packages:
```bash
source activateEnv.sh
```
to deactivate virtual environment
```bash
deactivate
```



Start with
----------

run models individually:
```bash
python3 pyFiles/Simulation.py
python3 pyFiles/MetaModels/<desired model>.py
```
OR
run: simulation, any meta models, and generate any plots in runit.sh
```bash
./runit.sh
```
