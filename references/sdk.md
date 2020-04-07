### class substra.Client(config_path=None, profile_name=None, user_path=None, retry_timeout=300)
Client to interact with a Substra node.


* **Parameters**

    
    * **config_path** (*str**, **optional*) – The path to the config file to load. Defaults to ‘~/.substra’


    * **profile_name** (*str**, **optional*) – The name of the profile to set as current profile. Defaults
    to ‘default’


    * **user_path** (*str**, **optional*) – The path to the user file to load. Defaults to ‘~/.substra-user’


    * **retry_timeout** (*int**, **optional*) – Number of seconds to wait before retry when an add request
    timeouts. Defaults to 300 (5min)



#### add_aggregate_algo(data, exist_ok=False)
Creates a new aggregate algo asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “name”: str,
        “description”: str,
        “file”: str,
        “permissions”: {

        > ”public”: bool,
        > “authorizedIDs”: list[str],

        },

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – An aggregate algo with the same archive file already exists on the
        server.



#### add_aggregatetuple(data, exist_ok=False)
Creates a new aggregatetuple asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “algo_key”: str,
        “in_models_keys”: list[str],
        “tag”: str,
        “compute_plan_id”: str,
        “rank”: int,
        “worker”: str,

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A traintuple already exists on the server that:

        \* has the same algo_key and in_models_keys
        \* was created through the same node this Client instance points to



#### add_algo(data, exist_ok=False)
Creates a new algo asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “name”: str,
        “description”: str,
        “file”: str,
        “permissions”: {

        > ”public”: bool,
        > “authorized_ids”: list[str],

        },

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – An algo with the same archive file already exists on the server.



#### add_composite_algo(data, exist_ok=False)
Creates a new composite algo asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “name”: str,
        “description”: str,
        “file”: str,
        “permissions”: {

        > ”public”: bool,
        > “authorizedIDs”: list[str],

        },

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A composite algo with the same archive file already exists on the
        server.



#### add_composite_traintuple(data, exist_ok=False)
Creates a new composite traintuple asset.

As specified in the data dict structure, output trunk models cannot be made
public.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “algo_key”: str,
        “data_manager_key”: str,
        “in_head_model_key”: str,
        “in_trunk_model_key”: str,
        “out_trunk_model_permissions”: {

        > ”authorized_ids”: list[str],

        },
        “tag”: str,
        “rank”: int,
        “compute_plan_id”: str,

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A traintuple already exists on the server that:

        \* has the same algo_key, data_manager_key, train_data_sample_keys,
          in_head_models_key and in_trunk_model_key
        \* was created through the same node this Client instance points to



#### add_compute_plan(data)
Creates a new compute plan asset.

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.


* **Parameters**

    **data** (*dict*) – Must have the following schema

    {

        “traintuples”: list[{

            “traintuple_id”: str,
            “algo_key”: str,
            “data_manager_key”: str,
            “train_data_sample_keys”: list[str],
            “in_models_ids”: list[str],
            “tag”: str,

        }],
        “composite_traintuples”: list[{

        > ”composite_traintuple_id”: str,
        > “algo_key”: str,
        > “data_manager_key”: str,
        > “train_data_sample_keys”: list[str],
        > “in_head_model_id”: str,
        > “in_trunk_model_id”: str,
        > “out_trunk_model_permissions”: {

        > > ”authorized_ids”: list[str],

        > },
        > “tag”: str,

        }]
        “aggregatetuples”: list[{

        > ”aggregatetuple_id”: str,
        > “algo_key”: str,
        > “worker”: str,
        > “in_models_ids”: list[str],
        > “tag”: str,

        }],
        “testtuples”: list[{

        > ”objective_key”: str,
        > “data_manager_key”: str,
        > “test_data_sample_keys”: list[str],
        > “traintuple_id”: str,
        > “tag”: str,

        }],
        “clean_models”: bool,
        “tag”: str

    }




* **Returns**

    The newly created asset.



* **Return type**

    dict



#### add_data_sample(data, local=True, exist_ok=False)
Creates a new data sample asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “path”: str,
        “data_manager_keys”: list[str],
        “test_only”: bool,

    }

    The path in the data dictionary must point to a directory representing the
    data sample content. Note that the directory can contain multiple files, all the
    directory content will be added to the platform.



    * **local** (*bool*) – If true, path must refer to a directory located on the local
    filesystem. The file content will be transferred to the server through an
    HTTP query, so this mode should be used for relatively small files (<10mo).

    If false, path must refer to a directory located on the server
    filesystem. This directory must be accessible (readable) by the server.  This
    mode is well suited for all kind of file sizes.



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A data sample with the same content already exists on the server.



#### add_data_samples(data, local=True)
Creates multiple new data sample assets.

This method is well suited for adding multiple small files only. For adding a
large amount of data it is recommended to add them one by one. It allows a
better control in case of failures.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “paths”: list[str],
        “data_manager_keys”: list[str],
        “test_only”: bool,

    }

    The paths in the data dictionary must be a list of paths where each path
    points to a directory representing one data sample.



    * **local** (*bool*) – If true, path must refer to a directory located on the local
    filesystem. The file content will be transferred to the server through an
    HTTP query, so this mode should be used for relatively small files (<10mo).

    If false, path must refer to a directory located on the server
    filesystem. This directory must be accessible (readable) by the server.  This
    mode is well suited for all kind of file sizes.




* **Returns**

    The newly created assets



* **Return type**

    list[dict]



* **Raises**

    **AlreadyExists** – data samples with the same content as some of the paths already exist on
        the server.



#### add_dataset(data, exist_ok=False)
Creates a new dataset asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “name”: str,
        “description”: str,
        “type”: str,
        “data_opener”: str,
        “objective_key”: str,
        “permissions”: {

        > ”public”: bool,
        > “authorized_ids”: list[str],

        },

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A dataset with the same opener already exists on the server.



#### add_objective(data, exist_ok=False)
Creates a new objective asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “name”: str,
        “description”: str,
        “metrics_name”: str,
        “metrics”: str,
        “test_data_manager_key”: str,
        “test_data_sample_keys”: list[str],
        “permissions”: {

        > ”public”: bool,
        > “authorized_ids”: list[str],

        },

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – An objective with the same description already exists on the server.



#### add_profile(profile_name, username, password, url, version='0.0', insecure=False)
Adds new profile and sets it as current profile.


* **Parameters**

    
    * **profile_name** (*str*) – The name of the new profile


    * **username** (*str*) – The username that will be used to get an authentication token


    * **password** (*str*) – The password that will be used to get an authentication token


    * **url** (*str*) – The URL of the node


    * **version** (*str*) – The version of the API to use. Defaults to 0.0


    * **insecure** (*bool*) – If true the node’s SSL certificate will not be verified. Defaults to
    False.



* **Returns**

    The new profile



* **Return type**

    dict



#### add_testtuple(data, exist_ok=False)
Creates a new testtuple asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “objective_key”: str,
        “data_manager_key”: str,
        “traintuple_key”: str,
        “test_data_sample_keys”: list[str],
        “tag”: str,

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A traintuple already exists on the server that:

        \* has the same traintuple_key, objective_key, data_manager_key and
          test_data_sample_keys
        \* was created through the same node this Client instance points to



#### add_traintuple(data, exist_ok=False)
Creates a new traintuple asset.


* **Parameters**

    
    * **data** (*dict*) – Must have the following schema

    {

        “algo_key”: str,
        “data_manager_key”: str,
        “train_data_sample_keys”: list[str],
        “in_models_keys”: list[str],
        “tag”: str,
        “rank”: int,
        “compute_plan_id”: str,

    }



    * **exist_ok** (*bool**, **optional*) – If true, AlreadyExists exceptions will be ignored and the
    existing asset will be returned. Defaults to False.



* **Returns**

    The newly created asset.



* **Return type**

    dict



* **Raises**

    **AlreadyExists** – A traintuple already exists on the server that:

        \* has the same algo_key, data_manager_key, train_data_sample_keys and in_models_keys
        \* was created through the same node this Client instance points to



#### cancel_compute_plan(compute_plan_id)
Cancels the execution of a compute plan.


* **Parameters**

    **compute_plan_id** (*str*) – The ID of the compute plan to cancel.



* **Returns**

    The canceled compute plan.



* **Return type**

    dict



#### describe_aggregate_algo(aggregate_algo_key)
Gets an aggregate algo description.


* **Parameters**

    **aggregate_algo_key** (*str*) – The key of the target aggregate algo.



* **Returns**

    The asset’s description.



* **Return type**

    str



#### describe_algo(algo_key)
Gets an algo description.


* **Parameters**

    **algo_key** (*str*) – The key of the target algo.



* **Returns**

    The asset’s description.



* **Return type**

    str



#### describe_composite_algo(composite_algo_key)
Gets a composite algo description.


* **Parameters**

    **composite_algo_key** (*str*) – The key of the target composite algo.



* **Returns**

    The asset’s description.



* **Return type**

    str



#### describe_dataset(dataset_key)
Gets a dataset description.


* **Parameters**

    **dataset_key** (*str*) – The key of the target dataset.



* **Returns**

    The asset’s description.



* **Return type**

    str



#### describe_objective(objective_key)
Gets an objective description.


* **Parameters**

    **objective_key** (*str*) – The key of the target objective.



* **Returns**

    The asset’s description.



* **Return type**

    str



#### download_aggregate_algo(aggregate_algo_key, destination_folder)
Downloads an aggregate algo archive.


* **Parameters**

    
    * **aggregate_algo_key** (*str*) – The key of the target aggregate algo.


    * **destination_folder** (*str*) – The path to the folder where the target aggregate algo’s
    archive should be downloaded.



#### download_algo(algo_key, destination_folder)
Downloads an algo archive.


* **Parameters**

    
    * **algo_key** (*str*) – The key of the target algo.


    * **destination_folder** (*str*) – The path to the folder where the target algo’s archive
    should be downloaded.



#### download_composite_algo(composite_algo_key, destination_folder)
Downloads a composite algo archive.


* **Parameters**

    
    * **composite_algo_key** (*str*) – The key of the target composite algo.


    * **destination_folder** (*str*) – The path to the folder where the target composite algo’s
    archive should be downloaded.



#### download_dataset(dataset_key, destination_folder)
Downloads a dataset opener.


* **Parameters**

    
    * **dataset_key** (*str*) – The key of the target dataset.


    * **destination_folder** (*str*) – The path to the folder where the target dataset’s opener
    should be downloaded.



#### download_objective(objective_key, destination_folder)
Downloads an objective metrics archive.


* **Parameters**

    
    * **objective_key** (*str*) – The key of the target objective.


    * **destination_folder** (*str*) – The path to the folder where the target objective’s
    metrics archive should be downloaded.



#### get_aggregate_algo(aggregate_algo_key)
Gets an aggregate algo by key.


* **Parameters**

    **aggregate_algo_key** (*str*) – The key of the aggregate algo



* **Raises**

    **NotFound** – The aggregate_algo_key did not match any aggregate algo.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_aggregatetuple(aggregatetuple_key)
Gets an aggregatetuple by key.


* **Parameters**

    **aggregatetuple_key** (*str*) – The key of the aggregatetuple



* **Raises**

    **NotFound** – The aggregatetuple_key did not match any aggregatetuple.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_algo(algo_key)
Gets an algo by key.


* **Parameters**

    **algo_key** (*str*) – The key of the algo



* **Raises**

    **NotFound** – The algo_key did not match any algo.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_composite_algo(composite_algo_key)
Gets a composite algo by key.


* **Parameters**

    **composite_algo_key** (*str*) – The key of the composite algo



* **Raises**

    **NotFound** – The composite_algo_key did not match any composite algo.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_composite_traintuple(composite_traintuple_key)
Gets a composite traintuple by key.


* **Parameters**

    **composite_traintuple_key** (*str*) – The key of the composite_traintuple



* **Raises**

    **NotFound** – The composite_traintuple_key did not match any composite_traintuple.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_compute_plan(compute_plan_key)
Gets a compute plan by key.


* **Parameters**

    **compute_plan_key** (*str*) – The key of the compute plan



* **Raises**

    **NotFound** – The compute_plan_key did not match any compute plan.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_dataset(dataset_key)
Gets a dataset by key.


* **Parameters**

    **dataset_key** (*str*) – The key of the dataset



* **Raises**

    **NotFound** – The dataset_key did not match any dataset.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_objective(objective_key)
Gets an objective by key.


* **Parameters**

    **objective_key** (*str*) – The key of the objective



* **Raises**

    **NotFound** – The objective_key did not match any objective.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_testtuple(testtuple_key)
Gets a testtuple by key.


* **Parameters**

    **testtuple_key** (*str*) – The key of the testtuple



* **Raises**

    **NotFound** – The testtuple_key did not match any testtuple.



* **Returns**

    The requested asset



* **Return type**

    dict



#### get_traintuple(traintuple_key)
Gets a traintuple by key.


* **Parameters**

    **traintuple_key** (*str*) – The key of the traintuple



* **Raises**

    **NotFound** – The traintuple_key did not match any traintuple.



* **Returns**

    The requested asset



* **Return type**

    dict



#### leaderboard(objective_key, sort='desc')
Gets an objective leaderboard


* **Parameters**

    
    * **objective_key** (*str*) – The key of the target objective.


    * **sort** (*str*) – Either ‘desc’ or ‘asc’. Whether to sort the leaderboard values by ascending
    order (lowest score first) or descending order (highest score first). Defaults to
    ‘desc’



* **Returns**

    The list of leaderboard tuples.



* **Return type**

    list[dict]



#### link_dataset_with_data_samples(dataset_key, data_sample_keys)
Links a dataset with data samples.


* **Parameters**

    
    * **dataset_key** (*str*) – The key of the dataset to link.


    * **data_sample_keys** (*list**[**str**]*) – The keys of the data samples to link.



* **Returns**

    The updated data samples.



* **Return type**

    list[dict]



#### link_dataset_with_objective(dataset_key, objective_key)
Links a dataset with an objective.


* **Parameters**

    
    * **dataset_key** (*str*) – The key of the dataset to link.


    * **objective_key** (*str*) – The key of the objective to link.



* **Returns**

    The updated dataset.



* **Return type**

    dict



#### list_aggregate_algo(filters=None, is_complex=False)
Lists aggregate algos.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the aggregate algo list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_aggregatetuple(filters=None, is_complex=False)
Lists aggregatetuples.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the aggregatetuple list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_algo(filters=None, is_complex=False)
Lists algos.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the algo list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_composite_algo(filters=None, is_complex=False)
Lists composite algos.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the composite algo list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_composite_traintuple(filters=None, is_complex=False)
Lists composite traintuples.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the composite traintuple
    list. Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_compute_plan(filters=None, is_complex=False)
Lists compute plans.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the compute plan list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_data_sample(filters=None, is_complex=False)
Lists data samples.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the data sample list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_dataset(filters=None, is_complex=False)
Lists datasets.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the dataset list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_node(\*args, \*\*kwargs)
Lists nodes.


* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_objective(filters=None, is_complex=False)
Lists objectives.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the objective list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_testtuple(filters=None, is_complex=False)
Lists testtuple


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the testtuple list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### list_traintuple(filters=None, is_complex=False)
Lists traintuples.


* **Parameters**

    **filters** (*list**[**str**]**, **optional*) – List of filters to apply to the traintuple list.
    Defaults to None.

    A single filter is a string that can be either:
    \* ‘OR’
    \* ‘<asset_type>:<asset_field>:<value>’




* **Raises**

    **InvalidRequest** – 



* **Returns**

    The list of requested assets.



* **Return type**

    list[dict]



#### login()
Logs into a substra node.

Uses the current profile’s login and password to get a token from the profile’s node. The
token will then be used to authenticate all calls made to the node.


* **Returns**

    The authentication token



* **Return type**

    string



#### set_profile(profile_name)
Sets current profile from profile name.

If profile_name has not been defined through the add_profile method, it is loaded
from the config file.


* **Parameters**

    **profile_name** (*str*) – The name of the profile to set as current profile



* **Returns**

    The new current profile



* **Return type**

    dict



#### set_user()
Loads authentication token from user file.

If a token is found in the user file, it will be used to authenticate all calls made to the
node.


#### update_compute_plan(compute_plan_id, data)
Updates an existing compute plan asset.

As specified in the data dict structure, output trunk models of composite
traintuples cannot be made public.


* **Parameters**

    
    * **compute_plan_id** (*str*) – The compute plan ID of the asset to update.


    * **data** (*dict*) – Must have the following schema

    {

        “traintuples”: list[{

            “traintuple_id”: str,
            “algo_key”: str,
            “data_manager_key”: str,
            “train_data_sample_keys”: list[str],
            “in_models_ids”: list[str],
            “tag”: str,

        }],
        “composite_traintuples”: list[{

        > ”composite_traintuple_id”: str,
        > “algo_key”: str,
        > “data_manager_key”: str,
        > “train_data_sample_keys”: list[str],
        > “in_head_model_id”: str,
        > “in_trunk_model_id”: str,
        > “out_trunk_model_permissions”: {

        > > ”authorized_ids”: list[str],

        > },
        > “tag”: str,

        }]
        “aggregatetuples”: list[{

        > ”aggregatetuple_id”: str,
        > “algo_key”: str,
        > “worker”: str,
        > “in_models_ids”: list[str],
        > “tag”: str,

        }],
        “testtuples”: list[{

        > ”objective_key”: str,
        > “data_manager_key”: str,
        > “test_data_sample_keys”: list[str],
        > “traintuple_id”: str,
        > “tag”: str,

        }],

    }




* **Returns**

    The updated asset.



* **Return type**

    dict



#### update_dataset(dataset_key, data)
Updates a dataset.

This only updates the link between a given dataset and objectives.


* **Parameters**

    
    * **dataset_key** (*str*) – The dataset key of the asset to update.


    * **data** (*dict*) – Must have the following schema

    {

        “objective_key”: str

    }




* **Returns**

    The updated asset.



* **Return type**

    dict
