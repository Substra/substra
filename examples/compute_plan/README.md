# Compute plan

> :warning: 
> This example relies on the assets setup by the [Titanic example](../titanic/README.md). In order to run the following 
code snippets, you'll need to have run the Titanic example before 
(or at least make sure you have submitted the Titanic objective and datasets of Node 0 and 1).  

In the Titanic example, we trained our algo on all data samples of Node 0 and then on all data samples of Node 1. 

In this example, we'll train our algo sequentially on part of the data samples of Node 0, then part of the data samples of Node 1, then again on part of the data samples of Node 0, etc ...  

To do so, we'll generate a *compute plan* that describes each step of the training and have each of these steps 
evaluated against the objective's test data so that we can see the score improving. 

We'll also need to add an updated version of the regression algo that can reuse a previously trained model.

To submit the new algo and the compute plan, run:
```sh
python scripts/add_compute_plan.py
```

And to display the growing scores, run:
```sh
python scripts/display_scores.py
```

You can use the `watch` command to refresh the scores as soon as they are available:
```sh
watch python scripts/display_scores.py
```

