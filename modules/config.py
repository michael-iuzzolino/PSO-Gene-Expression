TESTING = True

# PSO Hyperparameters
# -----------------------------------------------------------------------------------------------------------------------
MAX_EPOCHS = 10 if TESTING else 50
NUM_AGENTS = 200                                # Set to None for auto-scaling (set num agents = 10% of num genes)
C1 = 2                                          # 1.49445
C2 = 2                                          # 1.49445
W = 0.4                                         # 0.729
VMIN = -4
VMAX = 4
# -----------------------------------------------------------------------------------------------------------------------

# Data Handler parameters
# -----------------------------------------------------------------------------------------------------------------------
DATA_PATH = "data"
PERCENTILES = {
    "top"       : 95,
    "bottom"    : 5
}
TOP_K_VARIABLE_GENES = 10                           # Set the number of genes able to select from for setting target
BASELINE_ITERATIONS = 5                             # How many times to run the baseline regressor
FEATURES = ["age", "gender", "structure_acronym"]   # all four: ["donor_name", "age", "gender", "structure_acronym"]
NUM_SUBSET_GENES = 5000                             # How much data to subset from ~50k genes. Set to False to disable
# -----------------------------------------------------------------------------------------------------------------------

# Plot parameters
# -----------------------------------------------------------------------------------------------------------------------
PLOT_GENE_ACTIVITY = True
PLOT_GENE_VARIABILITY_ON_LOAD = False
# -----------------------------------------------------------------------------------------------------------------------
