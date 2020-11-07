import os

import pandas as pd

from data_analisys import paths, utils


class DataAnalyser:
    def __init__(self):
        if not os.path.exists(paths.post_processed_data_path):
            self._download_and_postprocess_data()
        self.data = pd.read_csv(paths.post_processed_data_path)
        self.data = utils.set_types(self.data)
        self.user_name_dict = utils.generate_ids(self.data)
        self.user_health_dict = utils.generate_health_score(len(self.user_name_dict))

    def _download_and_postprocess_data(self):
        utils.download_data()
        utils.postprocess_data()

    def _get_user_slice(self, account_name):
        return self.data[self.data.accountName == account_name]

    def get_user_balance(self, account_name):
        account_slice = self._get_user_slice(account_name)
        balance = account_slice.iloc[account_slice.timestamp.argmax()].balance
        return balance

    def get_user_info(self, user_id):
        user_name = self.user_name_dict[user_id]
        user_health = self.user_health_dict[user_id]
        user_avatar_url = ""
        user_balance = self.get_user_balance(user_name)
        return {
            'user_name': user_name,
            'user_health': user_health,
            'user_avatar_url': user_avatar_url,
            'user_balance': user_balance
        }








