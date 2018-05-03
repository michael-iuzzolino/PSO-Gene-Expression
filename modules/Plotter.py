import os
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import pandas as pd

class Plotter(object):

    def __init__(self):
        self.paths = {
            "experiments"   : "experiments",
            "figures"       : "experiments/figs"
        }

    def plot_gene_activation_heatmap(self, history_data, gene_names, baseline_error):
        cbar_plotted = False # Prevents multiple cbar prints

        for history_i, (history, best_error_i, best_feature_importance) in enumerate(zip(history_data["position"], history_data["error"], history_data["feature_importance"])):
            # print("\n")
            # print("History {}".format(history_i+1))
            # print("Feature importances")
            # for key, val in best_feature_importance.items():
            #     print("\t{} : {}".format(key, val))
            # print("\n")
            # print("\n")

            history = history[:100].reshape(100, 1)

            num_genes = history.shape[0]
            num_cols = 10
            num_rows = int(np.ceil(num_genes / float(num_cols)))
            reshaped_global_positions = history.reshape(num_rows, num_cols)

            gene_names = gene_names[:100]

            reshaped_global_gene_names = np.array(gene_names).reshape(num_rows, num_cols)

            plot_params = {
                "cmap"          : ListedColormap(["#ffcccc", "#99ff99"]),
                "linewidths"    : 1.5,
                "annot"         : reshaped_global_gene_names if len(reshaped_global_gene_names) < 100 else None,
                "fmt"           : '',
                "cbar"          : False if cbar_plotted else True
            }
            ax = sns.heatmap(reshaped_global_positions, **plot_params)

            if not cbar_plotted:
                cbar = ax.collections[0].colorbar
                cbar.set_ticks([0.25, 0.75])
                cbar.set_ticklabels(["OFF", "ON"])
                cbar_plotted = True

            plt.title("Timestep: {} / {} \n Best Error: {:0.4f}".format(history_i+1, len(history_data["position"]), best_error_i))
            plt.axis('off')
            plt.savefig("{}/heatmap_{}.png".format(self.paths["figures"], history_i+1), dpi=300)
            plt.cla()

        # Clear the axes
        cbar.remove()

    def data_analysis_plots(self, json_file):
        plt.cla()

        json_path = os.path.join(self.paths["experiments"], json_file)
        with open(json_path, "r") as infile:
            data = json.load(infile)

        means = []
        num_genes_active = []
        errors = []
        bests = []
        timesteps = [i for i in range(len(data["error_stats"]))]
        for timestep_i, data_i in enumerate(data["error_stats"]):
            num_genes = data["num_genes_active"][timestep_i]
            mean = data_i["mean"]
            std = data_i["std"]
            error_list = data_i["errors"]
            best = np.min(error_list)
            means.append(mean)
            num_genes_active.append(num_genes)
            errors.append(error_list)
            bests.append(best)

        # Num genes vs. timesteps
        df = pd.concat([pd.DataFrame(num_genes_active, columns=["num_genes_active"]), pd.DataFrame(timesteps, columns=["timesteps"])], axis=1)
        sns.regplot(x="timesteps", y="num_genes_active", data=df)
        plt.plot(timesteps, [baseline_error for i in range(len(timesteps))], 'r--', label="Correlation Baseline: {}".format(baseline_error))
        plt.title("Gene Count vs. Timesteps")
        plt.xlabel("Training Timesteps")
        plt.ylabel("Number of Genes for Regression")
        plt.savefig("{}/gene_count.png".format(self.paths["figures"]), dpi=300)
        plt.cla()

        # Best OOBs
        df = pd.concat([pd.DataFrame(bests, columns=["best"]), pd.DataFrame(timesteps, columns=["timesteps"])], axis=1)
        sns.regplot(x="timesteps", y="best", data=df)
        plt.plot(timesteps, [baseline_error for i in range(len(timesteps))], 'r--', label="Correlation Baseline: {}".format(baseline_error))
        plt.legend()
        plt.title("OOB Best Error vs. Timesteps")
        plt.xlabel("Training Timesteps")
        plt.ylabel("OOB Best Error")
        plt.savefig("{}/best_oob.png".format(self.paths["figures"]), dpi=300)
        plt.cla()

        # Average OOBs
        df = pd.concat([pd.DataFrame(means, columns=["means"]), pd.DataFrame(timesteps, columns=["timesteps"])], axis=1)
        sns.regplot(x="timesteps", y="means", data=df)
        plt.title("OOB Mean Error vs. Timesteps")
        plt.xlabel("Training Timesteps")
        plt.ylabel("OOB Mean Error")
        plt.savefig("{}/average_oob.png".format(self.paths["figures"]), dpi=300)
        plt.cla()
