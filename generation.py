from typing import List

from adornment import AdornedPredicate
from models import Rule


def generate_magic_predicate(adorned_predicate: AdornedPredicate) -> AdornedPredicate:
    """
    Transforms an adorned predicate into its "magic" counterpart, keeping only the bound arguments.

    The "magic" predicate is a reduced form of the original predicate used in the generation of
    magic rules, which is a part of the Magic Set method for query optimization. The new predicate
    retains the name of the original but is prefixed with "magic_" and only includes arguments
    that are bound (denoted by 'b' in the binding pattern).

    Args:
        adorned_predicate (AdornedPredicate): The adorned predicate to transform.

    Returns:
        AdornedPredicate: A new adorned predicate representing the "magic" version.
    """
    bound_arguments = [
        arg
        for arg, bound in zip(adorned_predicate.args, adorned_predicate.binding_pattern)
        if bound == "b"
    ]
    magic_name = f"magic_{adorned_predicate.name}"
    return AdornedPredicate(
        magic_name, bound_arguments, "".join("b" for _ in bound_arguments)
    )


def generate_magic_rules(rule: Rule) -> List[Rule]:
    """
    Generates magic rules from a rule by transforming each adorned predicate in the rule's body into a new rule.
    
    Each new rule (magic rule) consists of a new head generated from the adorned predicate and a body that includes
    the main rule's head and all predicates before the current adorned predicate.
    
    Args:
        rule (Rule): The rule from which to generate magic rules.
    
    Returns:
        List[Rule]: A list of magic rules generated from the adorned predicates.
    """
    magic_rules = []
    for index, predicate in enumerate(rule.body):
        if isinstance(predicate, AdornedPredicate):
            magic_head = generate_magic_predicate(predicate)
            magic_body = [generate_magic_predicate(rule.head)]
            magic_body.extend(rule.body[:index])
            magic_rules.append(Rule(magic_head, magic_body))
    return magic_rules


def execute_generation(adorned_rules: List[Rule]) -> List[Rule]:
    """
    Executes the generation of magic rules from a list of adorned rules.
    
    This function iterates through each adorned rule, generates corresponding magic rules,
    and collects them into a single list to return.
    
    Args:
        adorned_rules (List[Rule]): A list of adorned rules from which to generate magic rules.
    
    Returns:
        List[Rule]: A list of all generated magic rules.
    """
    all_magic_rules = []
    for rule in adorned_rules:
        all_magic_rules.extend(generate_magic_rules(rule))
    return all_magic_rules


def main():
    from models import Predicate

    adorned_rules = [
        Rule(
            AdornedPredicate("path", ["X", "Y"], "bb"), [Predicate("edge", ["X", "Y"])]
        ),
        Rule(
            AdornedPredicate("path", ["X", "Y"], "bb"),
            [Predicate("edge", ["X", "Z"]), AdornedPredicate("path", ["Z", "Y"], "bb")],
        ),
    ]
    magic_rules = execute_generation(adorned_rules)
    for rule in magic_rules:
        print(rule)


if __name__ == "__main__":
    main()
