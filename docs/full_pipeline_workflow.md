# Adding a full pipeline

In order to add a full pipeline, you'll have to follow these steps **in this order**:

1. Data prep
   1. split your raw data into individual data assets
   2. split these assets between train and test
2. Add dataset
   1. write an opener following [the requirements](https://github.com/SubstraFoundation/substratools/blob/dev/docs/api.md#opener)
   2. write a text describing the dataset, its structure and content
   3. write and push a [json description of the dataset](../references/cli.md#substra-add-dataset)
3. [Add the prepared data assets](../references/cli.md#substra-add-data_sample)
4. Add objective
   1. write a metrics file following [the requirements](https://github.com/SubstraFoundation/substratools/blob/dev/docs/api.md#metrics)
   2. write a text describing the objective and how it's evaluated
   3. write and push [json description of the objective](../references/cli.md#substra-add-objective)
5. Add algo
   1. write your algorithm script following [the requirements](https://github.com/SubstraFoundation/substratools/blob/dev/docs/api.md#algo)
   2. write a targz archive with Dockerfile and algo script
   3. write a text describing the algo
   4. write and push a [json description of the algorithm](../references/cli.md#substra-add-algo)
6. [Add a traintuple to launch training task](../references/cli.md#substra-add-traintuple)

You can see a full example of this in the [Titanic example](../examples/titanic)
