import os
import stat
import zipfile


class ZipFile(zipfile.ZipFile):
    """Override Zipfile to ensure unix file permissions are preserved.

    This is due to a python bug:
    https://bugs.python.org/issue15795

    Workaround from:
    https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries
    """

    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        ret_val = self._extract_member(member, path, pwd)
        attr = member.external_attr >> 16
        os.chmod(ret_val, attr)
        return ret_val

    def extractall(self, path=None, members=None, pwd=None):
        self._sanity_check()
        super().extractall(path, members, pwd)

    def _sanity_check(self):
        """Check that the archive does not attempt to traverse path.

        This is inspired by TarSafe: https://github.com/beatsbears/tarsafe
        """
        for zipinfo in self.infolist():
            if self._is_traversal_attempt(zipinfo):
                raise Exception(f"Attempted directory traversal for member: {zipinfo.filename}")
            if self._is_symlink(zipinfo):
                raise Exception(f"Unsupported symlink for member: {zipinfo.filename}")

    def _is_traversal_attempt(self, zipinfo: zipfile.ZipInfo) -> bool:
        base_directory = os.getcwd()
        zipfile_path = os.path.abspath(os.path.join(base_directory, zipinfo.filename))
        if not zipfile_path.startswith(base_directory):
            return True
        return False

    def _is_symlink(self, zipinfo: zipfile.ZipInfo) -> bool:
        return zipinfo.external_attr & stat.S_IFLNK << 16 == stat.S_IFLNK << 16
