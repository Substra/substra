import os
import shutil
from .base import Base

assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'create-project-assets')


class CreateProject(Base):
    """BulkUpdate asset"""

    def run(self):
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
