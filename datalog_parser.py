from models import DatalogProgram, Fact, Predicate, Rule


def parse_predicate(predicate_str: str) -> Predicate:
    """
    Parses a string into a Predicate object.

    Args:
        predicate_str (str): A string representing a predicate in the format 'Name(arg1, arg2, ...)'.

    Returns:
        Predicate: A Predicate object.
    """
    try:
        if "(" not in predicate_str or ")" not in predicate_str:
            return Predicate(predicate_str.strip(), [])
        predicate_name, args_str = predicate_str.split("(", 1)
        args = args_str.strip(")").split(",")
        return Predicate(predicate_name.strip(), [arg.strip() for arg in args])
    except ValueError as e:
        raise ValueError(
            f"Error parsing predicate from string '{predicate_str}': {str(e)}"
        ) from e


def parse_line(line: str):
    """
    Parses a single line of a Datalog program into either a Fact or a Rule object.

    Args:
        line (str): A string representing a line in a Datalog program.

    Returns:
        Either a Fact or Rule object depending on the line content.
    """
    try:
        if ":-" not in line:
            return Fact(parse_predicate(line.strip().rstrip(".")))
        head_str, body_str = line.split(":-", 1)
        head = parse_predicate(head_str.strip())
        body = [
            parse_predicate(pred.strip() + ")")
            for pred in body_str.strip().rstrip(".").split("), ")
            if pred
        ]
        return Rule(head, body)
    except ValueError as e:
        raise ValueError(f"Error parsing line '{line}': {str(e)}") from e


def parse_datalog_program(program_lines: list) -> DatalogProgram:
    """
    Parses multiple lines into a DatalogProgram instance containing facts and rules.

    Args:
        program_lines (list): A list of strings, each representing a line of a Datalog program.

    Returns:
        DatalogProgram: A DatalogProgram object filled with parsed facts and rules.
    """
    datalog_program = DatalogProgram()
    for line in program_lines:
        if line.strip():
            parsed_line = parse_line(line)
            if isinstance(parsed_line, Fact):
                datalog_program.add_fact(parsed_line)
            elif isinstance(parsed_line, Rule):
                if parsed_line.head.name == "goal__reachable":
                    datalog_program.set_query(parsed_line)
                else:
                    datalog_program.add_rule(parsed_line)
    return datalog_program


def main():
    sample_program = [
        "pddl_type_product(lco).",
        "pddl_type_object(lco).",
        "may__interface(rat__a, lco).",
        "goal__reachable :- on(b2, a3), on(b5, a2), normal(s12), normal(s13).",
        "first(Var_batch__atom__in, Var_pipe) :- pddl_type_pipe(Var_pipe), pddl_type_batch__atom(Var_batch__atom__in), pddl_type_area(Var_from__area), on(Var_batch__atom__in, Var_from__area).",
    ]

    parsed_datalog = parse_datalog_program(sample_program)
    print(parsed_datalog)


if __name__ == "__main__":
    main()
