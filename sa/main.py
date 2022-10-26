import inspect
import os
from typing import Any, List, Dict, Union
from pathlib import Path
from lark import Lark, Tree, tree, exceptions
from Result import Result, ResultMultiplePositions
from sa.Result import Result, ResultMultiplePositions, output_result

from rules import local_rules_module


class SA:
    """
    The main class -- loads the cairo grammar, and runs rules.
    """

    @staticmethod
    def load_cairo_grammar() -> Lark:
        _module_dir = Path(__file__).resolve().parent
        GRAMMAR_FILENAME = _module_dir.joinpath("grammars", "cairo.lark")
        with open(GRAMMAR_FILENAME, "r", encoding="utf8") as f:
            buf = f.read()
        cairo_parser = Lark(
            buf,
            start=[
                "cairo_file",
                "code_block",
                "code_element",
                "expr",
                "instruction",
                "type",
                "typed_identifier",
            ],
            parser="lalr",
            propagate_positions=True,
        )

        return cairo_parser

    @staticmethod
    def load_classes_in_module(module: Any) -> List:
        return [cls() for (_, cls) in inspect.getmembers(module, inspect.isclass)]

    def __init__(self) -> None:
  
        self.parser = SA.load_cairo_grammar()
  
        self.data: Dict[str, Any] = {}
        self.rules = SA.load_classes_in_module(local_rules_module)

    def run_local_rules(
        self, filename: str, parsed_cairo_file: Any) -> List[Union[Result, ResultMultiplePositions]]:
        """
        Run all local rules.

        TODO: add argument to only run certain rule or exclude others.
        """
        results = []
        for Rule in self.rules:
            results += Rule.run_rule(filename, parsed_cairo_file)
        
        print("printing resuts: ")
            
        return results


    def parse_cairo_file(self, filename: str) -> Union[Tree, None]:
        """
        Parse the cairo file
        """
        try:
            with open(filename, "r", encoding="utf8") as f:
                return self.parser.parse(f.read(), start="cairo_file")
        except exceptions.UnexpectedCharacters as e:
            print(f"Could not parse {filename}: {e}")
            return None


def analyze_directory(rootdir: str) -> List[Any]:
    """
    Run rules in all .cairo files inside a directory.
    """
    sa = SA()

    all_results = []

    for subdir, _dirs, files in os.walk(rootdir):
        for file in files:
            fname = os.path.join(subdir, file)

            if fname.endswith(".cairo"):
                parsed_cairo_file = sa.parse_cairo_file(fname)
                if not parsed_cairo_file:
                    continue

                all_results += sa.run_local_rules(fname, parsed_cairo_file)
                sa.run_gatherer_rules(fname, parsed_cairo_file)

    all_results += sa.run_post_process_rules()
    return all_results


def analyze_file() -> List[Union[Result, ResultMultiplePositions]]:
    """
    Run analysis rules on a .cairo file.
    """
    fname = "uinitialized_variable.cairo"
    sa = SA()
    parsed_cairo_file = sa.parse_cairo_file(fname)
    print("Printing parsed cairo file\n")
    print(parsed_cairo_file)
    print("\n")

    if parsed_cairo_file:
        print("analysing")
        return sa.run_local_rules(fname, parsed_cairo_file)
    return []


if __name__ == "__main__":
    fname = "out.sarif"

    res = analyze_file()
    print(type(res))
    output_result(res,fname)
