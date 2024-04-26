from typing import List

from adornment import AdornedPredicate
from generation import generate_magic_predicate
from models import Rule


def modify_rule_with_magic_atom(
    adorned_rule: Rule, magic_predicate: AdornedPredicate
) -> Rule:
    """
    Modifies an adorned rule by adding a corresponding magic atom to its body.
    This magic atom helps in the optimization of query processing by limiting the inference of facts.

    Args:
        adorned_rule (Rule): The adorned rule to be modified.
        magic_predicate (AdornedPredicate): The magic predicate derived from the adorned rule's head.

    Returns:
        Rule: The modified rule with the magic atom added to its body.
    """
    new_body = [magic_predicate] + adorned_rule.body
    return Rule(adorned_rule.head, new_body)


def modification_step(adorned_rules: List[Rule]) -> List[Rule]:
    """
    Applies the modification step to a list of adorned rules, adding magic atoms to their bodies.

    Args:
        adorned_rules (List[Rule]): A list of adorned rules to be modified.

    Returns:
        List[Rule]: A list of modified rules.
    """
    modified_rules = []
    for adorned_rule in adorned_rules:
        magic_atom = generate_magic_predicate(adorned_rule.head)
        modified_rule = modify_rule_with_magic_atom(adorned_rule, magic_atom)
        modified_rules.append(modified_rule)
    return modified_rules


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
    magic_rules = modification_step(adorned_rules)
    for rule in magic_rules:
        print(rule)


if __name__ == "__main__":
    main()
