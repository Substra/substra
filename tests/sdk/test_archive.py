import os
import shutil
import tempfile

import pytest
import tarsafe
from substra.sdk.archive import ZipFile, _untar, _unzip


class TestsArchive:
    """Test archive methods"""

    # This zip file was specifically crafted and contains empty files named:
    # foo/bar
    # ../foo/bar
    # ../../foo/bar
    # ../../../foo/bar
    TRAVERSAL_ZIP = os.path.join(os.path.dirname(__file__), 'data', 'traversal.zip')

    # This zip file was specifically crafted and contains:
    # bar
    # foo -> bar (symlink)
    SYMLINK_ZIP = os.path.join(os.path.dirname(__file__), 'data', 'symlink.zip')

    def test_raise_on_path_traversal(self):
        zf = ZipFile(self.TRAVERSAL_ZIP, "r")
        with pytest.raises(Exception) as exc:
            zf.extractall(tempfile.gettempdir())

        assert "Attempted directory traversal" in str(exc.value)

    def test_raise_on_symlink(self):
        zf = ZipFile(self.SYMLINK_ZIP, "r")
        with pytest.raises(Exception) as exc:
            zf.extractall(tempfile.gettempdir())

        assert "Unsupported symlink" in str(exc.value)

    def test_compress_uncompress_tar(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path_testdir = os.path.join(tmpdirname, 'testdir')
            os.makedirs(path_testdir)
            with open(os.path.join(path_testdir, 'testfile.txt'), 'w') as f:
                f.write('testtext')
            path_tarfile = os.path.join(tmpdirname, 'test_archive.tar')
            with tarsafe.open(path_tarfile, 'w:gz') as tar:
                tar.add(path_testdir, arcname=os.path.basename(path_testdir))

            _untar(path_tarfile, os.path.join(tmpdirname, 'test_archive'))

            assert os.listdir(tmpdirname+'/test_archive/testdir') == ['testfile.txt']

    def test_compress_uncompress_zip(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path_testdir = os.path.join(tmpdirname, 'testdir')
            os.makedirs(path_testdir)
            with open(os.path.join(path_testdir, 'testfile.txt'), 'w') as f:
                f.write('testtext')
            shutil.make_archive(os.path.join(tmpdirname, 'test_archive'), 'zip',
                                root_dir=os.path.dirname(path_testdir))
            _unzip(os.path.join(tmpdirname, 'test_archive.zip'),
                   os.path.join(tmpdirname, 'test_archive'))

            assert os.listdir(tmpdirname+'/test_archive/testdir') == ['testfile.txt']
