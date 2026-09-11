PLANFORGE HEURISTIC ENVIRONMENT
===============================

You are generating a heuristic for PlanForge, a numeric classical planner.

The heuristic will be used on CVRP instances generated from the same CVRP PDDL
domain, but with different numbers of customers, demands, distances,
capacities and vehicle limits.

Your generated heuristic must therefore generalize across instances.
Do NOT hardcode:
- PlanForge variable IDs
- customer names such as c2, c7, etc.
- number of customers
- capacity
- number of vehicles
- values from the example instance


AVAILABLE STATE API
===================

Inside compute_heuristic(), EvaluationState provides:

    eval_state.task()
    eval_state.state()
    eval_state.state_registry()
    eval_state.is_goal()

Goal states should return:

    0.0


NUMERIC STATE ACCESS
====================

The full numeric state can be read efficiently with:

    let registry = eval_state.state_registry();
    let state = eval_state.state();

    registry
        .view(state)
        .fill_numeric(&mut numeric_values)

The returned vector corresponds to PlanForge numeric-variable IDs.

If your heuristic needs numeric variables frequently, discover their IDs
ONCE in the constructor and store those IDs in the heuristic struct.

Do NOT search numeric-variable names on every heuristic evaluation.


PROPOSITIONAL STATE ACCESS
==========================

The complete propositional state can be read efficiently with:

    state.fill_state(registry, &mut propositional_values);

Alternatively, an individual fact can be tested with:

    fact.is_hold(registry.view(state))

For heuristics that inspect many customers, prefer reading the complete
propositional state once.


TASK INTROSPECTION
==================

The task exposes information including:

    task.variables()
    task.numeric_variables()
    task.get_operators()
    task.get_num_goals()
    task.get_goal_fact(i)
    task.get_fact_name(...)
    task.get_initial_numeric_state_values()

A propositional fact can be constructed using:

    ExplicitFact::propositional(var_id, value)


IMPORTANT OBSERVATIONS FROM THE CVRP DOMAIN
===========================================

PlanForge propositional variable names themselves are generic:

    var0
    var1
    var18
    ...

Do NOT use variable.name() to identify CVRP propositions.

Semantic fact names ARE preserved through task.get_fact_name(...).

Observed examples:

    Atom loc(c10)
    NegatedAtom loc(c10)

    Atom visited(c7)
    NegatedAtom visited(c7)

Therefore location and visited mappings can be discovered during heuristic
construction by scanning fact names.


NUMERIC VARIABLES
=================

In the inspected CVRP instance, the dynamic variables were exposed cleanly as:

    PNE vehicles()    type=Regular
    PNE load()        type=Regular
    PNE total-cost()  type=Cost

Their numeric IDs are instance/task dependent and MUST NOT be hardcoded.

Many other numeric expressions, especially those involving:

    demand
    capacity
    travel-cost
    max-vehicles

may be compiled by PlanForge into complex derived PNE expressions.

Do NOT assume they will appear as simple strings such as:

    demand(c7)
    capacity()
    travel-cost(c4,c7)

Prefer structural task/operator information where possible rather than
fragile parsing of translator-generated derived names.


GROUNDED OPERATORS
==================

Grounded operator names preserve useful CVRP semantics.

Observed forms include:

    visit d1 c7
    visit c4 c7
    return-to-depot c7
    visit-via-depot c4 c7

Operators can be inspected using:

    task.get_operators()
    op.name()
    op.preconditions()
    op.effects()
    op.assignment_effects()

PlanForge's FF implementation also uses:

    metric_operator_cost_from_initial_values(task, op)

to obtain the metric cost of grounded operators.

This may be useful to reconstruct routing costs without parsing derived
travel-cost variable names.


CONSTRUCTION VS EVALUATION
==========================

Your heuristic object may contain:
- precomputed arrays
- mappings
- helper structs
- cached task information
- reusable scratch buffers

Use LlmHeuristic::new(task) for information that depends only on the task.

compute_heuristic() may be called hundreds of thousands or millions of times,
so it should be relatively cheap.

Do NOT repeatedly:
- scan every task variable by name
- reconstruct static distance matrices
- parse the complete task
- allocate large temporary structures unnecessarily


FREEDOM
=======

You MAY:
- add fields to LlmHeuristic
- add helper structs and functions
- add scratch buffers
- perform task-dependent precomputation in new()
- implement any heuristic algorithm you consider useful for CVRP

You MUST preserve:
- the PlanForge Heuristic implementation
- the builder interface
- the external registration mechanism
- generalization across CVRP instances

Return the COMPLETE Rust source file.