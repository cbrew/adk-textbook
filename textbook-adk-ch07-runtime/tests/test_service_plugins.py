from adk_service_plugins.service_loader import load_service, register_scheme


def test_python_import_target():
    # define a dummy class inline
    class _X:
        def __init__(self, a="1", b="2"):
            self.a, self.b = a, b

    import types, sys

    mod = types.ModuleType("tmp_mod")
    mod._X = _X
    sys.modules["tmp_mod"] = mod
    inst = load_service("python:tmp_mod:_X?a=10&b=20", "memory")
    assert inst.a == "10" and inst.b == "20"


def test_register_scheme():
    def make_dummy(parsed, qs):
        return ("ok", parsed.scheme, qs.get("x"))

    register_scheme("artifact", "dummy", make_dummy)
    out = load_service("dummy://host/path?x=5", "artifact")
    assert out == ("ok", "dummy", "5")
