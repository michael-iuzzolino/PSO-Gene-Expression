import os
import sys
import numpy as np
import pandas as pd
import json
import h5py
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.stats import stats
from sklearn.ensemble import RandomForestRegressor

TESTING_LOAD_THRESHOLD = 5000

class DataHandler(object):
    def __init__(self, percentiles, features, data_dir="../data", num_agents=None, top_k_variable_genes=10, show_variability_plot=False, baseline_iterations=5):

        # Setup the directory paths
        self.data_dir = data_dir
        self.paths = {
            "expression_data"   : "{}/genes_matrix_csv/expression_matrix.csv".format(data_dir),
            "columns_metadata"  : "{}/genes_matrix_csv/columns_metadata.csv".format(data_dir),
            "rows_metadata"     : "{}/genes_matrix_csv/rows_metadata.csv".format(data_dir),
            "stats"             : "{}/genes_matrix_expression_variability.json".format(data_dir),
            "correlation"       : "{}/gene_correlations.json".format(data_dir)
        }

        # Setup the variables
        self.features = features

        self.num_agents = num_agents
        self.scale_num_agents = False if num_agents else True

        self.baseline_iterations = baseline_iterations
        self.top_k_variable_genes = top_k_variable_genes
        self.show_variability_plot = show_variability_plot

        self.percentile_bounds = percentiles

        # Define other attributes
        self.stats = {"mean" : [], "std" : [], "max" : [], "min" : [], "range" : []}
        self.gene_expression_variability_high_to_low = []
        self.encoding_lookups = []
        self.highly_correlated_genes = []

        self.gene_expression_data = []      # X
        self.target_gene_data = []          # y
        self.target_gene = ""
        self.target_gene_index = None

        # Load the data
        self.__MAIN_load()

    def __MAIN_load(self):
        print("Loading Data...")

        # Load Data (expression, column metadata, row metadata)
        # ---------------------
        self.__1_load_data()
        # ---------------------

        # Encode column features
        # ---------------------------------------------
        self.__2_setup_feature_encodings()
        # ---------------------------------------------

        # Process gene expression variability
        # --------------------------------------------
        self.__3_process_gene_expression_variability()
        # --------------------------------------------

        # Get target gene
        # ----------------------------
        self.__4_select_target_gene()
        # ----------------------------

        # Calculate correlations between target gene and all other genes
        # --------------------------------
        self.__5_get_correlations()
        # --------------------------------

        # Calculate Baseline
        # ----------------------------
        self.__6_calculate_baseline()
        # ----------------------------

        print("Load complete.")

    def __1_load_data(self):
        # Load Expression Data
        self.gene_expression_df = pd.read_csv(self.paths["expression_data"], header=None, index_col=0)

        # Load column data
        self.columns_metadata_df = pd.read_csv(self.paths["columns_metadata"])

        # Select columns of interest from column data
        self.selected_columns_df = self.columns_metadata_df[self.features]

        # Load row data
        self.rows_metadata_df = pd.read_csv(self.paths["rows_metadata"])

        # Setup full gene list and assign list to row indices of expression df
        self.full_gene_list = list(self.rows_metadata_df["gene_symbol"])
        self.gene_expression_df.index = self.full_gene_list

    def __2_setup_feature_encodings(self):
        """
            For each of the gene features, setup encodings for donor, age, gender, and tissue
        """
        # Donor id
        # ---------------------------------------------------------------------------
        donors = list(set(self.columns_metadata_df["donor_name"]))
        donors_onehot = np.identity(len(donors))
        # ---------------------------------------------------------------------------

        # Age
        # ---------------------------------------------------------------------------
        ages = list(set(self.columns_metadata_df["age"]))
        ages_onehot = np.identity(len(ages))
        # ---------------------------------------------------------------------------

        # Gender
        # ---------------------------------------------------------------------------
        genders = {"M" : [0, 1], "F" : [1, 0]}
        # ---------------------------------------------------------------------------

        # Structure id
        # ---------------------------------------------------------------------------
        structures = list(set(self.columns_metadata_df["structure_acronym"]))
        structures_onehot = np.identity(len(structures))
        # ---------------------------------------------------------------------------

        # Put into single list for easy iteration
        self.encoding_lookups = {
            "donor"         : lambda donor : list(donors_onehot[donors.index(donor)]),
            "age"           : lambda age : list(ages_onehot[ages.index(age)]),
            "gender"        : lambda gender : genders[gender],
            "structure"     : lambda structure : list(structures_onehot[structures.index(structure)])
        }

        # Put sizes together
        self.encoding_sizes = {
            "donor"         : len(donors_onehot),
            "age"           : len(ages_onehot),
            "gender"        : len(genders.keys()),
            "structure"     : len(structures_onehot)
        }

    def __3_process_gene_expression_variability(self):
        """
            Checks if stats file exists.
            If stats file exists, load the file into self.gene_expression_variability_high_to_low and self.stats
            Else, process stats on gene_expression_df into self.gene_expression_variability_high_to_low and self.stats
        """
        print("Calculating Variability...")

        if os.path.exists(self.paths["stats"]):     # Stats exist - load them
            self.__3A_load_stats()
        else:                                       # Stats do not exist - create them
            self.__3B_process_stats()

    def __3A_load_stats(self):
        """
            Load the stats from file and create self.gene_expression_variability_high_to_low and self.stats
        """
        print("Loading stats data...")

        # Write
        with open(self.paths["stats"], "r") as infile:
            self.gene_expression_variability_high_to_low = json.load(infile)

    def __3B_process_stats(self):
        """
            Create self.gene_expression_variability_high_to_low
        """
        print("Generating stats data...")

        # Load dataframe
        genes_df = pd.DataFrame(self.gene_expression_df.index, columns=["gene_symbol"])

        # Calculate range of expression for each row
        # --------------------------------------------------------------------------------------------
        expression_range = self.gene_expression_df.apply(np.ptp, axis=1).reshape(-1, 1)
        expression_range_df = pd.DataFrame(expression_range, columns=["range"])
        # --------------------------------------------------------------------------------------------

        # Concatenate with stats df
        # -----------------------------------------------------------
        stats_df = pd.concat([genes_df, expression_range_df], axis=1)
        print(stats_df.head(4))
        # -----------------------------------------------------------

        # Sort the dataframe by range values
        # --------------------------------------------------------------------------------
        gene_expression_ranges_sorted = stats_df.sort_values(by="range")[::-1]
        # --------------------------------------------------------------------------------

        # Plot the bar chart if enabled
        # ------------------------------------------------------------------------------------
        if self.show_variability_plot:
            cmap = cm.get_cmap('Spectral') # Colour map (there are many others)
            gene_expression_ranges_sorted[:20].plot(x="gene_symbol", y="range", kind="bar", colormap=cmap)
            plt.show()
        # ------------------------------------------------------------------------------------

        # Generate list of gene expression variability from high to low - for use in selecting target gene
        # -----------------------------------------------------------------------------------------------------
        self.gene_expression_variability_high_to_low = []
        for gene_sym, gene_range in zip(list(gene_expression_ranges_sorted["gene_symbol"]), list(gene_expression_ranges_sorted["range"])):
            self.gene_expression_variability_high_to_low.append({
                "gene_symbol"   : gene_sym,
                "range"         : gene_range
            })
        # -----------------------------------------------------------------------------------------------------

        # Write stats to file
        # -----------------------------------------------------------------------------------------------------
        with open(self.paths["stats"], "w") as outfile:
            json.dump(self.gene_expression_variability_high_to_low, outfile)
        # -----------------------------------------------------------------------------------------------------

    def __4_select_target_gene(self):
        """
            Select the target gene and target_gene_index
        """
        target_selected = False
        while not target_selected:
            print("\n")
            print("Highly Variable Genes")
            print('---------------------')
            for i, gene_i in enumerate(self.gene_expression_variability_high_to_low[:self.top_k_variable_genes], 1):
                print("{}. {:15s} -- {:10.3f}".format(i, gene_i["gene_symbol"], gene_i["range"]))

            try:
                selected_gene_input = int(raw_input("Select gene: "))
                selected_gene = self.gene_expression_variability_high_to_low[selected_gene_input-1]["gene_symbol"]
                self.target_gene_index = self.full_gene_list.index(selected_gene)
                self.target_gene = self.full_gene_list[self.target_gene_index]

                # Error check
                # ------------------------------------------------------------------------------------------------
                if selected_gene != self.target_gene:
                    error_string = "ERROR! Gene ID issues.\n"
                    error_string += "selected_gene (user input) != self.full_gene_list[self.target_gene_index]\n"
                    error_string += "See function self.__4_select_target_gene"
                    print(error_string)
                    exit(1)
                # ------------------------------------------------------------------------------------------------

                # Disply info to user for confirmation
                # -------------------------------------------------
                print("Target gene: {}".format(self.target_gene))
                raw_input("Press any key to continue...")
                # -------------------------------------------------

                # Flag as selected to break loop
                target_selected = True

            except KeyboardInterrupt:
                print("\nKeyboard interrupt. Exiting...")
                exit(0)

            except:
                print("Invalid selection.")

        # Set target gene data
        self.target_gene_data = np.array(self.gene_expression_df.ix[self.target_gene]).reshape(-1,)

    def __5_get_correlations(self):

        # Check if file exists
        if os.path.exists(self.paths["correlation"]):
            # If file exists, check if it contains correlation data for target gene
            with open(self.paths["correlation"], "r") as infile:
                correlation_data = json.load(infile)

            if self.target_gene in correlation_data.keys():
                self.highly_correlated_genes = correlation_data[self.target_gene]
            else:
                self.__5A_calculate_correlations()
        else:
            self.__5A_calculate_correlations()

        # Set gene name list
        self.gene_name_list = [val[0] for val in self.highly_correlated_genes]

        # Set gene expression data, X
        self.gene_expression_data = self.gene_expression_df.loc[self.gene_name_list]

        # Set number of genes
        self.num_genes = self.gene_expression_data.shape[0]

        # Set number of agents
        if self.scale_num_agents:
            self.num_agents = int(self.num_genes * 0.10) # Set the num agents to 1/10th the number of genes

    def __5B_write_correlation_data(self):
        # Check if file exists
        if os.path.exists(self.paths["correlation"]):
            # If file exists, open and read in data, then append and write
            with open(self.paths["correlation"], "r") as infile:
                correlation_data = json.load(infile)

            correlation_data[self.target_gene] = self.highly_correlated_genes

        else:
            write_data = {self.target_gene : self.highly_correlated_genes}
            with open(self.paths["correlation"], "w") as outfile:
                json.dump(write_data, outfile)

    def __5A_calculate_correlations(self):
        """
            Calculate the pair-wise correlation between the target gene and all other genes (pearson correlation coefficient)
            Calculate the 5 and 95 percentiles and use to threshold and generate list of highly correlated genes: self.highly_correlated_gene_indices
        """
        print("Calculating Correlations...")
        print("Target Gene: {}".format(self.target_gene))
        print("Target Gene Index: {}".format(self.target_gene))

        y = self.target_gene_data

        # Calculate the Pearson correlation coefficients between each x_i in X and the target gene
        # -------------------------------------------------------------------------------------------
        gene_correlation_data = []
        for gene_i, gene_name in enumerate(self.full_gene_list):

            # DEBUG
            if TESTING_LOAD_THRESHOLD:
                if gene_i > TESTING_LOAD_THRESHOLD:
                    break

            # Skip if current gene is target
            if gene_name == self.target_gene:
                continue

            x_i = list(self.gene_expression_df.loc[gene_name])

            # Calculate pearson correlation coefficient
            pearson_val = stats.pearsonr(x_i, y)[0] # Take first element: correlation coefficient. Second element is probability

            # Catch nan values and do not store these: DEBUG later
            if not np.isnan(pearson_val):
                # Store a tuple of the gene name and its pearson corr coeff
                gene_correlation_data.append((gene_name, gene_i, pearson_val))

            else:
                try:
                    pearson_val = 0.0
                    gene_correlation_data.append((gene_name, gene_i, pearson_val))
                except:
                    print("Fail again.")

            sys.stdout.write("\r Gene {} / {}".format(gene_i, len(self.full_gene_list)))
            sys.stdout.flush()
        # -------------------------------------------------------------------------------------------

        # Calculate top and bottom percentiles
        # -------------------------------------------------------------------------------------------
        # Pearson_corr_coeff_values = np.array(gene_correlation_data)[:,2]
        Pearson_corr_coeff_values = [val[2] for val in gene_correlation_data]
        try:
            top_percentile = np.percentile(Pearson_corr_coeff_values, self.percentile_bounds["top"])
            bottom_percentile = np.percentile(Pearson_corr_coeff_values, self.percentile_bounds["bottom"])
        except:
            print("\nERROR!")
            print("Pearson_corr_coeff_values")
            print(Pearson_corr_coeff_values)
            print("\n")
            print("self.percentile_bounds")
            print(self.percentile_bounds)
        # -------------------------------------------------------------------------------------------

        # Calculate the list of highly correlated genes given percentile constraints
        # -------------------------------------------------------------------------------------------
        self.highly_correlated_genes = []
        for gene_name, gene_index, pearson_val in gene_correlation_data:
            # Check if gene's pearson corr coeff is within a percentile - if so, store it
            if pearson_val < bottom_percentile or pearson_val > top_percentile:
                self.highly_correlated_genes.append((gene_name, gene_index, pearson_val))

        print("\n")
        print("{} highly correlated genes.".format(len(self.highly_correlated_genes)))
        # -------------------------------------------------------------------------------------------

        # Write correlation data
        self.__5B_write_correlation_data()

    def __6_calculate_baseline(self):
        print("Calculating baseline...")
        # self.
        X, y = self.get_expression_levels([i for i in range(self.num_genes)])

        baseline_errors = []
        for i in range(self.baseline_iterations):
            baseline_reg = RandomForestRegressor(oob_score=True)
            baseline_reg.fit(X, y)
            baseline_error = baseline_reg.oob_score_
            baseline_errors.append(baseline_error)

        self.baseline_error = np.mean(baseline_errors)

        print("Baseline error: {}".format(self.baseline_error))
        print("\n")

    def get_expression_levels(self, active_gene_indices):
        """
            Get the X, y for regression
        """
        expression_data = self.gene_expression_data.iloc[active_gene_indices].T

        encoded_column_data = []
        for col_data in np.array(self.selected_columns_df):
            encoded_data = self.__encode_data(col_data)
            encoded_column_data.append(encoded_data)

        encoded_column_data = np.array(encoded_column_data)

        X = np.concatenate([expression_data, encoded_column_data], axis=1)
        y = self.target_gene_data

        return X, y

    def __encode_data(self, col_data):
        """
            Encode the features using 1hot encoding setup in step 2
        """
        encoded_values = []
        for val, feature_raw in zip(col_data, self.features):
            feature = feature_raw.split("_")[0]
            encoded_val = self.encoding_lookups[feature](val)

            if type(encoded_val) is type([]):
                encoded_values += encoded_val
            else:
                encoded_values.append(encoded_val)

        return encoded_values
