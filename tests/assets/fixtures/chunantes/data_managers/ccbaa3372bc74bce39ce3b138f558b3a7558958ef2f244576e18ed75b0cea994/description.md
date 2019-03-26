# ISIC 2018


The dataset consists of 10015:
- images of size (450, 600, 3) 
- ground truth response one line CSV files, with 7 columns corresponding to diagnosis confidence for:
  -  Melanoma (MEL)
  -  Melanocytic nevus (NV)
  -  Basal cell carcinoma (BCC)
  -  Actinic keratosis / Bowen’s disease (intraepithelial carcinoma) (AKIEC)
  -  Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis) (BKL)
  -  Dermatofibroma (DF)
  -  Vascular lesion (VASC).


The dataset was extracted from the “[ISIC 2018](https://challenge2018.isic-archive.com/task3/training/): Skin Lesion Analysis Towards Melanoma Detection” grand challenge datasets [\[1\]](#ref1)[[2]](#ref2).

Data is provided by ISIC 2018 under the terms of the Creative Commons Attribution-NonCommercial (CC BY-NC) 4.0 license. If you are unable to accept the terms of this license, do not download or use this data.

### Opener output

```
import opener

X = opener.get_X(folder)  # numpy array with shape (n_samples, 450, 600, 3)
y = opener.get_y(folder)  # numpy array with shape (n_samples,7)
```


**References**  
<a name="ref1">[1]</a> Noel C. F. Codella, David Gutman, M. Emre Celebi, Brian Helba, Michael A. Marchetti, Stephen W. Dusza, Aadi Kalloo, Konstantinos Liopyris, Nabin Mishra, Harald Kittler, Allan Halpern: “Skin Lesion Analysis Toward Melanoma Detection: A Challenge at the 2017 International Symposium on Biomedical Imaging (ISBI), Hosted by the International Skin Imaging Collaboration (ISIC)”, 2017; arXiv:1710.05006.  
<a name="ref2">[2]</a> Philipp Tschandl, Cliff Rosendahl, Harald Kittler: “The HAM10000 Dataset: A Large Collection of Multi-Source Dermatoscopic Images of Common Pigmented Skin Lesions”, 2018; arXiv:1803.10417.