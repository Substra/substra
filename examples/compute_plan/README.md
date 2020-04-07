# Compute plan

> Important
> This example relies on the assets setup by the [Titanic example](../titanic/README.md). In order to run the following
code snippets, you'll need the `assets_keys.json` generated while running the Titanic example.

In the Titanic example, we trained our algos on all the available data samples simultaneously. In this example, we'll
go a different route, training our algo on a single data sample at once, chaining our training tasks so that the
resulting model improves with each individual step.

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

