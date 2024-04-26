from dataclasses import dataclass
from typing import List, Set
from collections import deque

from models import DatalogProgram, Predicate, Rule


@dataclass
class AdornedPredicate(Predicate):
    """
    Represents a predicate that includes a binding pattern used to optimize query processing.

    Attributes:
        name (str): The name of the predicate.
        args (List[str]): A list of arguments for the predicate.
        binding_pattern (str): A pattern indicating which arguments are bound ('b') and which are free ('f').
    """

    binding_pattern: str

    def __repr__(self) -> str:
        return f"{self.name}_{self.binding_pattern}({', '.join(self.args)})"

    def adorned_name(self) -> str:
        """Generate the adorned name of the predicate."""
        return f"{self.name}_{self.binding_pattern}"


def adorn_predicate(predicate: Predicate, binding_pattern: str) -> AdornedPredicate:
    """
    Create an adorned predicate using the provided binding pattern.

    Args:
        predicate (Predicate): The original predicate to adorn.
        binding_pattern (str): The binding pattern for the predicate.

    Returns:
        AdornedPredicate: The newly created adorned predicate.
    """
    return AdornedPredicate(predicate.name, predicate.args, binding_pattern)


def determine_case_based_binding(args: List[str]) -> str:
    """
    Generate a binding pattern based on argument types, where constants are marked as 'b' and variables as 'f'.

    Args:
        args (List[str]): A list of predicate arguments.

    Returns:
        str: A binding pattern string.
    """
    pattern = ["f" if arg.isupper() else "b" for arg in args]
    return "".join(pattern)


def adorn_query(datalog_program: DatalogProgram, query: Rule) -> List[AdornedPredicate]:
    """
    Create an initial list of adorned predicates from the query based on argument types.

    Args:
        datalog_program (DatalogProgram): The Datalog program containing the logic and data structure.
        query (Rule): The query containing predicates to adorn.

    Returns:
        List[AdornedPredicate]: A list of adorned predicates.
    """
    adorned_predicates = []
    for predicate in query.body:
        if datalog_program.is_predicate_intensional(predicate):
            binding_pattern = determine_case_based_binding(predicate.args)
            adorned_predicates.append(adorn_predicate(predicate, binding_pattern))
    return adorned_predicates


def generate_binding_from_set(args: List[str], bound_variables: Set[str]) -> str:
    """
    Generate a binding pattern for arguments, marking each as 'b' (bound) or 'f' (free).

    Args:
        args (List[str]): A list of arguments to analyze.
        bound_variables (Set[str]): A set of variables that are considered bound.

    Returns:
        str: A string representing the binding pattern, where 'b' indicates a bound variable and 'f' indicates a free variable.
    """
    pattern = ["b" if arg in bound_variables else "f" for arg in args]
    return "".join(pattern)


def greedy_binding_order(
    datalog_program: DatalogProgram, body: List[Predicate]
) -> List[Predicate]:
    """
    Sorts the predicates in a rule's body with a focus on optimization for query processing.
    Extensional predicates are prioritized over intensional ones, and within the same category,
    predicates with more arguments are given higher priority.

    Args:
        datalog_program (DatalogProgram): The Datalog program to query predicate status.
        body (List[Predicate]): A list of Predicate objects that make up the body of a rule.

    Returns:
        List[Predicate]: A sorted list of Predicate objects based on defined criteria.
    """

    def sort_key(predicate: Predicate) -> tuple:
        """
        Defines the sorting criteria for predicates:
        - First by type (extensional: 0, intensional: 1)
        - Then by the number of arguments in descending order

        Args:
        - predicate (Predicate): The predicate to evaluate for sorting.

        Returns:
        - tuple: Tuple where the first element is type priority, and the second is the negative argument count.
        """
        is_intensional = datalog_program.is_predicate_intensional(predicate)
        type_priority = 1 if is_intensional else 0
        return (type_priority, -len(predicate.args))

    ordered_body = sorted(body, key=sort_key)
    return ordered_body


def adorn_rule(
    datalog_program: DatalogProgram,
    rule: Rule,
    binding_pattern: str,
    reorder_body: bool = False,
) -> Rule:
    """
    Adorns a rule based on a specified binding pattern, sorts the predicates, and constructs a new rule.
    Predicates are adorned according to their type and the provided binding pattern, and the predicates
    in the body are sorted for optimal query execution.

    Args:
        datalog_program (DatalogProgram): The Datalog program for checking predicate statuses.
        rule (Rule): The rule to be adorned and sorted.
        binding_pattern (str): The binding pattern used to adorn the head predicate and influence body adornment.

    Returns:
        Rule: A new Rule object with an adorned head and an ordered and adorned body.
    """
    new_head = adorn_predicate(rule.head, binding_pattern)
    bound_variables = set(rule.head.args)
    new_body = []

    body = (
        rule.body
        if not reorder_body
        else greedy_binding_order(datalog_program, rule.body)
    )

    for predicate in body:
        if datalog_program.is_predicate_intensional(predicate):
            new_binding_pattern = generate_binding_from_set(
                predicate.args, bound_variables
            )
            adorned_predicate = adorn_predicate(predicate, new_binding_pattern)
            new_body.append(adorned_predicate)
        else:
            new_body.append(predicate)

        bound_variables.update(predicate.args)

    return Rule(new_head, new_body)


def adorn_datalog_program(
    datalog_program: DatalogProgram, reorder_body: bool = False
) -> tuple:
    """
    Adorn all rules in a Datalog program based on the adorned predicates derived from the query.
    This process helps optimize the query execution by pre-determining the binding patterns of predicates.

    Args:
        datalog_program (DatalogProgram): The Datalog program containing rules and a query to be adorned.

    Returns:
        tuple: A tuple containing a list of adorned rules, ready for optimized execution, and the adorned predicates.
    """
    adorned_predicates = adorn_query(datalog_program, datalog_program.query)
    adorned_predicates_queue = deque(adorned_predicates)
    seen = {predicate.adorned_name() for predicate in adorned_predicates_queue}

    adorned_rules = []

    while adorned_predicates_queue:
        current_adorned_predicate = adorned_predicates_queue.popleft()
        for rule in datalog_program.rules:
            if current_adorned_predicate.name == rule.head.name:
                new_rule = adorn_rule(
                    datalog_program,
                    rule,
                    current_adorned_predicate.binding_pattern,
                    reorder_body,
                )
                adorned_rules.append(new_rule)

                for predicate in new_rule.body:
                    if (
                        isinstance(predicate, AdornedPredicate)
                        and predicate.adorned_name() not in seen
                    ):
                        adorned_predicates_queue.append(predicate)
                        seen.add(predicate.adorned_name())

    return adorned_rules, adorned_predicates


def example_program1():
    from models import Fact

    program = DatalogProgram()

    program.add_fact(Fact(Predicate("parent", ["'Bob'", "'Alice'"])))
    program.add_fact(Fact(Predicate("parent", ["'Alice'", "'Carol'"])))

    program.add_rule(
        Rule(Predicate("ancestor", ["X", "Y"]), [Predicate("parent", ["X", "Y"])])
    )
    program.add_rule(
        Rule(
            Predicate("ancestor", ["X", "Y"]),
            [Predicate("ancestor", ["X", "Z"]), Predicate("parent", ["Z", "Y"])],
        )
    )

    # program.set_query(Rule(Predicate("q", []), Predicate("ancestor", ["X", "'Carol'"])))
    program.set_query(
        Rule(Predicate("q", []), [Predicate("ancestor", ["'Bob'", "'Carol'"])])
    )

    return program


def example_program2():
    from models import Fact

    program = DatalogProgram()

    program.add_fact(Fact(Predicate("edge", ["1", "3"])))
    program.add_fact(Fact(Predicate("edge", ["2", "4"])))
    program.add_fact(Fact(Predicate("edge", ["3", "5"])))

    program.add_rule(
        Rule(Predicate("path", ["X", "Y"]), [Predicate("edge", ["X", "Y"])])
    )
    program.add_rule(
        Rule(
            Predicate("path", ["X", "Y"]),
            [Predicate("edge", ["X", "Z"]), Predicate("path", ["Z", "Y"])],
        )
    )

    program.set_query(Rule(Predicate("q", []), [Predicate("path", ["1", "5"])]))

    return program


def main():
    program = example_program1()
    adorned_rules = adorn_datalog_program(program)
    for rule in adorned_rules:
        print(rule)


if __name__ == "__main__":
    main()
