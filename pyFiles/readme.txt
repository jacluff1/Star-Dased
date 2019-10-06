Python files in this directory are for setting up the quest and running the
simulation. Files included:
================================================================================
| BaseModel         | Define a base model class that will be used for both     |
|                   | sim and meta models. Provide save-load capability        |
|                   | and anything else that may be useful.                    |
|-------------------|----------------------------------------------------------|
| FactorSpace       | 1) Define the parameters and their range.                |
|                   | 2) Construct a pd.DataFrame of all the input value       |
|                   |   permutations.                                          |
|                   | 3) Save as csv. Another option would be to have a model  |
|                   |   instance that can save and load itself, perhaps as pkl.|
|-------------------|----------------------------------------------------------|
| Functions         | Auxillary function definitions shared across multiple    |
|                   | files/modules.                                           |
|-------------------|----------------------------------------------------------|
| Input             | Definitions for any and all constants, conversions, etc  |
|-------------------|----------------------------------------------------------|
| Main              | Any main instructions -- not implemented yet             |
|-------------------|----------------------------------------------------------|
| MassDistrobution  | Use an initial mass function (IMF) to calculate a mass   |
|                   | distribution. Use the mass PDF to create a generating    |
|                   | function that will randomly select a mass and thereby    |
|                   | also select spectral type and star radius.               |
|-------------------|----------------------------------------------------------|
| Simulation        | My idea is to create define an class instance that can   |
|                   | run the simulation, save its progress (perhaps by        |
|                   | pickling itself), and able to load its progress upon     |
|                   | construction.                                            |
================================================================================
