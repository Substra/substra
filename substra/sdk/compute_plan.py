from substra.sdk import exceptions
from substra.sdk import graph
from substra.sdk import schemas


def _insert_into_graph(task_graph, task_id, in_model_ids):
    if task_id in task_graph:
        raise exceptions.InvalidRequest("Two tasks cannot have the same id.", 400)
    task_graph[task_id] = in_model_ids


def get_dependency_graph(spec: schemas._BaseComputePlanSpec):
    """Get the task dependency graph and, for each type of task, a mapping table id/task."""
    task_graph = {}
    tasks = {}

    if spec.tasks:
        for task in spec.tasks:
            _insert_into_graph(
                task_graph=task_graph,
                task_id=task.task_id,
                in_model_ids=[
                    input_ref.parent_task_key for input_ref in (task.inputs or []) if input_ref.parent_task_key
                ],
            )
            tasks[task.task_id] = schemas.TaskSpec.from_compute_plan(
                compute_plan_key=spec.key,
                rank=None,
                spec=task,
            )
    return task_graph, tasks


def get_tasks(spec):
    """Returns compute plan tasks sorted by dependencies."""

    # Create the dependency graph and get the dict of tasks by id
    task_graph, tasks = get_dependency_graph(spec)

    already_created_ids = set()
    # Here we get the pre-existing tasks and assign them the minimal rank
    for dependencies in task_graph.values():
        for dependency_id in dependencies:
            if dependency_id not in task_graph:
                already_created_ids.add(dependency_id)

    # Compute the relative ranks of the new tasks (relatively to each other, these
    # are not their actual ranks in the compute plan)
    id_ranks = graph.compute_ranks(node_graph=task_graph, node_to_ignore=already_created_ids)

    # Sort the tasks by rank
    sorted_by_rank = sorted(id_ranks.items(), key=lambda item: item[1])

    return [tasks[task_id] for task_id, _ in sorted_by_rank]
