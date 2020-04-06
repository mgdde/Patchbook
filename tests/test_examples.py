import pytest

import patchbook
from patchbook import _PARSER_VERSION, detailModule, exportJSON, graphviz, parseFile, printConnections, printDict


@pytest.mark.parametrize("patchname", ["patch1", "patch2", "syncpll"])
class TestExamplePatch1:
    maxDiff = None

    def teardown_method(self, method):
        """
        Currently the code isn't idempotent so we need to do some cleanup after every test run.

        Hopefully this teardown code can be removed soon
        """
        print("Resetting globals...")
        patchbook.mainDict = {
            "info": {"patchbook_version": _PARSER_VERSION},
            "modules": {},
            "comments": []
        }
        patchbook.lastModuleProcessed = ""
        patchbook.lastVoiceProcessed = ""
        patchbook.quiet = False
        patchbook.connectionID = 0
        patchbook.direction = ""

    def test_parsefile_raise_no_errors(self, patchname):
        parseFile(f"../Examples/{patchname}.txt")

    def test_modules_prints_all_output(self, capsys, patchname):
        with capsys.disabled():
            parseFile(f"../Examples/{patchname}.txt")

        detailModule(all=True)
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_modules.txt").read()
        assert expected == captured.out

    def test_printDict_output(self, capsys, patchname):
        with capsys.disabled():
            parseFile(f"../Examples/{patchname}.txt")

        printDict()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_print.txt").read()
        assert expected == captured.out

    def test_exportJSON_output(self, capsys, patchname):
        with capsys.disabled():
            parseFile(f"../Examples/{patchname}.txt")

        exportJSON()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_export.txt").read()
        assert expected == captured.out

    def test_printConnections_output(self, capsys, patchname):
        with capsys.disabled():
            parseFile(f"../Examples/{patchname}.txt")

        printConnections()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_connections.txt").read()
        assert expected == captured.out

    def test_graphviz_output(self, capsys, patchname):
        with capsys.disabled():
            parseFile(f"../Examples/{patchname}.txt")

        graphviz()
        captured = capsys.readouterr()
        expected = open(f"sample_output/{patchname}_graph.txt").read()
        assert expected == captured.out
