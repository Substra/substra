# Substra Documentation

Substra is a **framework for secure and traceable machine learning (ML) on sensitive distributed datasets**. 
Substra deploys a network of nodes containing dataset over which it orchestrates training of machine learning models on data that remain stored in the nodes.


## Before we start

To enable machine learning on distributed data, four types of objects are defined within a Substra network: 
  - **Objective**   
    It clearly defines the scientific question to be answered with a ML model.
    It specifies:
      - the data format that the **Dataset**, **Algo** and **Model** have to follow, 
      - the identity of the test data points used to compare and evaluate the models, 
      - the metrics script which is used to quantify the accuracy of a model.
  - **Dataset**  
      It aggregates numerous data points under a single format.                                        
    It includes a single *Opener* script which imports and opens the file using libraries specific to the data type.
  - **Algo** (Algorithm)  
	It corresponds to a script which specifies the method to train a **Model** on a **Dataset**. 
	In particular it specifies the model type and architecture, the loss function, the optimizer, hyperparameters and identifies the parameters that are tuned during training.
	Algo dependencies are also specified.
  - **Model**  
    It corresponds to a file containing the parameters of a trained model.                  
    In the case of neural networks, it gathers the weights of the connections. 
    It is associated with:
      - training tasks specification (*Traintuple*)  
	  A *Traintuple* specifies which **Algo** must be trained on which **Dataset** for which **Objective** and starting from which **Model(s)**
	  Once the training is done, it specifies the resulting **Model**.
      - evaluation tasks specification (*Testtuple*) 
	  A **Testtuple** specifies the output of Traintuple to be evaluated. This corresponds to evaluating a **Model** against a (test) **Dataset** associated with an **Objective**. 

The core idea of Substra is to keep **Dataset** in the different nodes of a network and make **Algo** and **Models** travel from one node to another to train them on **Dataset**.

## How to use it?

- How to implement your assets in python?
    - [Objective](https://github.com/SubstraFoundation/substratools/blob/dev/docs/api.md#metrics)
    - [Dataset](https://github.com/SubstraFoundation/substratools/blob/dev/docs/api.md#opener)
    - [Algo](https://github.com/SubstraFoundation/substratools/blob/dev/docs/api.md#algo)

- How to interact with a Substra network?
    - [Using the Python SDK](https://github.com/SubstraFoundation/substra-cli/blob/dev/docs/sdk.md)
    - [Using the Substra CLI](https://github.com/SubstraFoundation/substra-cli/blob/dev/docs/cli.md)

- Examples
    - [Prerequisites](./examples/prerequisites.md)
    - [Titanic](./examples/titanic/README.md) 
    - [Cross-validation](./examples/cross_val/README.md)
    - [Compute plan](./examples/compute_plan/README.md)

- [How to install a Substra network locally on your machine?](./local_install.md)

## How does Substra work?
  - [Concepts](./concepts.md)
  - [Machine Learning tasks](./ml_tasks.md)


### Contributing

#### To this documentation

For any bug/ please report them as an issue. 
Please contact camille.marini@owkin.com or mathieu.galtier@owkin.com for human inquiries.

#### To Substra in general 

TODO: add link to code guidelines
