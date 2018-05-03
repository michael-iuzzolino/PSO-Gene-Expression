def __5_calculate_correlations(self):
    """
        Calculate the pair-wise correlation between the target gene and all other genes (pearson correlation coefficient)
        Calculate the 5 and 95 percentiles and use to threshold and generate list of highly correlated genes: self.highly_correlated_gene_indices
    """
    print("Calculating Correlations...")
    print("Target Gene: {}".format(self.target_gene))
    print("Target Gene Index: {}".format(self.target_gene))

    y = self.target_gene_data

    correlations_path_exists = False
    correlation_data_already_exists = False

    # Check if correlations file exists
    if os.path.exists(self.paths["correlations"]):

        correlations_path_exists = True
        # Check if target gene already has correlations built
        with open(self.paths["correlations"], "r") as infile:
            correlation_data = json.load(infile)

        if self.target_gene in correlation_data.keys():
            correlation_data_already_exists = True

            # Load the data
            self.highly_correlated_genes = correlation_data[self.target_gene]

    if not correlations_path_exists or not correlation_data_already_exists:
        # Calculate the Pearson correlation coefficients between each x_i in X and the target gene
        # -------------------------------------------------------------------------------------------
        gene_correlation_data = []
        for gene_i, gene_name in enumerate(self.full_gene_list):

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


    # Set gene name list
    self.gene_name_list = [val[0] for val in self.highly_correlated_genes]

    # Set gene expression data, X
    self.gene_expression_data = self.gene_expression_df.loc[self.gene_name_list]

    # Set number of genes
    self.num_genes = self.gene_expression_data.shape[0]

    # Set number of agents
    if self.scale_num_agents:
        self.num_agents = int(self.num_genes * 0.10) # Set the num agents to 1/10th the number of genes
