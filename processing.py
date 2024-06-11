from typing import List, Tuple

from adornment import AdornedPredicate
from generation import generate_magic_predicate
from models import Fact, Predicate, Rule


def generate_magic_facts_and_rules(
    query_adorned_atoms: List[AdornedPredicate],
    query_adorned_predicates: List[AdornedPredicate],
) -> Tuple[List[Predicate], List[Rule]]:
    """
    Generate magic seed facts and query rules for each adorned predicate derived from the query.

    Args:
        query_adorned_atoms (List[AdornedPredicate]): List of adorned atoms from the query.
        query_adorned_predicates (List[AdornedPredicate]): List of adorned predicates from the query.

    Returns:
        Tuple[List[Predicate], List[Rule]]: A tuple containing:
            - A list of magic seed facts.
            - A list of query rules.
    """
    magic_seed_facts: List[Predicate] = []
    query_rules: List[Rule] = []

    for adorned_atom in query_adorned_atoms:
        magic_seed_fact = create_magic_seed(adorned_atom)
        magic_seed_facts.append(magic_seed_fact)

    for adorned_predicate in query_adorned_predicates:
        variable_names = generate_variable_names("Var_", len(adorned_predicate.args))
        predicate_head = Predicate(adorned_predicate.name, variable_names)
        predicate_body = AdornedPredicate(
            adorned_predicate.name, variable_names, adorned_predicate.binding_pattern
        )
        query_rule = Rule(predicate_head, [predicate_body])
        query_rules.append(query_rule)

    return magic_seed_facts, query_rules


def create_magic_seed(adorned_predicate: AdornedPredicate) -> Fact:
    """
    Generates a magic seed predicate from an adorned predicate. Only bound arguments are retained.

    Args:
        adorned_predicate (AdornedPredicate): The adorned predicate to transform.

    Returns:
        Fact: The resulting magic seed predicate.
    """
    return Fact(generate_magic_predicate(adorned_predicate))


def generate_variable_names(prefix: str, number: int) -> List[str]:
    """
    Creates a list of uniquely named variables with a given prefix and a specified number.

    Args:
        prefix (str): The prefix to prepend to each variable name.
        number (int): The total number of variable names to generate.

    Returns:
        List[str]: A list of unique variable names.
    """
    return [f"{prefix}{i + 1}" for i in range(number)]
