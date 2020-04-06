import json
import logging
import os
import re
import sys
from typing import List, Optional

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

# Available connection types
CONNECTION_TYPES = {
    "->": "audio",
    ">>": "cv",
    "p>": "pitch",
    "g>": "gate",
    "t>": "trigger",
    "c>": "clock"
}


class PatchbookParser:
    _PARSER_VERSION = "b3"

    def __init__(self, quiet: bool = False):
        self.quiet = quiet
        self.last_module_processed = None
        self.direction = None
        self.last_voice_processed = None
        self.connection_id = 0

        self.modules = {}

        self.comments = []

    def initial_print(self) -> None:
        if not self.quiet:
            print()
            print("██████████████████████████████")
            print("       PATCHBOOK PARSER       ")
            print("   Created by Spektro Audio   ")
            print("██████████████████████████████")
            print()
            print(f"Version {self._PARSER_VERSION}")
            print()

    def get_script_path(self) -> str:
        # Get path to python script
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    def get_file_path(self, filename: str) -> str:
        try:
            # Append script path to the filename
            base_dir = self.get_script_path()
            filepath = os.path.join(base_dir, filename)
            logger.debug(f"File path: {filepath}")
            return filepath
        except IndexError:
            pass

    def parse_file(self, filename: str) -> None:
        # This function reads the txt file and process each line.
        lines = []
        try:
            if not self.quiet:
                print(f"Loading file: {filename}")
            with open(filename) as file:
                for l in file:
                    lines.append(l)
                    self.regex_line(l)
        except TypeError:
            print("ERROR. Please add text file path after the script.")
        except FileNotFoundError:
            print("ERROR. File not found.")
        if not self.quiet:
            print("File successfully processed.")
            print()

    def regex_line(self, line: str) -> None:
        logger.debug(f"Processing: {line}")

        # CHECK FOR COMMENTS
        logger.debug("Checking input for comments...")
        re_filter = re.compile(r"^\/\/\s?(.+)$")  # Regex for "// Comments"
        re_results = re_filter.search(line.strip())
        try:
            comment = re_results.group().replace("//", "").strip()
            logger.debug(f"New comment found: {comment}")
            self.add_comment(comment)
            return
        except AttributeError:
            pass

        # CHECK FOR VOICES
        logger.debug("Checking input for voices...")
        re_filter = re.compile(r"^(.+)\:$")  # Regex for "VOICE 1:"
        re_results = re_filter.search(line)
        try:
            # For some reason the Regex filter was still detecting parameter declarations as voices,
            # so I'm also running the results through an if statement.
            results = re_results.group().replace(":", "")
            if "*" not in results and "-" not in results and "|" not in results:
                logger.debug(f"New voice found: {results.upper()}")
                self.last_voice_processed = results.upper()
                return
        except AttributeError:
            pass

        # CHECK FOR CONNECTIONS
        logger.debug("Checking input for connections...")
        re_filter = re.compile(r"\-\s(.+)[(](.+)[)]\s(\>\>|\-\>|[a-z]\>)\s(.+)[(](.+)[)]\s(\[.+\])?$")
        re_results = re_filter.search(line)
        try:
            results = re_results.groups()
            voice = self.last_voice_processed
            if len(results) == 6:
                logger.debug("New connection found, parsing info...")
                # args = parseArguments(results[5])
                # results = results[:5]
                self.add_connection(results, voice)
                return
        except AttributeError:
            pass

        # CHECK PARAMETERS
        logger.debug("Checking for parameters...")
        # If single-line parameter declaration:
        re_filter = re.compile(r"^\*\s(.+)\:\s?(.+)?$")
        re_results = re_filter.search(line.strip())
        try:
            # Get module name
            results = re_results.groups()
            module = results[0].strip().lower()
            logger.debug(f"New module found: {module}")
            if results[1] != None:
                # If parameters are also declared
                parameters = results[1].split(" | ")
                for p in parameters:
                    p = p.split(" = ")
                    self.add_parameter(module, p[0].strip().lower(), p[1].strip())
                return
            elif results[1] == None:
                logger.debug("No parameters found. Storing module as last_module_processed...")
                self.last_module_processed = module
                return
        except AttributeError:
            pass

        # If multi-line parameter declaration:
        if "|" in line and "=" in line and "*" not in line:
            module = self.last_module_processed.lower()
            logger.debug(f"Using last_module_processed: {module}")
            parameter = line.split(" = ")[0].replace("|", "").strip().lower()
            value = line.split(" = ")[1].strip()
            self.add_parameter(module, parameter, value)
            return

    def parse_arguments(self, args: str) -> dict:
        # This method takes an arguments string like "[color = blue]" and converts it to a dictionary
        args_string = args.replace("[", "").replace("]", "")
        args_array = args_string.split(",")
        args_dict = {}

        logger.debug(f"Parsing arguments: {args}")

        for item in args_array:
            item = item.split("=")
            name = item[0].strip()
            value = item[1].strip()
            args_dict[name] = value
            logger.debug(f"{name} = {value}")

        logger.debug("All arguments processes.")

        return args_dict

    def add_connection(self, a_list: List[str], voice: str = "none") -> None:
        self.connection_id += 1

        logger.debug("Adding new connection...")
        logger.debug("-----")

        output_module: str = a_list[0].lower().strip()
        output_port: str = a_list[1].lower().strip()

        logger.debug(f"Output module: {output_module}")
        logger.debug(f"Output port: {output_port}")

        try:
            connection_type = CONNECTION_TYPES[a_list[2].lower()]
            logger.debug(f"Matched connection type: {connection_type}")
        except KeyError:
            print(f"Invalid connection: {a_list[2]}")
            connection_type = "cv"

        input_module: str = a_list[3].lower().strip()
        input_port: str = a_list[4].lower().strip()

        if a_list[5] is not None:
            arguments = self.parse_arguments(a_list[5])
        else:
            arguments = {}

        logger.debug(f"Input module: {input_module}")
        logger.debug(f"Input port: {output_port}")

        self.check_module_existence(output_module, output_port, "out")
        self.check_module_existence(input_module, input_port, "in")

        logger.debug("Appending output and input connections to mainDict...")

        output_dict = {
            "input_module": input_module,
            "input_port": input_port,
            "connection_type": connection_type,
            "voice": voice,
            "id": self.connection_id}

        input_dict = {
            "output_module": output_module,
            "output_port": output_port,
            "connection_type": connection_type,
            "voice": voice,
            "id": self.connection_id}

        for key in arguments:
            output_dict[key] = arguments[key]
            input_dict[key] = arguments[key]

        self.modules[output_module]["connections"]["out"][output_port].append(
                output_dict)
        self.modules[input_module]["connections"]["in"][input_port] = input_dict
        logger.debug("-----")

    def check_module_existence(self, module: str, port: str = "port", direction: str = "") -> None:
        logger.debug(f"Checking if module already existing in the module dictionary: {module}")

        # Check if module exists in main dictionary
        if module not in self.modules:
            self.modules[module] = {
                "parameters": {},
                "connections": {"out": {}, "in": {}}
            }

        # If it exists, check if the port exists
        if direction == "in":
            if port not in self.modules[module]["connections"]["in"]:
                self.modules[module]["connections"]["in"][port] = []

        if direction == "out":
            if port not in self.modules[module]["connections"]["out"]:
                self.modules[module]["connections"]["out"][port] = []

    def add_parameter(self, module: str, name: str, value: str) -> None:
        self.check_module_existence(module)
        # Add parameter to mainDict
        logger.debug(f"Adding parameter: {module} - {name} - {value}")
        self.modules[module]["parameters"][name] = value

    def add_comment(self, value: str) -> None:
        self.comments.append(value)

    def ask_command(self, command: Optional[str] = None, one_shot: bool = False):
        if one_shot:
            command = command
        if not command:
            command = input("> ").lower().strip()

        if command == "module":
            self.detail_module()
        elif command == "modules":
            self.detail_module(show_all=True)
        elif command == "print":
            self.print_dict()
        elif command == "export":
            self.export_json()
        elif command == "connections":
            self.print_connections()
        elif command == "graph":
            self.graphviz()
        else:
            print("Invalid command, please try again.")

        if one_shot:
            return
        self.ask_command()

    def _print_module(self, module: str) -> None:
        print("-------")
        print(f"Showing information for module: {module.upper()}")
        print()
        print("Inputs:")
        for c in self.modules[module]["connections"]["in"]:
            keyvalue = self.modules[module]["connections"]["in"][c]
            print(f"{keyvalue['output_module'].title()} ({keyvalue['output_port'].title()}) > {c.title()} - {keyvalue['connection_type'].title()}")
        print()

        print("Outputs:")
        for x in self.modules[module]["connections"]["out"]:
            port = self.modules[module]["connections"]["out"][x]
            for c in port:
                keyvalue = c
                print(f"{x.title()} > {keyvalue['input_module'].title()} ({keyvalue['input_port'].title()})  - {keyvalue['connection_type'].title()} - {keyvalue['voice']}")
        print()

        print("Parameters:")
        for p in self.modules[module]["parameters"]:
            value = self.modules[module]["parameters"][p]
            print(f"{p.title()} = {value}")
        print()

        if not self.quiet:
            print("-------")

    def detail_module(self, show_all: bool = False) -> None:
        if not show_all:
            module = input("Enter module name: ").lower()
            if module in self.modules:
                self._print_module(module)
        else:
            for module in self.modules:
                self._print_module(module)

    def print_connections(self) -> None:
        print()
        print("Printing all connections by type...")
        print()

        for ctype in CONNECTION_TYPES.values():
            print(f"Connection type: {ctype}")
            # For each module
            for module in self.modules:
                # Get all outgoing connections:
                connections = self.modules[module]["connections"]["out"]
                for connection in connections.values():
                    for subc in connection:
                        if subc["connection_type"] == ctype:
                            print(f"{module.title()} > {subc['input_module'].title()} ({subc['input_port'].title()})")
            print()

    def export_json(self) -> None:
        # Exports mainDict as json file
        # name = filename.split(".")[0]
        # filepath = getFilePath(name + '.json')
        # print("Exporting dictionary as file: " + filepath)
        # with open(filepath, 'w') as fp:
        #     json.dump(mainDict, fp)
        print(json.dumps({
            "info": {"patchbook_version": self._PARSER_VERSION},
            "modules": self.modules,
            "comments": self.comments
        }))

    def graphviz(self) -> str:
        linetypes = {
            "audio": {"style": "bold"},
            "cv": {"color": "gray"},
            "gate": {"color": "red", "style": "dashed"},
            "trigger": {"color": "orange", "style": "dashed"},
            "pitch": {"color": "blue"},
            "clock": {"color": "purple", "style": "dashed"}
        }
        if self.direction == "DN":
            rank_dir_token = "rankdir = BT;\n"
            from_token = ":s  -> "
            to_token = ":n  "
        else:
            rank_dir_token = "rankdir = LR;\n"
            from_token = ":e  -> "
            to_token = ":w  "
        if not self.quiet:
            print("Generating signal flow code for GraphViz.")
            print("Copy the code between the line break and paste it into https://dreampuf.github.io/GraphvizOnline/ to download a SVG / PNG chart.")
        conn = []
        total_string = ""
        if not self.quiet:
            print("-------------------------")
        print("digraph G{\n" + rank_dir_token + "splines = polyline;\nordering=out;")
        total_string += "digraph G{\n" + rank_dir_token + "splines = polyline;\nordering=out;\n"
        for module in sorted(self.modules):
            # Get all outgoing connections:
            outputs = self.modules[module]["connections"]["out"]
            module_outputs = ""
            out_count = 0
            out: str
            for out in sorted(outputs):
                out_count += 1
                out_formatted: str = f"_{re.sub('[^A-Za-z0-9]+', '', out)}"
                module_outputs += f"<{out_formatted}> {out.upper()}"
                if out_count < len(outputs.keys()):
                    module_outputs += " | "
                connections = outputs[out]
                for c in connections:
                    line_style_array = []
                    graphviz_parameters = [
                        "color", "weight", "style", "arrowtail", "dir"]
                    for param in graphviz_parameters:
                        if param in c:
                            line_style_array.append(f"{param}={c[param]}")
                        elif param in linetypes[c["connection_type"]]:
                            line_style_array.append(f"{param}={linetypes[c['connection_type']][param]}")
                    if len(line_style_array) > 0:
                        line_style = f"[{', '.join(line_style_array)}]"
                    else:
                        line_style = ""
                    in_formatted = f"_{re.sub('[^A-Za-z0-9]+', '', c['input_port'])}"
                    connection_line: str = f"{module.replace(' ', '')}:{out_formatted}{from_token}{c['input_module'].replace(' ', '')}:{in_formatted}{to_token}{line_style}"
                    conn.append([c["input_port"], connection_line])

            # Get all incoming connections:
            inputs = self.modules[module]["connections"]["in"]
            module_inputs = ""
            in_count = 0
            inp: str
            for inp in sorted(inputs):
                inp_formatted: str = f"_{re.sub('[^A-Za-z0-9]+', '', inp)}"
                in_count += 1
                module_inputs += f"<{inp_formatted}> {inp.upper()}"
                if in_count < len(inputs.keys()):
                    module_inputs += " | "

            # Get all parameters:
            params = self.modules[module]["parameters"]
            module_params = ""
            param_count = 0
            par: str
            for par in sorted(params):
                param_count += 1
                module_params += f"{par.title()} = {params[par]}"
                if param_count < len(params.keys()):
                    module_params += '\\n'

            # If module contains parameters
            if module_params != "":
                # Add them below module name
                middle = "{{" + module.upper() + "}|{" + module_params + "}}"
            else:
                # Otherwise just display module name
                middle = module.upper()

            final_box = module.replace(" ", "") + "[label=\"{ {" + module_inputs + "}|" + middle + "| {" + module_outputs + "}}\"  shape=Mrecord]"
            print(final_box)
            total_string += final_box + "; "

        # Print Connections
        for c in sorted(conn):
            print(c[1])
            total_string += c[1] + "; "

        if len(self.comments) != 0:
            format_comments: str = ""
            comments_count = 0
            for comment in self.comments:
                comments_count += 1
                format_comments += f"{{0}}"
                if comments_count < len(self.comments):
                    format_comments += "|"
            format_comments = "comments[label=<{{{<b>PATCH COMMENTS</b>}|" + format_comments + "}}>  shape=Mrecord]"
            print(format_comments)

        print("}")
        total_string += "}"

        if not self.quiet:
            print("-------------------------")
            print()
        return total_string

    def print_dict(self) -> None:
        for k, v in self.modules.items():
            print(f"{k.title()}: {v}")
