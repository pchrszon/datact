#!/usr/bin/env python

# datact - data-aware synchronization in PRISM
#
# Usage:
# datact <MODEL> <DOMAIN>
#
# Assuming each action in <MODEL> has type [1 .. DOMAIN], datact translates the
# <MODEL> into a standard PRISM model without data-aware synchronization.


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
                act_part_new = re.sub(r"\b" + action + r"\b", action + "_" + str(i), act_part)

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
                renamings.append(action + "_" + str(i) + " = " + rename_part + "_" + str(i))

            line_new = start + str.join(", ", renamings) + end + "\n"
            lines_expanded.append(line_new)
        else:
            lines_expanded.append(line)

    return lines_expanded


def expand_actions(actions, values, lines):
    result = lines
    for action in actions:
        result = expand_commands(action, values, result)
        result = expand_renamings(action, values, result)

    return result


def main():
    if len(sys.argv) != 3:
        print("Usage:", sys.argv[0], "<FILE> <MAX-VALUE>")
        return 1

    file_name = sys.argv[1]
    max_value = int(sys.argv[2])

    with open(file_name) as f:
        lines = f.readlines()

    actions = find_actions(lines)
    lines = expand_actions(actions, list(range(1, max_value + 1)), lines)

    for line in lines:
        print(line, end = "")


if __name__ == "__main__":
    main()
