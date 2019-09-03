from dtdecoder import DTDecoder

def loads(s, cls=None):
    """
    Loads a string containing a datatag file into python objects representing the dataset.
    Returns a dict containing the dataset, as key value pairs corresponding to their representation in the datatag file.
    """
    cls = DTDecoder if not cls else cls
    prs = cls(False)
    return prs.decode(s)

def load(fp, cls=None):
    """
    Loads a python filestream containing a datatag file into python objects representing the dataset.
    Returns a dict containing the dataset, as key value pairs corresponding to their representation in the datatag file.
    """
    return loads(fp.dump())

def loadso(fp, cls=None):
    """
    Loads a string containing a datatag file into python objects representing the dataset.
    Returns a object containing the dataset, where the class corresponds to the datatag's structure.
    """
    cls = DTDecoder if not cls else cls
    prs = cls(True)
    return prs.decode(s)

def loado(fp, cls=None):
    """
    Loads a python filestream containing a datatag file into python objects representing the dataset.
    Returns a object containing the dataset, where the class corresponds to the datatag's structure.
    """
    return loadso(fp.dump())
