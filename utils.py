import torch
import numpy as np
import pandas as pd
import torch.nn.functional as F
import torch.nn as nn
import logging
import os
import tqdm
from torch.utils.data import Dataset, DataLoader

def get_logger(log_dir, name):
    """Get a `logging.Logger` instance that prints to the console
    and an auxiliary file.

    Args:
        log_dir (str): Directory in which to create the log file.
        name (str): Name to identify the logs.

    Returns:
        logger (logging.Logger): Logger instance for logging events.
        
    Credit: Stanford CS 224N Default Project code
    """
    class StreamHandlerWithTQDM(logging.Handler):
        """Let `logging` print without breaking `tqdm` progress bars.

        See Also:
            > https://stackoverflow.com/questions/38543506
        """
        def emit(self, record):
            try:
                msg = self.format(record)
                tqdm.tqdm.write(msg)
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Log everything (i.e., DEBUG level and above) to a file
    log_path = os.path.join(log_dir, 'log.txt')
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    # Log everything except DEBUG level (i.e., INFO level and above) to console
    console_handler = StreamHandlerWithTQDM()
    console_handler.setLevel(logging.INFO)

    # Create format for the logs
    file_formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                       datefmt='%m.%d.%y %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                          datefmt='%m.%d.%y %H:%M:%S')
    console_handler.setFormatter(console_formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_available_devices():
    """Get IDs of all available GPUs

    Returns:
        device (torch.device): Main device (GPU 0 or CPU)
        gpu_ids (list): list of IDs of all GPUs that are available
    """
    gpu_ids = []
    if torch.cuda.is_available():
        gpu_ids += [gpu_id for gpu_id in range(torch.cuda.device_count())]
        device = torch.device('cuda:{}'.format(gpu_ids[0]))
        torch.cuda.set_device(device)
    else:
        device = torch.device('cpu')

    return device, gpu_ids

def cuda(x):
    return x.cuda(non_blocking=True)

def check_early_stopping(scores, patience=5, threshold=3e-3):
    """
    Stop if validation scores haven't increased for patience
    
    input: validation scores (list)
           patience (integer)
    returns: whether to early stop (bool)
    """
    
    x = scores[::-1]
    counter = 0
    for i in range(1, patience):
        if x[i] > x[i+1] + threshold:
            counter = 0
        else:
            counter += 1
        if counter >= patience:
            print("Early stopping...")
            return True
        
    return False
