import os
import shutil
from .base import Base

base_assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'create_project_assets')


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
            print(f'New project created in {target_path}')
