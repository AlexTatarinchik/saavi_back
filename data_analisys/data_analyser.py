import os
import subprocess

import pandas as pd

from data_analisys import paths, utils


class DataAnalyser:
    def __init__(self):
        if not os.path.exists(paths.post_processed_data_path):
            self._download_and_postprocess_data()
        self.data = pd.read_csv(paths.post_processed_data_path)

    def _download_and_postprocess_data(self):
        utils.download_data()
        utils.postprocess_data()

    def _get_user_slice(self, account_name):
        return self.data[self.data.accountName == account_name]







