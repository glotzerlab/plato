import os

def get_fname(fname):
    base = os.environ.get('PLATO_TEST_ARTIFACT_DIR', '/tmp')
    return os.path.join(base, fname)
