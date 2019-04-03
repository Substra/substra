# Skin Lesion Classification 

Problem based on [ISIC 2018 challenge](https://challenge2018.isic-archive.com/task3/). 

## Goal

Submit automated predictions of disease classification within **dermoscopic images**.

Possible disease categories are:

- Melanoma
- Melanocytic nevus
- Basal cell carcinoma
- Actinic keratosis / Bowen’s disease (intraepithelial carcinoma)
- Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis)
- Dermatofibroma
- Vascular lesion

## Evaluation metric

Predicted responses are scored using a **macro averaged recall**.

## Test dataset description

Test dataset features are numpy array of shape (n_test_samples, 450, 600, 3).

## Predictions format

Dataset opener must implement the `save_pred` function so that it creates a `pred/pred.csv` file with one line for each sample (same order as features returned by the opener `get_X` function) and 7 columns contaning the probability of belonging to each of the seven classes.