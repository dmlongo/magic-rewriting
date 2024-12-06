from dataclasses import dataclass


@dataclass
class Predicate:
    """
    Represents a predicate in logic programming with a name and a list of arguments.
    """

    name: str
    args: list

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(self.args)})"

    def get_name(self) -> str:
        return f"{self.name}"

    def arity(self):
        return len(self.args)

@dataclass
class Fact:
    """
    Represents a logical fact, essentially a wrapper for a Predicate object.
    """

    predicate: Predicate

    def __repr__(self) -> str:
        return f"{self.predicate}."

    def get_predicate_symbol(self) -> str:
        return f"{self.predicate.get_name()}"


    def get_arity(self) -> int:
        return self.predicate.arity()

@dataclass
class Rule:
    """
    Represents a logical rule, consisting of a head (a single Predicate) and a body (a list of Predicates).
    """

    head: Predicate
    body: list

    def __repr__(self) -> str:
        body_str = ", ".join(map(str, self.body))
        return f"{self.head} :- {body_str}."


@dataclass
class DatalogProgram:
    """
    Manages a collection of facts, rules, and supports querying in a Datalog-like rule-based system.
    Efficiently checks for intensional predicates by caching head names. The query is represented as a Rule.
    """

    facts: list = None
    rules: list = None
    query: Rule = None
    head_names: set = None

    def __post_init__(self):
        self.facts = self.facts if self.facts is not None else []
        self.rules = self.rules if self.rules is not None else []
        self.head_names = self.head_names if self.head_names is not None else set()

    def add_fact(self, fact: Fact):
        if not isinstance(fact, Fact):
            raise ValueError("Only Fact instances can be added.")
        self.facts.append(fact)

    def add_rule(self, rule: Rule):
        if not isinstance(rule, Rule):
            raise ValueError("Only Rule instances can be added.")
        self.rules.append(rule)
        self.head_names.add(rule.head.name)

    def set_query(self, query: Rule):
        if not isinstance(query, Rule):
            raise ValueError("Query must be a Rule instance.")
        self.query = query

    def is_predicate_intensional(self, predicate: Predicate) -> bool:
        return predicate.name in self.head_names

    def get_extensional_predicates(self):
        """
        Returns a list [(s1, a1), ...] where sN is the N-th predicate symbol
        occurring in the initial set of facts, and aN is its arity.
        """
        symbols = set()
        for f in self.facts:
            symbols.add((f.get_predicate_symbol(), f.get_arity()))
        return symbols

    def __repr__(self) -> str:
        facts_str = "\n".join(map(str, self.facts))
        rules_str = "\n".join(map(str, self.rules))
        query_str = f"{self.query}" if self.query else ""
        components = [part for part in [facts_str, rules_str, query_str] if part]
        return "\n\n".join(components)
