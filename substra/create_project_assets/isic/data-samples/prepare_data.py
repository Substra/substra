"""Script to prepare data before registering them on Substra Platform"""
import os
import pandas as pd
import tarfile

# absolute path to the ISIC2018_Task3_Training_Input folder containing LICENSE.txt and images
DATA_FOLDER = ""
# absolutl ve path of the ISIC2018_Task3_Training_GroundTruth.csv file
LABEL_FILE_PATH = ""


features_id = [ff.split(".")[0] for ff in os.listdir(DATA_FOLDER) if ".jpg" in ff]

# Create one label file for each data
labels = pd.read_csv(LABEL_FILE_PATH, index_col=0)
labels = labels.loc[features_id]

for _, row in labels.iterrows():
    filename = row.name.replace("ISIC", "LABEL") + ".csv"
    pd.DataFrame(row).T.to_csv(os.path.join(DATA_FOLDER, filename), header=None, index=False)

# Rename images files
for fid in features_id:
    filename = fid + ".jpg"
    os.rename(os.path.join(DATA_FOLDER, filename), os.path.join(DATA_FOLDER,
                                                                filename.replace("ISIC",
                                                                                 "IMG")))

# Create archives
for fid in features_id:
    fid = fid.split('_')[1]
    archive = tarfile.open(name=fid + ".tar.gz",
                           mode="w:gz")
    archive.add(os.path.join(DATA_FOLDER, "LICENSE.txt"), recursive=False)
    archive.add(os.path.join(DATA_FOLDER, 'LABEL_' + fid + '.csv'), recursive=False)
    archive.add(os.path.join(DATA_FOLDER, 'IMG_' + fid + '.jpg'), recursive=False)
    archive.close()
