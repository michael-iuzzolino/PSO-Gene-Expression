import numpy as np
import pandas as pd

class DataHandler(object):
    def __init__(self):
        data_dir = "../../data"
        self.expression_matrix_path = "{}/genes_matrix_csv/expression_matrix.csv".format(data_dir)
        self.columns_metadata_path = "{}/genes_matrix_csv/columns_metadata.csv".format(data_dir)
        self.rows_metadata_path = "{}/genes_matrix_csv/rows_metadata.csv".format(data_dir)

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

        # Cast to matrix and limit data
        self.raw_expression_data = np.array(raw_expression_df)[:num_genes]

        # TODO: Update later
        # ******************************************************
        # Random target gene
        self.target_gene = self.gene_list[num_genes:num_genes+1]
        self.y = np.array(raw_expression_df.ix[self.target_gene]).reshape(-1,)
        # ******************************************************

        # Limit gene list
        self.gene_list = self.gene_list[:num_genes]
        self.num_genes = len(self.gene_list)

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
