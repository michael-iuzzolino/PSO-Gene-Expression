import numpy as np
import pandas as pd

from modules.Swarm import Swarm

num_agents = 20
maxiter = 100
C1 = 1.49
C2 = 1.49
W = 0.25

class Data(object):
    def __init__(self):
        data_dir = "../../data"
        self.expression_matrix_path = "{}/genes_matrix_csv/expression_matrix.csv".format(data_dir)
        self.columns_metadata_path = "{}/genes_matrix_csv/columns_metadata.csv".format(data_dir)
        self.rows_metadata_path = "{}/genes_matrix_csv/rows_metadata.csv".format(data_dir)

    def load(self, limit=-1):
        print("Loading Data...")
        raw_expression_df = pd.read_csv(self.expression_matrix_path, header=None, index_col=0)

        # Load row data
        rows_metadata_df = pd.read_csv(self.rows_metadata_path)

        # Set index with gene names
        self.gene_list = list(rows_metadata_df["gene_symbol"])
        raw_expression_df.index = self.gene_list

        # Cast to matrix and limit data
        self.raw_expression_data = np.array(raw_expression_df)[:limit]

        # TODO: Update later
        # ******************************************************
        # Random target gene
        self.target_gene = self.gene_list[limit:limit+1]
        self.y = np.array(raw_expression_df.ix[self.target_gene]).reshape(-1,)
        # ******************************************************

        # Limit gene list
        self.gene_list = self.gene_list[:limit]
        print("Load complete.")

    def get_expression_levels(self, active_gene_indices):
        X = self.raw_expression_data[active_gene_indices].T
        return X, self.y

    @property
    def num_genes(self):
        return self.raw_expression_data.shape[0]

def main():
    data = Data()
    data.load(5)

    #--- RUN ----------------------------------------------------------------------+
    swarm_params = {
        "num_agents"                : num_agents,
        "maxiter"                   : maxiter,
        "agent_params"                  : {
            "c1"                        : C1,
            "c2"                        : C2,
            "weight"                    : W,
            "data"                      : data
        }
    }

    pso_swarm = Swarm(**swarm_params)
    pso_swarm.run()
    #--- END ----------------------------------------------------------------------+

if __name__ == "__main__":
    main()
