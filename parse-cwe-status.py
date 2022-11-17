#!/usr/bin/env python3
import sys
import argparse
import re


last_df_var = 84


def get_status_str(status: int) -> str:
    if status - 128 == 34:
        return "SIGPROT"
    if status - 128 == 6:
        return "SIGABRT"
    if status == 124:
        return "TIMEOUT"
    if status == 0:
        return "OK"
    return str(status)


def update_dataflow_variant(status2dfvar: dict[int, list[int]], status: int, df_var: int) -> None:
    if status not in status2dfvar.keys():
        status2dfvar[status] = []
        for i in range(0, last_df_var + 1):
            status2dfvar[status].append(0)
    status2dfvar[status][df_var] = status2dfvar[status][df_var] + 1


def update_functional_variant(func_vars: dict[str, dict[int, int]], status: int, f_var: str) -> None:
    if f_var not in func_vars.keys():
        func_vars[f_var] = {}

    func_vars[f_var][status] = func_vars[f_var].get(status, 0) + 1


def do_parsing(filename: str) -> tuple[str, dict[int, list[int]], dict[str, dict[int, int]]]:
    with open(filename) as f:
        entries = [l for l in f]
        headline = entries[0]

        dataflow_stats: dict[int, list[int]] = {}
        functional_stats: dict[str, dict[int, int]] = {}

        entry_pattern = re.compile('(\S*)__(\S+)_(\d+)-\w* (\d*)\n')
        for e in entries[1:]:
            e_match = entry_pattern.match(e)
            if e_match:
                status = int(e_match.group(4))
                dataflow_var = int(e_match.group(3))
                functional_var = e_match.group(2)
                update_dataflow_variant(dataflow_stats, status, dataflow_var)
                update_functional_variant(functional_stats, status, functional_var)
            else:
                print("Failed to parse line:\n\t" + e, file=sys.stderr, end="")

        return (headline, dataflow_stats, functional_stats)


def print_exit_status_stats(status2dfvar: dict[int, list[int]]) -> None:
    print("\n===== EXIT STATUS =====")

    for status in sorted(status2dfvar.keys()):
        st_sum = sum(status2dfvar[status])
        print('{:10s} {:>5d}'.format(get_status_str(status), st_sum))


def print_dataflow_stats(status2dfvar: dict[int, list[int]]) -> None:
    print("\n===== DATAFLOW VARIANTS =====")

    # Header
    print(" VAR ", end="")
    for status in sorted(status2dfvar.keys()):
        print("{:>10s}".format(get_status_str(status)), end="")
    print()

    # Rows
    for dfvar in range(1, last_df_var + 1):
        dfvar_sum = sum(status2dfvar[s][dfvar] for s in status2dfvar.keys())
        if dfvar_sum > 0:
            print(' {:2d}: '.format(dfvar), end="")
            for s in sorted(status2dfvar.keys()):
                print('{:>10d}'.format(status2dfvar[s][dfvar]), end="")
            print()


def print_functional_stats(exit_codes: list[int], func_stats: dict[str, dict[int, int]]) -> None:
    print("\n===== FUNCTIONAL VARIANTS =====")

    # Header
    print("{:30s}".format(""), end="")
    for s in exit_codes:
        print("{:>10s}".format(get_status_str(s)), end="")
    print()

    # Rows
    for fvar in func_stats.keys():
        print('{:30s}'.format(fvar), end="")
        for status in exit_codes:
            n = func_stats[fvar].get(status, 0)
            print('{:>10d}'.format(n), end="")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Juliet test cases run log")
    parser.add_argument("filename", type=str, help="path to file with run log, e.g. good.run")
    args = parser.parse_args()

    (headline, dataflow_stats, functional_stats) = do_parsing(args.filename)
    print_exit_status_stats(dataflow_stats)
    print_dataflow_stats(dataflow_stats)
    print_functional_stats(sorted(dataflow_stats.keys()), functional_stats)
