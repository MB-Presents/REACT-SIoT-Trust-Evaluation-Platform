import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from experiments.settings import Settings
from trust.trust_recommenders.ontology_based.constants import TrustModelSettings
import utils.pathfinder as pathfinder

def get_experiment_results(experiments_result : list):
    columns = [
                'Run', 'Accuracy_Emergency', 'Precision_Emergency', 'Recall_Emergency', 'F1Score_Emergency',
                'Accuracy_TrafficLight', 'Precision_TrafficLight', 'Recall_TrafficLight', 'F1Score_TrafficLight',
                'Accuracy_Overall', 'Precision_Overall', 'Recall_Overall', 'F1Score_Overall'
            ]
    df = pd.DataFrame(columns=columns)

    for i, simulation_results in enumerate(experiments_result):
        _, accuracy_emergency_report, accuracy_traffic_light = simulation_results

                # Extracting metrics from emergency report
        emergency_report = accuracy_emergency_report['classification_report']
        emergency_metrics = {
                    'Accuracy': emergency_report['accuracy'],
                    'Precision': emergency_report['weighted avg']['precision'],
                    'Recall': emergency_report['weighted avg']['recall'],
                    'F1Score': emergency_report['weighted avg']['f1-score']
                }

                # Extracting metrics from traffic light report
        traffic_light_report = accuracy_traffic_light['classification_report']
        traffic_light_metrics = {
                    'Accuracy': traffic_light_report['accuracy'],
                    'Precision': traffic_light_report['weighted avg']['precision'],
                    'Recall': traffic_light_report['weighted avg']['recall'],
                    'F1Score': traffic_light_report['weighted avg']['f1-score']
                }

                # Calculating overall metrics
        overall_metrics = {
                    'Accuracy': np.mean([emergency_metrics['Accuracy'], traffic_light_metrics['Accuracy']]),
                    'Precision': np.mean([emergency_metrics['Precision'], traffic_light_metrics['Precision']]),
                    'Recall': np.mean([emergency_metrics['Recall'], traffic_light_metrics['Recall']]),
                    'F1Score': np.mean([emergency_metrics['F1Score'], traffic_light_metrics['F1Score']])
                }

                # Add to DataFrame
        df.loc[i] = [
                    i + 1,  # Run number
                    emergency_metrics['Accuracy'], emergency_metrics['Precision'], emergency_metrics['Recall'], emergency_metrics['F1Score'],
                    traffic_light_metrics['Accuracy'], traffic_light_metrics['Precision'], traffic_light_metrics['Recall'], traffic_light_metrics['F1Score'],
                    overall_metrics['Accuracy'], overall_metrics['Precision'], overall_metrics['Recall'], overall_metrics['F1Score']
                ]

            # Compute statistics
    stats = df.describe(percentiles=[.25])
    print(stats)

            # Plotting
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1Score']
    systems = ['Emergency', 'TrafficLight', 'Overall']

    fig, axes = plt.subplots(len(metrics), len(systems), figsize=(18, 8))

    for i, metric in enumerate(metrics):
        for j, system in enumerate(systems):
            ax = axes[i, j]
            column_name = f'{metric}_{system}'
            df.boxplot(column=column_name, ax=ax)
            ax.set_title(f'{metric} {system}')
            ax.set_ylabel(metric)

    plt.suptitle(f'Metric Distribution of {Settings.TRUST_MODEL_DESCRIPTION}')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    # plt.show()
    
    
    experiment_result_path = pathfinder.get_experiment_results_path(Settings.SELECTED_TRUST_MODEL, Settings.EXPERIMENT_NAME)
    experiment_result_file = os.path.join(experiment_result_path, "experiment_results.png")
    plt.savefig(experiment_result_file)
    
    return stats, df
