import wget
import zipfile

import pandas as pd
import numpy as np

from data_analisys import paths


def download_data():
    wget.download(paths.raw_data_web_path, paths.raw_zipped_data_path)
    with zipfile.ZipFile(paths.raw_zipped_data_path, "r") as zip_ref:
        zip_ref.extractall(paths.raw_data_directory)


def generate_category(data):
    randomizer = np.random.RandomState(42)
    category_names = np.array([
        'Eatery',
        'Restaurants',
        'Shopping',
        'Additional',
        'Transport',
        'Housing',
        'Music',
        'Tourism',
        'Pets',
        'Children',
        'Cultural entertainment',
        'Wellness beauty',
        'Health',
        'Hobbies',
        'Insurance',
    ])

    category_probs = np.array([
        2093960,
        933692,
        733692,
        666811,
        588298,
        375832,
        475832,
        266824,
        227481,
        196072,
        180628,
        146150,
        127001,
        104744,
        79212,
    ])
    category_probs = category_probs / category_probs.sum()

    values_account, counts_account = np.unique(data.counterpartyAccountName, return_counts=True)
    sort = np.argsort(counts_account)[::-1]
    values_account = values_account[sort]
    counts_account = counts_account[sort]
    account_probs = counts_account / counts_account.sum()

    account_bins = np.ones_like(account_probs) * -1
    probs_ = category_probs.copy()
    for i in range(len(account_probs)):
        if counts_account[i] > 16:
            value = randomizer.choice(np.arange(3), p=probs_[:3] / probs_[:3].sum())
        else:
            value = randomizer.choice(np.arange(probs_.shape[0]), p=probs_ / probs_.sum())
        probs_[value] -= account_probs[i]
        probs_[value] = max(0, probs_[value])
        account_bins[i] = value
    account_bins = account_bins.astype(int)

    values_account_index = {
        name: i for i, name in enumerate(values_account)
    }

    category_list = []
    for name in data.counterpartyAccountName:
        bin_ = account_bins[values_account_index[name]]
        category = category_names[bin_]
        category_list.append(category)

    data['category'] = category_list
    return data


def process_date(data):
    data['timestamp'] = pd.to_datetime(data.timestamp)
    return data


def postprocess_data():
    data = pd.read_csv(paths.raw_data_path, sep=';')
    data = generate_category(data)
    data = process_date(data)
    data.to_csv(paths.post_processed_data_path, index=False)
    return data


def set_types(data):
    data = process_date(data)
    return data


def generate_ids(data):
    unique_users = data.accountName.unique()
    unique_users_num = unique_users.shape[0]
    ids = np.arange(unique_users_num).astype(int)
    return {id: name for id, name in zip(ids, unique_users)}


def generate_health_score(number):
    randomizer = np.random.RandomState(42)
    return randomizer.rand(number) * 5
