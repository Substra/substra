from substra.sdk import exceptions
from substra.sdk import graph
from substra.sdk import schemas


def _insert_into_graph(tuple_graph, tuple_id, in_model_ids):
    if tuple_id in tuple_graph:
        raise exceptions.InvalidRequest("Two tuples cannot have the same id.", 400)
    in_model_ids = in_model_ids or list()
    tuple_graph[tuple_id] = in_model_ids


def get_dependency_graph(spec: schemas._BaseComputePlanSpec):
    """Get the tuple dependency graph and, for each type of tuple, a mapping table id/tuple."""
    tuple_graph = {}
    tuples = {}

    if spec.traintuples:
        for traintuple in spec.traintuples:
            _insert_into_graph(
                tuple_graph=tuple_graph,
                tuple_id=traintuple.traintuple_id,
                in_model_ids=traintuple.in_models_ids,
            )
            tuples[traintuple.traintuple_id] = schemas.TraintupleSpec.from_compute_plan(
                compute_plan_key=spec.key,
                rank=None,
                spec=traintuple,
            )

    if spec.aggregatetuples:
        for aggregatetuple in spec.aggregatetuples:
            _insert_into_graph(
                tuple_graph=tuple_graph,
                tuple_id=aggregatetuple.aggregatetuple_id,
                in_model_ids=aggregatetuple.in_models_ids,
            )
            tuples[aggregatetuple.aggregatetuple_id] = schemas.AggregatetupleSpec.from_compute_plan(
                compute_plan_key=spec.key,
                rank=None,
                spec=aggregatetuple,
            )

    if spec.composite_traintuples:
        for compositetuple in spec.composite_traintuples:
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
            tuples[compositetuple.composite_traintuple_id] = schemas.CompositeTraintupleSpec.from_compute_plan(
                compute_plan_key=spec.key,
                rank=None,
                spec=compositetuple,
            )
    if spec.predicttuples:
        for predicttuple in spec.predicttuples:
            _insert_into_graph(
                tuple_graph=tuple_graph,
                tuple_id=predicttuple.predicttuple_id,
                in_model_ids=[predicttuple.traintuple_id],
            )
            tuples[predicttuple.predicttuple_id] = schemas.PredicttupleSpec.from_compute_plan(
                compute_plan_key=spec.key,
                rank=None,
                spec=predicttuple,
            )
    return tuple_graph, tuples


def get_tuples(spec):
    """Returns compute plan tuples sorted by dependencies."""

    # Create the dependency graph and get the dict of tuples by id
    tuple_graph, tuples = get_dependency_graph(spec)

    already_created_ids = set()
    # Here we get the pre-existing tuples and assign them the minimal rank
    for dependencies in tuple_graph.values():
        for dependency_id in dependencies:
            if dependency_id not in tuple_graph:
                already_created_ids.add(dependency_id)

    # Compute the relative ranks of the new tuples (relatively to each other, these
    # are not their actual ranks in the compute plan)
    id_ranks = graph.compute_ranks(node_graph=tuple_graph, node_to_ignore=already_created_ids)

    # Add the testtuples to 'visited' to take them into account in the batches
    if spec.testtuples:
        for testtuple in spec.testtuples:
            tuple_spec = schemas.TesttupleSpec.from_compute_plan(
                compute_plan_key=spec.key,
                spec=testtuple,
            )
            id_ranks[tuple_spec.key] = id_ranks.get(testtuple.predicttuple_id, -1) + 1
            tuples[tuple_spec.key] = tuple_spec

    # Sort the tuples by rank
    sorted_by_rank = sorted(id_ranks.items(), key=lambda item: item[1])

    return [tuples[tuple_id] for tuple_id, _ in sorted_by_rank]
