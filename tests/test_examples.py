from patchbook import detailModule, exportJSON, graphviz, parseFile, printConnections, printDict


class TestExamplePatch1:
    fn = "../Examples/patch1.txt"
    maxDiff = None

    def test_parsefile_raise_no_errors(self):
        parseFile(self.fn)

    def test_modules_prints_all_output(self, capsys):
        with capsys.disabled():
            parseFile(self.fn)

        detailModule(all=True)
        captured = capsys.readouterr()
        expected = open("sample_output/patch1_modules.txt").read()
        assert expected == captured.out

    def test_printDict_output(self, capsys):
        with capsys.disabled():
            parseFile(self.fn)

        printDict()
        captured = capsys.readouterr()
        expected = open("sample_output/patch1_print.txt").read()
        assert expected == captured.out

    def test_exportJSON_output(self, capsys):
        with capsys.disabled():
            parseFile(self.fn)

        exportJSON()
        captured = capsys.readouterr()
        expected = open("sample_output/patch1_export.txt").read()
        assert expected == captured.out

    def test_printConnections_output(self, capsys):
        with capsys.disabled():
            parseFile(self.fn)

        printConnections()
        captured = capsys.readouterr()
        expected = open("sample_output/patch1_connections.txt").read()
        assert expected == captured.out

    def test_graphviz_output(self, capsys):
        with capsys.disabled():
            parseFile(self.fn)

        graphviz()
        captured = capsys.readouterr()
        expected = open("sample_output/patch1_graph.txt").read()
        assert expected == captured.out


class TestExamplePatch2:
    def test_parsefile_raise_no_errors(self):
        fn = "../Examples/patch2.txt"
        parseFile(fn)


class TestExampleSyncPII:
    def test_parsefile_raise_no_errors(self):
        fn = "../Examples/syncpii.txt"
        parseFile(fn)
