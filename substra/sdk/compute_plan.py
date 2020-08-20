# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from copy import deepcopy
import math
import typing

from substra.sdk import schemas, graph, exceptions


def _insert_into_graph(tuple_graph, tuple_id, in_model_ids):
    if tuple_id in tuple_graph:
        raise exceptions.InvalidRequest("Two tuples cannot have the same id.", 400)
    in_model_ids = in_model_ids or list()
    tuple_graph[tuple_id] = in_model_ids


def get_dependency_graph(spec: schemas._BaseComputePlanSpec):
    """Get the tuple dependency graph and, for each type of tuple, a mapping table id/tuple.
    """
    tuple_graph = dict()
    traintuples_by_ids = dict()
    if spec.traintuples:
        for traintuple in spec.traintuples:
            _insert_into_graph(
                tuple_graph=tuple_graph,
                tuple_id=traintuple.traintuple_id,
                in_model_ids=traintuple.in_models_ids,
            )
            traintuples_by_ids[traintuple.traintuple_id] = traintuple

    aggregatetuples_by_ids = dict()
    if spec.aggregatetuples:
        for aggregatetuple in spec.aggregatetuples:
            _insert_into_graph(
                tuple_graph=tuple_graph,
                tuple_id=aggregatetuple.aggregatetuple_id,
                in_model_ids=aggregatetuple.in_models_ids,
            )
            aggregatetuples_by_ids[aggregatetuple.aggregatetuple_id] = aggregatetuple

    composite_traintuples_by_ids = dict()
    if spec.composite_traintuples:
        for compositetuple in spec.composite_traintuples:
            assert not compositetuple.out_trunk_model_permissions.public
            _insert_into_graph(
                tuple_graph=tuple_graph,
                tuple_id=compositetuple.composite_traintuple_id,
                in_model_ids=[
                    model
                    for model in [
                        compositetuple.in_head_model_id,
                        compositetuple.in_trunk_model_id,
                    ]
                    if model
                ],
            )
            composite_traintuples_by_ids[compositetuple.composite_traintuple_id] = compositetuple

    return tuple_graph, traintuples_by_ids, aggregatetuples_by_ids, composite_traintuples_by_ids


def filter_tuples_in_list(
    tuple_graph: typing.Dict[str, typing.List[str]],
    traintuples_by_ids: typing.Dict[str, schemas.ComputePlanTraintupleSpec],
    aggregatetuples_by_ids: typing.Dict[str, schemas.ComputePlanAggregatetupleSpec],
    composite_traintuples_by_ids: typing.Dict[str, schemas.ComputePlanCompositeTraintupleSpec],
    testtuples_by_ids: typing.Dict[str, schemas.ComputePlanTesttupleSpec],
):
    """Return the tuple lists with only the elements which are in the tuple graph.
    """
    filtered_traintuples = list()
    filtered_aggregatetuples = list()
    filtered_composite_traintuples = list()
    filtered_testtuples = list()
    for elem_id, _ in tuple_graph:
        if elem_id in traintuples_by_ids:
            filtered_traintuples.append(traintuples_by_ids[elem_id])
        elif elem_id in aggregatetuples_by_ids:
            filtered_aggregatetuples.append(aggregatetuples_by_ids[elem_id])
        elif elem_id in composite_traintuples_by_ids:
            filtered_composite_traintuples.append(composite_traintuples_by_ids[elem_id])
        elif elem_id in testtuples_by_ids:
            filtered_testtuples.append(testtuples_by_ids[elem_id])

    return (
        filtered_traintuples,
        filtered_aggregatetuples,
        filtered_composite_traintuples,
        filtered_testtuples,
    )


def auto_batching(spec, is_creation: bool = True, batch_size: int = 20):
    """Auto batching of the compute plan tuples
    """

    # Create the dependency graph and get the dict
    # of tuples by id
    (
        tuple_graph,
        traintuples_by_ids,
        aggregatetuples_by_ids,
        composite_traintuples_by_ids,
    ) = get_dependency_graph(spec)

    already_created_ids = set()
    if not is_creation:
        # Here we get the pre-existing tuples and assign them the minimal rank
        for dependencies in tuple_graph.values():
            for dependency_id in dependencies:
                if dependency_id not in tuple_graph:
                    already_created_ids.add(dependency_id)

    # Compute the relative ranks of the new tuples (relatively to each other, these
    # are not their actual ranks in the compute plan)
    id_ranks = graph.compute_ranks(
        node_graph=tuple_graph, node_to_ignore=already_created_ids
    )

    # Add the testtuples to 'visited' to take them into account in the batches
    testtuples_by_ids = dict()
    if spec.testtuples:
        for testtuple in spec.testtuples:
            # Rank 0 if testtuple.traintuple_id is in the nodes to ignore
            if testtuple.traintuple_id not in id_ranks:
                id_ranks["test_" + testtuple.traintuple_id] = 0
            else:
                id_ranks["test_" + testtuple.traintuple_id] = (
                    id_ranks[testtuple.traintuple_id] + 1
                )
            testtuples_by_ids["test_" + testtuple.traintuple_id] = testtuple

    # Sort the tuples by rank
    sorted_by_rank = sorted(id_ranks.items(), key=lambda item: item[1])

    # Create / update by batch
    for i in range(math.ceil(len(sorted_by_rank) / batch_size)):
        start = i * batch_size
        end = min(len(sorted_by_rank), (i + 1) * batch_size)

        if i == 0 and is_creation:
            # Compute plan does not exist (ie first batch of a creation):
            # we create it
            tmp_spec = deepcopy(spec)
            (
                tmp_spec.traintuples,
                tmp_spec.aggregatetuples,
                tmp_spec.composite_traintuples,
                tmp_spec.testtuples,
            ) = filter_tuples_in_list(
                sorted_by_rank[start:end],
                traintuples_by_ids,
                aggregatetuples_by_ids,
                composite_traintuples_by_ids,
                testtuples_by_ids,
            )
            yield tmp_spec
        else:
            # Compute plan exists: we update it
            tmp_spec = schemas.UpdateComputePlanSpec(
                traintuples=list(),
                composite_traintuples=list(),
                aggregatetuples=list(),
                testtuples=list(),
            )
            (
                tmp_spec.traintuples,
                tmp_spec.aggregatetuples,
                tmp_spec.composite_traintuples,
                tmp_spec.testtuples,
            ) = filter_tuples_in_list(
                sorted_by_rank[start:end],
                traintuples_by_ids,
                aggregatetuples_by_ids,
                composite_traintuples_by_ids,
                testtuples_by_ids,
            )
            yield tmp_spec
