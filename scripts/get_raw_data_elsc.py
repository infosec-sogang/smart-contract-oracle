import sys, os
import common
import plot_ELSC_bug
from common import init_elsc_bug_info

# Signatures reported by the Smartian version that uses its own (strict) oracle.
SC_STRICT = "SuicidalContractStrict"
EL_STRICT = "EtherLeakStrict"

def build_time_map_list(bug_info, target_dirs, iter_cnt):
    time_map_list = []
    for iter in range(1, iter_cnt + 1):
        time_map = {}
        for targ_dir in target_dirs:
            plot_ELSC_bug.analyze_dir(bug_info, targ_dir, iter, time_map)
        time_map_list.append(time_map)
    return time_map_list

def print_csv(bug_info, targ_list, time_map_list, bug_sigs, sig_names):
    header = "contract,bug_type,func"
    for iter in range(1, len(time_map_list) + 1):
        header += ",iter_%d" % iter
    print(header)
    for targ in targ_list:
        printed = []
        for (bug_sig, func) in bug_info[targ]:
            if bug_sig not in bug_sigs or func is None or (bug_sig, func) in printed:
                continue
            printed.append((bug_sig, func))
            row = "%s,%s,%s" % (targ, sig_names[bug_sig], func)
            for time_map in time_map_list:
                found_time = time_map.get((targ, bug_sig), [])
                # Only the found times of this function, not of the other
                # functions in the same contract.
                found_time = [t for (f, t) in found_time if f == func]
                row += ",%d" % min(found_time) if found_time else ",N/A"
            print(row)

def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    if strict:
        args.remove("--strict")
    bug_types = ["SC", "EL"]
    if "--bug" in args:
        idx = args.index("--bug")
        bug_types = [args[idx + 1]]
        args = args[:idx] + args[idx + 2:]
    if len(args) < 1 or any(b not in ["SC", "EL"] for b in bug_types):
        print("Usage: %s [--strict] [--bug SC|EL] [result dirs ...]" % sys.argv[0])
        exit(1)

    SC, EL = (SC_STRICT, EL_STRICT) if strict else (common.SC, common.EL)
    # plot_ELSC_bug.analyze_targ() keys the found times by these signatures.
    plot_ELSC_bug.SC, plot_ELSC_bug.EL = SC, EL
    bug_info = init_elsc_bug_info(SC, EL)
    target_dirs = sorted(args)
    iter_cnt = len(os.listdir(target_dirs[0]))
    time_map_list = build_time_map_list(bug_info, target_dirs, iter_cnt)

    targ_list = [ (targ_dir.split('/')[-2]
                if targ_dir.endswith('/') else targ_dir.split('/')[-1])
                for targ_dir in target_dirs ]
    bug_sigs = [ {"SC": SC, "EL": EL}[b] for b in bug_types ]
    sig_names = { SC: common.SC, EL: common.EL }
    print_csv(bug_info, targ_list, time_map_list, bug_sigs, sig_names)

if __name__ == "__main__":
    main()
