Python files in this directory are for taking the sim output and creating
surrogate models.
================================================================================
|  aseModel         | Define a base model class that will be used for both     |
|                   | sim and meta models. Provide save-load capability        |
|                   | and anything else that may be useful.                    |
|-------------------|----------------------------------------------------------|
| Functions         | Auxillary function definitions shared across multiple    |
|                   | files/modules.                                           |
|-------------------|----------------------------------------------------------|
| Input             | Definitions for any and all constants, conversions, etc  |
|-------------------|----------------------------------------------------------|
| Plots             | 3D static plot, animation, exploritory data analysis     |
|                   | (hopefully someday)                                      |
|-------------------|----------------------------------------------------------|
| Simulation        | takes in all user input and runs the simulation. will    |
|                   | save progress as it runs in a Simulation.pkl; as soon as |
|                   | sim is done running, will save completed data as         |
|                   | Simulation.csv.                                          |
================================================================================
