import argparse
import inspect
from pathlib import Path
import sys
import yaml

from substra.sdk import schemas

local_dir = Path(__file__).parent

schemas_list = [
    schemas.DataSampleSpec,
    schemas.DatasetSpec,
    schemas.ObjectiveSpec,
    schemas.TesttupleSpec,
    schemas.TraintupleSpec,
    schemas.AggregatetupleSpec,
    schemas.CompositeTraintupleSpec,
    schemas.CompositeAlgoSpec,
    schemas.AggregateAlgoSpec,
    schemas.ComputePlanSpec,
    schemas.UpdateComputePlanSpec,
    schemas.ComputePlanTesttupleSpec,
    schemas.ComputePlanAggregatetupleSpec,
    schemas.ComputePlanCompositeTraintupleSpec,
    schemas.ComputePlanTraintupleSpec,
    schemas.Permissions,
    schemas.PrivatePermissions,
]


def _get_field_description(fields):
    desc = [f"{field.name}: {field._type_display()}" for _, field in fields.items()]
    return desc


def generate_help(fh):
    fh.write("# Summary\n\n")

    def _create_anchor(schema):
        return "#{}".format(schema.__name__)

    for schema in schemas_list:
        anchor = _create_anchor(schema)
        fh.write(f"- [{schema.__name__}]({anchor})\n")

    fh.write("\n\n")
    fh.write("# Schemas\n\n")

    for schema in schemas_list:
        anchor = _create_anchor(schema)

        fh.write(f"## {schema.__name__}\n")
        # Write the docstring
        fh.write(f"{inspect.getdoc(schema)}\n")
        # List the fields and their types
        description = _get_field_description(schema.__fields__)
        desc_text = yaml.dump(description).replace('\'', ''),
        fh.write("```python\n")
        fh.writelines(desc_text)
        fh.write("\n```")
        fh.write("\n\n")


def write_help(path):
    with path.open('w') as fh:
        generate_help(fh)


if __name__ == '__main__':
    doc_dir = local_dir.parent / "references"
    default_path = doc_dir / "sdk_schemas.md"

    parser = argparse.ArgumentParser()
    parser.add_argument('--output-path', type=str, default=str(default_path.resolve()), required=False)

    args = parser.parse_args(sys.argv[1:])
    write_help(Path(args.output_path))
