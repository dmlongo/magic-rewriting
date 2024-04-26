from typing import List, Tuple

from adornment import AdornedPredicate
from generation import generate_magic_predicate
from models import Fact, Predicate, Rule


def generate_magic_facts_and_rules(
    query_adorned_predicates: List[AdornedPredicate],
) -> Tuple[List[Fact], List[Rule]]:
    """
    For each adorned predicate derived from the query, generate a corresponding magic seed fact
    and a query rule.

    Args:
        query_adorned_predicates (List[AdornedPredicate]): Adorned predicates from the query rule.

    Returns:
        Tuple[List[Fact], List[Rule]]: A tuple containing a list of magic seed facts and a list of query rules.
    """
    magic_seed_facts = []
    query_rules = []

    for adorned_predicate in query_adorned_predicates:
        magic_seed_fact = create_magic_seed(adorned_predicate)
        magic_seed_facts.append(magic_seed_fact)

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
