import argparse
import sys
from typing import List, Set, Tuple

from adornment import adorn_datalog_program, AdornedPredicate, adorn_facts
from datalog_parser import parse_datalog_program
from generation import execute_generation
from models import DatalogProgram, Rule
from modification import modification_step
from processing import generate_magic_facts_and_rules


def read_datalog_program(filename: str) -> list:
    """
    Reads a Datalog program from a file and splits it into lines.

    Args:
        filename (str): The path to the file containing the Datalog program.

    Returns:
        list: A list of non-empty lines from the Datalog program, or an empty list if an error occurs.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [
                line.strip()
                for line in file
                if line.strip() and not line.startswith("%")
            ]
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file '{filename}' was not found.") from e
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied when trying to read '{filename}'."
        ) from e
    except OSError as e:  # Catching OSError which includes IOError
        raise OSError(f"Error reading the file '{filename}': {e}") from e


def apply_magic_set_transformation(
    program: DatalogProgram, apply_reorder_optimization: bool
) -> DatalogProgram:
    """
    Applies the Magic Set transformation to a Datalog program, including adornment, magic rule generation,
    modification of rules with magic atoms, and generation of magic facts and query rules.

    Args:
        program (DatalogProgram): The original Datalog program to transform.
        apply_reorder_optimization (bool): Whether to apply greedy binding order optimization.

    Returns:
        DatalogProgram: A new DatalogProgram object representing the transformed program.
    """
    adorned_rules, query_adorned_atoms, query_adorned_predicates = (
        adorn_datalog_program(program, apply_reorder_optimization)
    )
    magic_rules = execute_generation(adorned_rules)
    modified_rules = modification_step(adorned_rules)
    magic_seeds, query_rules = generate_magic_facts_and_rules(
        query_adorned_atoms, query_adorned_predicates
    )

    all_adorned_predicates = get_unique_adorned_predicates(adorned_rules)
    adorned_facts = adorn_facts(program.facts, all_adorned_predicates)

    magic_program = DatalogProgram()
    magic_program.facts.extend(program.facts + adorned_facts)
    magic_program.rules.extend(magic_rules + modified_rules + query_rules)
    magic_program.facts.extend(magic_seeds)
    magic_program.set_query(program.query)

    return magic_program


def flatten(list_of_lists: List[List]) -> List:
    """Flatten a list of lists into a single list."""
    return [item for sublist in list_of_lists for item in sublist]


def get_unique_adorned_predicates(adorned_rules: List[Rule]) -> List[Tuple[str, str]]:
    unique_combinations: Set[Tuple[str, str]] = set()

    # Add heads if they are AdornedPredicate
    for r in adorned_rules:
        if isinstance(r.head, AdornedPredicate):
            unique_combinations.add((r.head.name, r.head.binding_pattern))

    # Add bodies if they are AdornedPredicate
    for p in flatten([r.body for r in adorned_rules]):
        if isinstance(p, AdornedPredicate):
            unique_combinations.add((p.name, p.binding_pattern))

    return list(unique_combinations)


def main():
    parser = argparse.ArgumentParser(
        description="Optimize Datalog program execution with Magic Set method."
    )
    parser.add_argument(
        "--program", type=str, required=True, help="Filename of the Datalog program."
    )
    parser.add_argument(
        "--greedy-binding-order",
        action="store_true",
        help="Apply greedy binding order optimization.",
    )

    try:
        args = parser.parse_args()

        program_lines = read_datalog_program(args.program)
        if not program_lines:
            print(f"No data to process from {args.program}, exiting.")
            return

        datalog_program = parse_datalog_program(program_lines)
        if not datalog_program:
            print("Failed to parse any data into a Datalog program, exiting.")
            return

        transformed_program = apply_magic_set_transformation(
            datalog_program, args.greedy_binding_order
        )

        print(transformed_program)

    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except PermissionError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
