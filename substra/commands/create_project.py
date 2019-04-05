import json
import os
import shutil
from .base import Base

base_assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'create_project_assets')


def with_absolute_paths(obj, list_of_keys, target_path):
    def abspath(path): return os.path.abspath(os.path.join(target_path, path))

    for keys in list_of_keys:
        (k1, k2) = keys
        if isinstance(obj[k1][k2], list):
            obj[k1][k2] = [abspath(path) for path in obj[k1][k2]]
        else:
            obj[k1][k2] = abspath(obj[k1][k2])
    return obj


def update_paths_in_json(target_path, filename, list_of_keys):
    file_path = os.path.join(target_path, filename)
    with open(file_path, 'r') as f:
        data = json.load(f)
    data = with_absolute_paths(data, list_of_keys, target_path)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


class CreateProject(Base):
    """Create project from template (starter_kit or isic)"""

    def run(self):
        if self.options['isic']:
            assets_path = os.path.join(base_assets_path, 'isic')
        else:
            assets_path = os.path.join(base_assets_path, 'starter_kit')

        target_path = self.options['<path>']
        target_path = os.path.abspath(target_path)
        try:
            shutil.copytree(assets_path, target_path)
        except FileExistsError:
            print(f'Cannot create project in {target_path}: folder already exists')
        except PermissionError:
            print(f'Cannot create project in {target_path}: permission denied')
        except Exception as e:
            self.handle_exception(e)
        else:
            if self.options['isic']:
                # update paths in JSON files
                update_paths_in_json(os.path.join(target_path, 'objective'), 'objective.json', [
                    ['objective', 'description'],
                    ['objective', 'metrics'],
                    ['data_manager', 'description'],
                    ['data_manager', 'data_opener'],
                    ['data_samples', 'paths']
                ])
                update_paths_in_json(os.path.join(target_path, 'dataset'), 'dataset.json', [
                    ['data_manager', 'description'],
                    ['data_manager', 'data_opener'],
                    ['data_samples', 'paths']
                ])
            print(f'New project created in {target_path}')
