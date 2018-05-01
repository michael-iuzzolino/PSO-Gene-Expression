import os
import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt
from matplotlib import cm

class DataHandler(object):
    def __init__(self, num_agents, top_k_variable_genes=10, show_variability_plot=False):
        self.data_dir = "../data"
        self.expression_matrix_path = "{}/genes_matrix_csv/expression_matrix.csv".format(self.data_dir)
        self.columns_metadata_path = "{}/genes_matrix_csv/columns_metadata.csv".format(self.data_dir)
        self.rows_metadata_path = "{}/genes_matrix_csv/rows_metadata.csv".format(self.data_dir)
        self.stats_path = "{}/genes_matrix_expression_variability.h5".format(self.data_dir)

        self.num_agents = num_agents
        self.scale_num_agents = True if num_agents < 0 else False
        self.top_k_variable_genes = top_k_variable_genes
        self.show_variability_plot = show_variability_plot

    def _get_genes_by_expression_variability(self, raw_expression_df):
        print("Calculating Variability...")

        if os.path.exists(self.stats_path):
            print("Loading stats data...")
            # Write
            with h5py.File(self.stats_path, "r") as infile:
                stats_group = infile["stats"]
                self.stats = { stat_key : stat_val for stat_key, stat_val in stats_group.items() }

                self.gene_expression_variability_high_to_low = []
                for gene_symbol, gene_range in zip(infile["sorted_variability"]["gene_symbol"], infile["sorted_variability"]["range"]):
                    self.gene_expression_variability_high_to_low.append({
                        "gene_symbol"   : gene_symbol,
                        "range"         : gene_range
                    })
        else:
            print("Generating stats data...")
            stats_df = pd.DataFrame(raw_expression_df.index)
            stats_df.columns = ["gene_symbol"]

            self.stats = {"mean" : [], "std" : [], "max" : [], "min" : [], "range" : []}
            for row_i in raw_expression_df.iterrows():
                row_key = row_i[0]
                row_val = row_i[1]
                self.stats["mean"].append(np.mean(row_val))
                self.stats["std"].append(np.std(row_val))
                self.stats["max"].append(np.max(row_val))
                self.stats["min"].append(np.min(row_val))
                self.stats["range"].append(np.max(row_val)-np.min(row_val))

            for stat in self.stats.keys():
                stats_df = pd.concat([stats_df, pd.DataFrame(self.stats[stat], columns=[stat])], axis=1)

            stats_df_sorted = stats_df.sort_values(by="range")[::-1]

            if self.show_variability_plot:
                cmap = cm.get_cmap('Spectral') # Colour map (there are many others)
                stats_df_sorted[:20].plot(x="gene_symbol", y="range", kind="bar", colormap=cmap)
                plt.show()

            self.gene_expression_variability_high_to_low = []
            for gene_sym, gene_range in zip(list(stats_df_sorted["gene_symbol"]), list(stats_df_sorted["range"])):
                self.gene_expression_variability_high_to_low.append({
                    "gene_symbol"   : gene_sym,
                    "range"         : gene_range
                })

            # Write
            with h5py.File(self.stats_path, "w") as outfile:
                stats_group = outfile.create_group("stats")
                for stat_key, stat_val in self.stats.items():
                    stats_group.create_dataset(stat_key, data=stat_val)

                sorted_variability_group = outfile.create_group("sorted_variability")
                sorted_variability_group.create_dataset("gene_symbol", data=[d["gene_symbol"] for d in self.gene_expression_variability_high_to_low])
                sorted_variability_group.create_dataset("range", data=[d["range"] for d in self.gene_expression_variability_high_to_low])

        # print(self.gene_expression_variability_high_to_low[:5])

    def _set_encoded_features(self, columns_metadata_df):

        # Donor id
        donors = {donor_id : i for i, donor_id in enumerate(list(set(columns_metadata_df["donor_id"])))}
        self.donor_lookup = lambda donor : donors[donor]
        self.donor_encoding_size = 1

        # Age
        ages = list(set(columns_metadata_df["age"]))
        ages_onehot = np.identity(len(ages))
        self.ages_lookup = lambda age : list(ages_onehot[ages.index(age)])

        self.ages_encoding_size = len(ages_onehot)

        # Gender
        genders = {
            "M" : [0, 1],
            "F" : [1, 0]
        }
        self.gender_lookup = lambda gender : genders[gender]

        self.gender_encoding_size = len(genders.keys())

        # Structure id
        structures = {structure_id : i for i, structure_id in enumerate(list(set(columns_metadata_df["structure_id"])))}
        self.structure_lookup = lambda structure : structures[structure]

        self.structure_encoding_size = 1

        # Put into single list for easy iteration
        self.lookups = [self.donor_lookup, self.ages_lookup, self.gender_lookup, self.structure_lookup]

        # Put sizes together
        self.encoding_sizes = {
            "donor"         : self.donor_encoding_size,
            "age"           : self.ages_encoding_size,
            "gender"        : self.gender_encoding_size,
            "structure"     : self.structure_encoding_size
        }

    def _get_target_gene(self):
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
                target_gene_index = self.gene_list.index(selected_gene)
                self.target_gene = self.gene_list[target_gene_index]
                print("Target gene: {}".format(self.target_gene))
                raw_input("")
                target_selected = True
            except:
                print("Invalid selection")

    def load(self, num_genes=-1, PCA_init=False):
        print("Loading Data...")

        # Load Expression Data
        raw_expression_df = pd.read_csv(self.expression_matrix_path, header=None, index_col=0)

        # Load column data
        columns_metadata_df = pd.read_csv(self.columns_metadata_path)

        # Select columns of interest from column data
        selected_columns_df = columns_metadata_df[["donor_id", "age", "gender", "structure_id"]]
        self.column_data = np.array(selected_columns_df)

        # Encode column features
        # ---------------------------------------------
        self._set_encoded_features(columns_metadata_df)
        # ---------------------------------------------

        # Load row data
        rows_metadata_df = pd.read_csv(self.rows_metadata_path)

        # Set index with gene names
        self.gene_list = list(rows_metadata_df["gene_symbol"])
        raw_expression_df.index = self.gene_list

        # Get variability()
        self._get_genes_by_expression_variability(raw_expression_df)

        # Cast to matrix and limit data
        self.raw_expression_data = np.array(raw_expression_df)[:num_genes]

        # TODO: Update later
        # ******************************************************
        self._get_target_gene()
        self.y = np.array(raw_expression_df.ix[self.target_gene]).reshape(-1,)
        # ******************************************************

        # Limit gene list
        self.gene_list = self.gene_list[:num_genes]
        self.num_genes = len(self.gene_list)

        if self.scale_num_agents:
            self.num_agents = int(self.num_genes * 0.10) # Set the num agents to 1/10th the number of genes

        # PCA init
        if PCA_init:
            print("Running PCA...")
            from sklearn.decomposition import PCA
            pca = PCA(n_components=self.num_agents)
            pca.fit(self.raw_expression_data.T)
            comps = pca.components_
            comps_thresholded = np.zeros_like(comps)
            for row_i, row in enumerate(comps):
                row_mean = np.mean(row)
                comps_thresholded[row_i] = np.abs(row) > row_mean

            self.agent_initializations = comps_thresholded.astype(np.int)
            print("Finished initializing agent positions.")

        print("Load complete.")

    def agent_initialization(self, agent_id):
        return self.agent_initializations[agent_id]

    def _encode_data(self, col_data):
        encoded_values = []
        for val, lookup in zip(col_data, self.lookups):
            encoded_val = lookup(val)

            if type(encoded_val) is type([]):
                encoded_values += encoded_val
            else:
                encoded_values.append(encoded_val)

        return encoded_values

    def get_expression_levels(self, active_gene_indices):
        expression_data = self.raw_expression_data[active_gene_indices].T

        encoded_column_data = []
        for col_data in self.column_data:
            encoded_column_data.append(self._encode_data(col_data))

        encoded_column_data = np.array(encoded_column_data)
        X = np.concatenate([expression_data, encoded_column_data], axis=1)

        return X, self.y
