import pytest

from parser import PatchbookParser


@pytest.mark.parametrize("patchname", ["patch1", "patch2", "syncpll"])
class TestExamplePatch1:
    maxDiff = None

    def test_parsefile_raise_no_errors(self, patchname):
        p = PatchbookParser()
        p.parse_file(f"../Examples/{patchname}.txt")

    def test_modules_prints_all_output(self, capsys, patchname):
        with capsys.disabled():
            p = PatchbookParser()
            p.parse_file(f"../Examples/{patchname}.txt")

        p.detail_module(show_all=True)
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_modules.txt").read()
        assert captured.out == expected

    def test_printDict_output(self, capsys, patchname):
        with capsys.disabled():
            p = PatchbookParser()
            p.parse_file(f"../Examples/{patchname}.txt")

        p.print_dict()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_print.txt").read()
        assert captured.out == expected

    def test_exportJSON_output(self, capsys, patchname):
        with capsys.disabled():
            p = PatchbookParser()
            p.parse_file(f"../Examples/{patchname}.txt")

        p.export_json()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_export.txt").read()
        assert captured.out == expected

    def test_printConnections_output(self, capsys, patchname):
        with capsys.disabled():
            p = PatchbookParser()
            p.parse_file(f"../Examples/{patchname}.txt")

        p.print_connections()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_connections.txt").read()
        assert captured.out == expected

    def test_graphviz_output(self, capsys, patchname):
        with capsys.disabled():
            p = PatchbookParser()
            p.parse_file(f"../Examples/{patchname}.txt")

        p.graphviz()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_graph.txt").read()
        assert captured.out == expected
