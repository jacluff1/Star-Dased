Python files in this directory are for setting up the quest and running the
simulation. Files included:
================================================================================
| BaseModel.py      | Define a base model class that will be used for both     |
|                   | sim and meta models. Provide save-load capability        |
|                   | and anything else that may be useful.                    |
|-------------------|----------------------------------------------------------|
| FactorSpace.py    | 1) Define the parameters and their range.                |
|                   | 2) Construct a pd.DataFrame of all the input value       |
|                   |   permutations.                                          |
|                   | 3) Save as csv. Another option would be to have a model  |
|                   |   instance that can save and load itself, perhaps as pkl.|
|-------------------|----------------------------------------------------------|
| Functions.py      | Auxillary function definitions shared across multiple    |
|                   | files/modules.                                           |
|-------------------|----------------------------------------------------------|
| Input.py          | Definitions for any and all constants, conversions, etc  |
|-------------------|----------------------------------------------------------|
| Simulation.py     | My idea is to create define an class instance that can   |
|                   | run the simulation, save its progress (perhaps by        |
|                   | pickling itself), and able to load its progress upon     |
|                   | construction.                                            |
================================================================================
