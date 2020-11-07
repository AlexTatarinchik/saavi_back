import os

import pandas as pd

from data_analisys import paths, utils
from datetime import datetime, timedelta

from data_analisys.subscription_analyser import SubscribtionAnalyser


class DataAnalyser:
    def __init__(self):
        if not os.path.exists(paths.post_processed_data_path):
            self._download_and_postprocess_data()
        self.data = pd.read_csv(paths.post_processed_data_path)
        self.data = utils.set_types(self.data)
        self.user_name_dict = utils.generate_ids(self.data)
        self.user_health_dict = utils.generate_health_score(len(self.user_name_dict))
        self.category_image_dict = utils.get_category_image_dict()
        self.subscribtion_analyser = SubscribtionAnalyser()
        self.subscription_id_dict = utils.subscription_id_dict(len(self.user_name_dict))

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
        if user_id == 1:
            user_avatar_url = '/images/Obsession-Joaquin-Phoenix-Her-Header-11217.jpg'
        user_balance = self.get_user_balance(user_name)
        user_month_subscribtion_payment = 0
        return {
            'user_name': user_name,
            'user_health': user_health,
            'user_avatar_url': user_avatar_url,
            'user_balance': user_balance,
            'user_month_subscribtion_payment': user_month_subscribtion_payment
        }

    def _get_most_popular_categories(self, account_slice, reference_datetime, previous_datetime_end, previous_datetime_start):
        group = 'category'
        current_time_slice = account_slice[
            (account_slice.timestamp > previous_datetime_end) & (account_slice.timestamp < reference_datetime)]
        previous_time_slice = account_slice[
            (account_slice.timestamp > previous_datetime_start) & (account_slice.timestamp < previous_datetime_end)]
        current_spendings = current_time_slice.groupby(group).amount.sum() * -1
        previous_spendings = previous_time_slice.groupby(group).amount.sum() * -1

        current_spendings = current_spendings.loc[current_spendings.index.isin(previous_spendings.index)]
        previous_spendings = previous_spendings.loc[previous_spendings.index.isin(current_spendings.index)]

        spendings_delta = current_spendings - previous_spendings
        counts = current_time_slice.groupby(group).amount.count()

        argsort = spendings_delta.argsort()
        return_array = []
        for index in argsort:
            name = spendings_delta.index[index]
            change = current_spendings.loc[name] / previous_spendings.loc[name] - 1

            if name in self.category_image_dict:
                image_name = self.category_image_dict[name]
            else:
                image_name = ""
            return_dict = {
                'image_name': image_name,
                'amount': current_spendings[name],
                'number_of_transactions': int(counts[name]),
                'name': name,
                'change': float(change),
            }
            return_array.append(return_dict)
        return return_array

    def _get_insides(self, account_slice, reference_datetime, previous_datetime_end, previous_datetime_start, group, choose_by_freq):
        current_time_slice = account_slice[
            (account_slice.timestamp > previous_datetime_end) & (account_slice.timestamp < reference_datetime)]
        previous_time_slice = account_slice[
            (account_slice.timestamp > previous_datetime_start) & (account_slice.timestamp < previous_datetime_end)]

        current_spendings = current_time_slice.groupby(group).amount.sum() * -1
        previous_spendings = previous_time_slice.groupby(group).amount.sum() * -1

        current_spendings = current_spendings.loc[current_spendings.index.isin(previous_spendings.index)]
        previous_spendings = previous_spendings.loc[previous_spendings.index.isin(current_spendings.index)]

        spendings_delta = current_spendings - previous_spendings
        counts = current_time_slice.groupby(group).amount.count()
        if not choose_by_freq:
            argmax = spendings_delta.argmax()
            name = spendings_delta.index[argmax]
        else:
            argmax = counts.argmax()
            name = counts.index[argmax]
        change = current_spendings.loc[name]/previous_spendings.loc[name] - 1

        if name in self.category_image_dict:
            image_name = self.category_image_dict[name]
        else:
            category_name = current_time_slice[current_time_slice[group] == name]['category'].iloc[0]
            image_name = self.category_image_dict[category_name]

        return_dict = {
            'image_name': image_name,
            'amount': current_spendings[name],
            'number_of_transactions': int(counts[name]),
            'name': name,
            'change': float(change),
        }
        return return_dict

    def get_popular_categories(self, user_id, date, type):
        user_name = self.user_name_dict[user_id]
        account_slice = self._get_user_slice(user_name)

        if date == "last":
            max_date = account_slice.timestamp.max()
            date = f'{max_date.year}-{max_date.month}-{max_date.day}'
        reference_datetime = datetime.strptime(date, '%Y-%m-%d')
        if type == 'day':
            previous_datetime_end = reference_datetime - timedelta(days=1)
            previous_datetime_start = previous_datetime_end - timedelta(days=1)
        elif type == 'week':
            previous_datetime_end = reference_datetime - timedelta(weeks=1)
            previous_datetime_start = previous_datetime_end - timedelta(weeks=1)
        elif type == 'month':
            previous_datetime_end = reference_datetime - timedelta(weeks=4)
            previous_datetime_start = previous_datetime_end - timedelta(weeks=4)


        return self._get_most_popular_categories(
            account_slice,
            reference_datetime,
            previous_datetime_end,
            previous_datetime_start
        )

    def get_insides(self, user_id, date, type):
        user_name = self.user_name_dict[user_id]
        account_slice = self._get_user_slice(user_name)

        if date == "last":
            max_date = account_slice.timestamp.max()
            date = f'{max_date.year}-{max_date.month}-{max_date.day}'

        reference_datetime = datetime.strptime(date, '%Y-%m-%d')
        if type == 'day':
            previous_datetime_end = reference_datetime - timedelta(days=1)
            previous_datetime_start = previous_datetime_end - timedelta(days=1)
        elif type == 'week':
            previous_datetime_end = reference_datetime - timedelta(weeks=1)
            previous_datetime_start = previous_datetime_end - timedelta(weeks=1)
        elif type == 'month':
            previous_datetime_end = reference_datetime - timedelta(weeks=4)
            previous_datetime_start = previous_datetime_end - timedelta(weeks=4)

        more_of_brand = self._get_insides(
            account_slice,
            reference_datetime,
            previous_datetime_end,
            previous_datetime_start,
            group='counterpartyAccountName',
            choose_by_freq=True,
        )

        more_of_category = self._get_insides(
            account_slice,
            reference_datetime,
            previous_datetime_end,
            previous_datetime_start,
            group='category',
            choose_by_freq=False,
        )

        return {
            'more_of_brand': more_of_brand,
            'more_of_category': more_of_category
        }

    def get_user_subscrption_prediction(self, user_id):
        sub_user_id = self.subscription_id_dict[user_id]
        return self.subscribtion_analyser.predict_user(sub_user_id)

    def get_active_subscriptions(self, user_id):
        sub_user_id = self.subscription_id_dict[user_id]
        return self.subscribtion_analyser.get_active_subscriptions(sub_user_id)

    def get_next_two_subscriptions(self, user_id, current_day=8):
        sub_user_id = self.subscription_id_dict[user_id]
        return self.subscribtion_analyser.get_next_two_subscriptions(sub_user_id, current_day)







