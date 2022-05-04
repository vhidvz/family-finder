import re


def standardization(aliases: list, kwargs: dict) -> dict:
    """
    This method engaged after the preprocessing functions and return the correct key for each value based on API documentation.

    Parameter:
        kwargs (dict): query string values.

    Return:
        dict: correct and standardized (key, value) pairs.
    """
    for alias, key in aliases:
        if alias in kwargs.keys():
            kwargs[key] = kwargs.pop(alias)
    return kwargs


def kwargparse(args: list, spliter='=') -> dict:
    args = args[1:]
    args = dict([tuple(raw.replace("'", '').replace("+", ' ').split(spliter))
                 for raw in args if spliter in raw and re.match(r"\w+[=][&'|]?[\w\s]+[']?", raw)])
    return args


def kwargcheck(kwargs: dict, support: str,
               arguments: dict) -> dict:
    flag = True
    hasOptArg = False
    newkwargs = {}
    support = support.split('|')
    for key, value in kwargs.items():
        if key in support:
            _tsearch = re.search(arguments[key], value)
            if _tsearch:
                _start, _end = _tsearch.span()
                newkwargs.update({key: value[_start:_end]})
                continue
        else:
            _supp = support[-1]
            if _supp.startswith('[') and flag:
                __supp = _supp if not _supp.endswith('*') else _supp[:-1]
                _tsearch = re.search(arguments[__supp], value)
                if _tsearch:
                    _start, _end = _tsearch.span()
                    newkwargs.update({key: value[_start:_end]})
                if not _supp.endswith('*'):
                    flag = False
                hasOptArg = True
    return newkwargs, hasOptArg


def argtypecheck(kwargs: dict, hasOptArg: bool,
                 support: str, argtype: str) -> bool:
    if kwargs == {}:
        return False
    argtype = 'AllOf' if 'AllOf'.lower() in argtype.lower() else 'OneOf'
    support = support if not hasOptArg else support.split('|')[:-1]
    if argtype.lower() == 'OneOf'.lower():
        if len(kwargs) >= 1:
            return True
    elif argtype.lower() == 'AllOf'.lower():
        if (len(kwargs) >= len(support) and hasOptArg)\
                or (len(kwargs) == len(support) and not hasOptArg):
            return True
    return False


def kwpreprocessing(info: dict, kwargs: dict) -> dict:
    for k in info.keys():
        if 'arguments' in k:
            arguments = (k.split(':')[1], info[k])
    kwargs, hasOptArg = kwargcheck(kwargs, info['support'], arguments[1])
    assert argtypecheck(kwargs, hasOptArg, info['support'], arguments[0])
    return kwargs
