# Running Application
1. pip install all required modules
2. Extract the `genes_matrix_csv.zip` into the `/data` directory.
3. cd into `PSO-Gene-Expression` directory
4. Run `python main.py`


# Configuration
The `modules/config.py` script contains PSO hyper parameters, data handler parameters, etc.

# Data Handler
The data handler class reads in the files, does all the data processing, and so on.
It is instantiated once inside of `main.py` and the object is passed to each Agent object.
Each agent evaluation, the Agent calls the data object with the set of selected indicies,
and the data object yields the processed and encoded X, y data for feeding into the Random Forest Regressor.

# Swarm
The `Swarm.py` script contains the PSO algorithm, data history, and plotting function (visualization of active genes each training step)

# Agent
Agents of the system.
