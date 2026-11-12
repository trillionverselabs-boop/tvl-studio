import json

import pytest

from example_plugin import tools
from example_plugin.paths import data_root


def test_the_tool_is_registered_and_echoes():
    class Ctx:
        def __init__(self):
            self.handlers = {}
            self.names = []

        def register_tool(self, name, toolset, schema, handler):
            self.names.append(name)
            self.handlers[name] = handler

    c = Ctx()
    tools.register_tools(c)
    assert c.names == ["example_echo"]
    out = json.loads(c.handlers["example_echo"]({"text": "hi"}))
    assert out["echo"] == "hi"


def test_a_malformed_run_id_is_a_json_error_not_a_crash():
    class Ctx:
        def __init__(self):
            self.handlers = {}

        def register_tool(self, name, toolset, schema, handler):
            self.handlers[name] = handler

    c = Ctx()
    tools.register_tools(c)
    out = json.loads(c.handlers["example_echo"]({"text": "hi", "run_id": "../evil"}))
    assert "error" in out


@pytest.mark.parametrize("bad", ["../../escape", "/etc", ".."])
def test_out_dir_cannot_escape_the_data_dir(bad):
    with pytest.raises(ValueError):
        tools.resolve_out_dir(bad)


def test_out_dir_inside_the_data_dir_is_allowed():
    p = tools.resolve_out_dir("records")
    assert str(p).startswith(str(data_root().resolve()))
