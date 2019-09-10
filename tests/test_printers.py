import pytest

from substra.cli import printers


@pytest.mark.parametrize('obj,path,res', [
    ({}, 'a', None),
    ({}, 'a.b', None),
    ({'a': None}, 'a.b', None),
    ({'a': 'a'}, 'a', 'a'),
    ({'a': {'b': 'b'}}, 'a.b', 'b'),
])
def test_find_dict_composite_key_value(obj, path, res):
    assert printers.find_dict_composite_key_value(obj, path) == res


def test_find_dict_composite_key_value_fails():
    with pytest.raises(AttributeError):
        printers.find_dict_composite_key_value({'a': 'b'}, 'a.b')


@pytest.mark.parametrize('asset,output_format,printer_cls', [
    ('algo', 'pretty', printers.AssetPrinter),
    ('algo', 'json', printers.JsonPrinter),
    ('algo', 'yaml', printers.YamlPrinter),
    ('foo', 'pretty', printers.JsonPrinter),
    ('foo', 'json', printers.JsonPrinter),
    ('foo', 'yaml', printers.YamlPrinter),
])
def test_get_asset_printer(asset, output_format, printer_cls):
    assert isinstance(printers.get_asset_printer(asset, output_format), printer_cls)


@pytest.mark.parametrize('output_format,printer_cls', [
    ('json', printers.JsonPrinter),
    ('yaml', printers.YamlPrinter),
    ('pretty', printers.LeaderBoardPrinter),
    ('foo', printers.JsonPrinter),
])
def test_get_leaderboard_printer(output_format, printer_cls):
    assert isinstance(printers.get_leaderboard_printer(output_format), printer_cls)
