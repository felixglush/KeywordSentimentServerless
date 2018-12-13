import tarfile
from io import BytesIO


def read_targz_s3_output(targz_bytes):
    bytestream = BytesIO(targz_bytes)
    with tarfile.open(fileobj=bytestream) as targz:
        for member in targz.getmembers():
            f = targz.extractfile(member)
            content = f.read().decode("utf-8")
            try:
                splitlist = content.split("\n")
                return splitlist
            except ValueError:
                return None
