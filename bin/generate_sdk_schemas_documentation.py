import argparse
import inspect
from pathlib import Path
import sys
import pydantic
import warnings

from substra.sdk import schemas, models

local_dir = Path(__file__).parent

schemas_list = [
    schemas.DataSampleSpec,
    schemas.DatasetSpec,
    schemas.ObjectiveSpec,
    schemas.TesttupleSpec,
    schemas.TraintupleSpec,
    schemas.AggregatetupleSpec,
    schemas.CompositeTraintupleSpec,
    schemas.ComputePlanSpec,
    schemas.UpdateComputePlanSpec,
    schemas.ComputePlanTesttupleSpec,
    schemas.ComputePlanAggregatetupleSpec,
    schemas.ComputePlanCompositeTraintupleSpec,
    schemas.ComputePlanTraintupleSpec,
    schemas.Permissions,
    schemas.PrivatePermissions,
]

models_list = [
    models.DataSample,
    models.Dataset,
    models.Objective,
    models.Testtuple,
    models.Traintuple,
    models.Aggregatetuple,
    models.CompositeTraintuple,
    models.Algo,
    models.ComputePlan,
    models.Node,
    models.Permissions,
    models.InModel,
    models.OutModel,
    models._File,
    models._Metric,
]


def _get_field_description(fields):
    desc = [f"{field.name}: {field._type_display()}" for _, field in fields.items()]
    return desc


def generate_help(fh, models: bool):

    if models:
        asset_list = models_list
        title = "Models"
    else:
        asset_list = schemas_list
        title = "Schemas"

    fh.write("# Summary\n\n")

    def _create_anchor(schema):
        return "#{}".format(schema.__name__)

    for asset in asset_list:
        anchor = _create_anchor(asset)
        fh.write(f"- [{asset.__name__}]({anchor})\n")

    fh.write("\n\n")
    fh.write(f"# {title}\n\n")

    for asset in asset_list:
        anchor = _create_anchor(asset)

        fh.write(f"## {asset.__name__}\n")
        # Write the docstring
        fh.write(f"{inspect.getdoc(asset)}\n")
        # List the fields and their types
        description = _get_field_description(asset.__fields__)
        fh.write("```python\n")
        fh.write("- " + "\n- ".join(description))
        fh.write("\n```")
        fh.write("\n\n")


def write_help(path, models: bool):
    with path.open('w') as fh:
        generate_help(fh, models)


if __name__ == '__main__':

    if pydantic.VERSION != '1.8.2':
        warnings.warn("The documentation should be generated with this exact version of pydantic or \
            there might be mismatches with the CI.")

    doc_dir = local_dir.parent / "references"
    default_path = doc_dir / "sdk_schemas.md"

    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, default=str(default_path.resolve()),
                        required=False)
    parser.add_argument('--models', action='store_true', help='Generate the doc for the models.\
        Default: generate for the schemas')

    args = parser.parse_args(sys.argv[1:])
    write_help(Path(args.output_path), models=args.models)
