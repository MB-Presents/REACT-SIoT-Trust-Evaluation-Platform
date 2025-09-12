import os
from pathlib import Path
import sys

import sys
sys.path.insert(0, '/app')



from dataset_builder.utils.path_helper import DATASET_TASK, DatasetType, get_graph_images_timeslot_output_path, get_output_video_path, set_constants
sys.path.insert(0, '/app')

import numpy as np
import cv2

from PIL import Image


BUILD_DEVICE = 'local'



def rename_files(directory):
    # List all files in the directory
    files = os.listdir(directory)
    # Filter out files that do not start with 'graph_' and end with '.png'
    graph_files = [f for f in files if f.startswith('graph_') and f.endswith('.png')]
    # Iterate over each file
    for file in graph_files:
        # Extract the number part from the file name
        number = int(file.split('_')[1].split('.')[0])
        # Create a new file name with leading zeros
        new_file_name = f'graph_{number:04}.png'
        # Rename the file
        os.rename(os.path.join(directory, file), os.path.join(directory, new_file_name))



def get_creation_date(file_path):
    return file_path.stat().st_ctime

def process_images_batch(images):
    return [np.array(image) for image in images]

def create_video(get_creation_date, process_images_batch):
    
    
    BUILD_DEVICE = 'local'
    DATASET_TYPE = DatasetType.NODE_CLASSIFICATION_SITUATION_LABELS.value
    set_constants(DATASET_TYPE, dataset_task=DATASET_TASK)
    
    
    # image_directory = get_graph_images_timeslot_output_path()
    image_directory = Path("/app/output/trust_network/with_transaction_exchange")
    renamed_files = rename_files(image_directory)
    
    
    image_files = sorted(image_directory.iterdir(), key=lambda x: x.name)

    common_shape = (1280, 960)  # Width: 640, Height: 480

    batch_size = 50  
    total_images = len(image_files)

    BUILD_DEVICE = 'local'
    # output_video_path = Path("/app")
    # output_video_path = get_output_video_path(DATASET_TYPE, BUILD_DEVICE)
    output_video_path = os.path.join("/app", "trust_network_with_transaction_exchange.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video = cv2.VideoWriter(output_video_path, fourcc, 20.0, common_shape)

    for batch_start in range(0, total_images, batch_size):
        batch_end = min(batch_start + batch_size, total_images)
        batch_files = image_files[batch_start:batch_end]

        resized_images = [Image.open(img_file).resize(common_shape) for img_file in batch_files]
        images = process_images_batch(resized_images)

        for image in images:
            
            bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            video.write(bgr_image)

    video.release()
    cv2.destroyAllWindows()

    print("Video created")


create_video(get_creation_date, process_images_batch)