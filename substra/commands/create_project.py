import json
import os
import shutil
from .base import Base

base_assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'create_project_assets')


def with_absolute_paths(data, to_update, target_path):
    def abspath(path): return os.path.abspath(os.path.join(target_path, path))

    for key in data.keys():
        if key in to_update.keys():
            # update path
            for k in to_update[key]:
                if isinstance(data[key][k], list):
                    data[key][k] = [abspath(path) for path in data[key][k]]
                else:
                    data[key][k] = abspath(data[key][k])
    return data


def update_paths_in_json(target_path, filename, to_update):
    file_path = os.path.join(target_path, filename)
    with open(file_path, 'r') as f:
        data = json.load(f)
    data = with_absolute_paths(data, to_update, target_path)
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
                update_paths_in_json(os.path.join(target_path, 'objective'), 'objective.json', {
                    'objective': ['description', 'metrics'],
                    'data_manager': ['description', 'data_opener'],
                    'data_samples': ['paths'],
                })
                update_paths_in_json(os.path.join(target_path, 'dataset'), 'dataset.json', {
                    'data_manager': ['description', 'data_opener'],
                    'data_samples': ['paths'],
                })
            print(f'New project created in {target_path}')
