"""
========
Template
========

This is a template of how to make a new examples for Connectlib

"""

# Author: Maria Telenczuk <https://github.com/maikia>
#
# License: TODO: what license are we using?

# %%
# If you wish to make a new explanatory note in your document use '%%' in the first line of you comment.
# If you only use `#` the comment will be considered as a Python comment.
# On how to structure your Python scripts for Sphinx-Gallery: https://sphinx-gallery.github.io/stable/syntax.html
#
# In between you can use normal Python code to be run in your example:


import matplotlib.pyplot as plt
import numpy as np

# %%
# Syntax
# ------
#
# Follow rules for reStructured text, eg you can find some explanations
#  `here <https://www.writethedocs.org/guide/writing/reStructuredText/>`_.
#
# Let's now generate some imaginery data. Let's say we have 5 partners and we tested 4 models
# only that, for exemplary purposes, we will only randomly generate the final results
# obtained by each model at each site.
#

partners = ["Hospital 1", "Hospital 2", "Pharma 1", "Pharma 2", "Pharma 3"]
models = ["Model A", "Model B", "Model C", "Model D"]
np.random.seed(42)
results = np.random.random([len(partners), len(models)])


# %%
# What next?
# ----------
#
# We can now keep explaining what we are doing in the example.
# Here let's just make some pretty matplotlib figure.
#
# Do not forget to use a reasonable colormaps for your figures and consider color-blind people when choosing your
# colors (eg in `matplotlib <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_).

fig, ax = plt.subplots()
im = ax.imshow(results, cmap="viridis")

# We want to show all ticks...
ax.set_xticks(np.arange(len(partners)))
ax.set_yticks(np.arange(len(models)))
# ... and label them with the respective list entries
ax.set_xticklabels(partners)
ax.set_yticklabels(models)

# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
for i in range(len(partners)):
    for j in range(len(models)):
        text = ax.text(j, i, round(results[i, j], 2), ha="center", va="center", color="w")

ax.set_title("Results from Federated Learning in different partners")
fig.tight_layout()
plt.show()

# %%
# Wrapping up
# -----------
#
# Once you have your in-depth, simple and beautiful example ready you need to embed it in the
# structure of the Connectlib docs:
# TODO: explain
#
# And you can test it:
# TODO: explain

# %%
# References
# -----------
#
# And of course, never forget to cite all the materials you might have used in your tutorial.
#
# Here, I adapted
# `matplotlib example <https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html#sphx-glr-gallery-images-contours-and-fields-image-annotated-heatmap-py>`_
# to Connectlib reality.
