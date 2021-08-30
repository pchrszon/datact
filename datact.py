#!/usr/bin/env python

# datact - data-aware synchronization in PRISM
#
# Usage:
# datact <MODEL> <DOMAIN> [<DOM-FILE>]
#
# Assuming each action in <MODEL> has type [1 .. DOMAIN], datact translates the
# <MODEL> into a standard PRISM model without data-aware synchronization.
#
# Optionally, specific actions can be given a domain different than <DOMAIN> by
# specifying a <DOM-FILE>. A <DOM-FILE> is a CSV-file with
# format <ACTION>, <DOMAIN>.


import re
import sys


def find_actions(lines):
    # match all non-tau actions
    pat_actions = re.compile(r"\s*[\[\]](.+)[\[\]]")

    actions = set()
    for line in lines:
        m = pat_actions.match(line)
        if m:
            line_actions = set([act.strip() for act in m.group(1).split(",")])
            actions.update(line_actions)

    return actions


def expand_commands(action, values, lines):
    # match all commands containing 'action'
    pat_command = re.compile(r"(\s*[\[\]].*\b" + action + r"\b.*[\[\]])(.*;)")

    lines_expanded = []
    for line in lines:
        m = pat_command.match(line)
        if m:
            # split command into action and guard + update
            act_part, var_part = m.group(1), m.group(2)

            for i in values:
                # expand action name by index
                act_part_new = re.sub(r"\b" + action + r"\b", "_" + action + "_" + str(i), act_part)

                # replace action name by its value
                var_part_new = re.sub(r"\b" + action + r"\b", str(i), var_part)

                lines_expanded.append(act_part_new + var_part_new + "\n")
        else:
            lines_expanded.append(line)

    return lines_expanded


def expand_renamings(action, values, lines):
    # match all module renamings containing 'action'
    pat_renaming = re.compile(r"(module .+=.+\[.*)(\b" + action + r"\b)\s*=\s*(\b.+?\b)(.*\].*endmodule)")

    lines_expanded = []
    for line in lines:
        m = pat_renaming.match(line)
        if m:
            start, act_part, rename_part, end = m.group(1), m.group(2), m.group(3), m.group(4)

            renamings = []
            for i in values:
                renamings.append("_" + action + "_" + str(i) + " = " + "_" + rename_part + "_" + str(i))

            line_new = start + str.join(", ", renamings) + end + "\n"
            lines_expanded.append(line_new)
        else:
            lines_expanded.append(line)

    return lines_expanded


def expand_actions(actions, domains, default_domain, lines):
    result = lines
    for action in actions:
        if action in domains:
            domain = domains[action]
        else:
            domain = default_domain

        values = list(range(1, domain + 1))

        result = expand_commands(action, values, result)
        result = expand_renamings(action, values, result)

    return result


def read_domains(file_name):
    pat_domain = re.compile(r"(\b.+?\b)\s*,\s*(\b[0-9]+\b)")
    domains = dict()

    with open(file_name) as f:
        for line in f.readlines():
            m = pat_domain.search(line)
            if m:
                action, domain = m.group(1), int(m.group(2))
                domains[action] = domain

    return domains


# Module renamings may also rename actions that have an associated domain. Thus,
# we need to apply the same domain for the renamed actions.
def extend_domains(domains, lines):
    # match all module renamings
    pat_renamings = re.compile(r"module .+=.+\[(.+)\].*endmodule")
    pat_renaming = re.compile(r"\s*(\b.+\b)\s*=\s*(\b.+\b)")

    for line in lines:
        m = pat_renamings.match(line)
        if m:
            renamings = [r for r in m.group(1).split(",")]
            for renaming in renamings:
                mr = pat_renaming.match(renaming)
                if mr:
                    act_orig, act_new = mr.group(1), mr.group(2)
                    if act_orig in domains:
                        domains[act_new] = domains[act_orig]


def main():
    if len(sys.argv) not in [3, 4]:
        print("Usage:", sys.argv[0], "<FILE> <DOM-MAX-VALUE> [<DOM-FILE>]")
        return 1

    file_name = sys.argv[1]
    default_domain = int(sys.argv[2])

    with open(file_name) as f:
        lines = f.readlines()

    domains = dict()
    if len(sys.argv) == 4:
        domains = read_domains(sys.argv[3])
        extend_domains(domains, lines)

    actions = find_actions(lines)
    lines = expand_actions(actions, domains, default_domain, lines)

    for line in lines:
        print(line, end = "")


if __name__ == "__main__":
    main()
