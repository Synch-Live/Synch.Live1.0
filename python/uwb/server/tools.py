from types import SimpleNamespace

def parse(d):
    """
    Convert nested dict to nested namespace
    """
    x = SimpleNamespace()
    _ = [setattr(x, k, parse(v)) if isinstance(v, dict) else setattr(x, k, v)
            for k, v in d.items() ]
    return x