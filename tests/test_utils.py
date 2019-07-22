import os
import zipfile

from substra.sdk import utils


def _unzip(fp, destination):
    with zipfile.ZipFile(fp, 'r') as zipf:
        zipf.extractall(destination)


def test_zip_folder(tmp_path):
    # initialise dir to zip
    dir_to_zip = tmp_path / "dir"
    dir_to_zip.mkdir()

    file_items = [
        ("name0.txt", "content0"),
        ("dir1/name1.txt", "content1"),
        ("dir2/name2.txt", "content2"),
    ]

    for name, content in file_items:
        path = dir_to_zip / name
        path.parents[0].mkdir(exist_ok=True)
        path.write_text(content)

    for name, _ in file_items:
        path = dir_to_zip / name
        assert os.path.exists(str(path))

    # zip dir
    fp = utils.zip_folder_in_memory(str(dir_to_zip))
    assert fp

    # unzip dir
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()
    _unzip(fp, str(destination_dir))
    for name, content in file_items:
        path = destination_dir / name
        assert os.path.exists(str(path))
        assert path.read_text() == content
