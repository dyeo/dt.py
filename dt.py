from dtdecoder import DTDecoder

def loads(s, cls=None, loose_arrays=False):
    """
    Loads a string containing a datatag file into python objects representing the dataset.
    Returns a dict containing the dataset, as key value pairs corresponding to their representation in the datatag file.
    * cls is a class that inherits DTDecoder. Default is None (loads uses the default decoder).
    * loose_arrays allows arrays to contain different types if true. Default is false.
    """
    cls = DTDecoder if not cls else cls
    prs = cls(None, loose_arrays)
    return prs.decode(s)

def load(fp, cls=None, loose_arrays=False):
    """
    Loads a python filestream containing a datatag file into python objects representing the dataset.
    Returns a dict containing the dataset, as key value pairs corresponding to their representation in the datatag file.
    * cls is a class that inherits DTDecoder. Default is None (uses the default decoder).
    * loose_arrays allows arrays to contain different types if true. Default is false.
    """
    return loads(fp.dump(), cls, loose_arrays)

def loadso(s, out_cls, cls=None, loose_arrays=False):
    """
    Loads a string containing a datatag file into python objects representing the dataset.
    Returns a object containing the dataset, where the class corresponds to the datatag's structure.
    * out_cls is a class corresponding to the class to decode to. The class must have a default constructor.
    * cls is a class that inherits DTDecoder. Default is None (uses the default decoder).
    * loose_arrays allows arrays to contain different types if true. Default is false.
    """
    cls = DTDecoder if not cls else cls
    prs = cls(out_cls, loose_arrays)
    return prs.decode(s)

def loado(fp, out_cls, cls=None, loose_arrays=False):
    """
    Loads a python filestream containing a datatag file into python objects representing the dataset.
    Returns a object containing the dataset, where the class corresponds to the datatag's structure.
    * out_cls is a class corresponding to the class to decode to. The class must have a default constructor.
    * cls is a class that inherits DTDecoder. Default is None (uses the default decoder).
    * loose_arrays allows arrays to contain different types if true. Default is false.
    """
    return loadso(fp.dump(), out_cls, cls, loose_arrays)
