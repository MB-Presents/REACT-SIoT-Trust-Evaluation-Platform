
from collections import Counter
import os
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
import seaborn as sns
import matplotlib.pyplot as plt

from dataset_builder.utils.path_helper import get_confusion_matrix_file_path, get_evaluation_directory_path, get_evaluation_result_path, get_loss_output_path, get_roc_curve_file_path, get_trainings_loss_file_path

# Compute confusion matrix
def generate_confusion_matrix(all_ground_truth,all_predictions_binary):
    
    
    conf_mat = confusion_matrix(all_ground_truth, all_predictions_binary)

    sns.heatmap(conf_mat, annot=True, fmt="d")
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    
    file_path = get_confusion_matrix_file_path()
    plt.savefig(file_path)
    plt.close()
    


def generate_roc_curve(all_ground_truth, all_predictions):
    fpr, tpr, thresholds = roc_curve(all_ground_truth, all_predictions)
    plt.plot(fpr, tpr, lw=2)
    plt.plot([0, 1], [0, 1], linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    
    file_path = get_roc_curve_file_path()
    plt.savefig(file_path)
    plt.close()
    


# Plotting the metrics
def plot_evaluation_results(accuracy_list, f1_score_list, recall_list, precision_list):
    
    epochs = range(1, len(accuracy_list) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, accuracy_list, label='Accuracy')
    plt.plot(epochs, f1_score_list, label='F1-Score')
    plt.plot(epochs, recall_list, label='Recall')
    plt.plot(epochs, precision_list, label='Precision')

    plt.xlabel('Epochs')
    plt.ylabel('Metrics')
    plt.title('Metrics Over Epochs')
    plt.legend()
    
    
    file_path = get_evaluation_result_path()
    plt.savefig(file_path)
    plt.close()
    

def plot_label_distribution(train_data):
    label_counts = Counter(train_data.y.numpy())
    print(label_counts)

    labels, counts = zip(*label_counts.items())
    plt.bar(labels, counts)
    plt.xlabel('Labels')
    plt.ylabel('Counts')
    plt.title('Distribution of Labels in the Dataset')
    plt.show()
    plt.close()
    

def plot_trainings_loss(train_losses, validation_losses):
    
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(validation_losses, label='Validation Loss')
    plt.title('Loss Evolution')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    file_name = get_trainings_loss_file_path()
    plt.savefig(file_name)
    plt.close()


def plot_embeddings(embeddings, epoch, folder_path, file_name):
    
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    tsne = TSNE(n_components=2,init='pca', learning_rate='auto')
    reduced_embeddings = tsne.fit_transform(embeddings.cpu().detach().numpy())

    # colors = ['red' if label == 1 else 'blue' for label in labels]
    # plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=colors, marker='o', s=5)
    
    plt.figure(figsize=(10,10))
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], marker='o', s=5)
    plt.title(f'Embeddings at Epoch {epoch}')
    
    plt.savefig(os.path.join(folder_path, file_name))
    plt.close()
