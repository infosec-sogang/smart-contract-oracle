import sys, os, re
from common import init_elsc_bug_info
from common import read_log_file, parse_fuzz_log
from common import collect_found_times
from common import SC, EL, TOTAL_TIME, PLOT_INTERVAL

def count_found_before(bug_sigs, time_map, sec):
    n = 0
    for (targ, found_bug) in time_map:
        found_time = time_map[(targ, found_bug)]
        found_time = [time for (func, time) in found_time if func is not None]
        for t in found_time:
            if found_bug in bug_sigs and t < sec:
                n += 1
    return n

def plot_count_over_time(bug_sigs, time_map_list):
    for minute in range(0, TOTAL_TIME + PLOT_INTERVAL, PLOT_INTERVAL):
        sec = 60 * minute
        count_list = []
        for time_map in time_map_list:
            count_list.append(count_found_before(bug_sigs, time_map, sec))
        count_avg = float(sum(count_list)) / len(count_list)
        print("%02dm: %.1f" % (minute, count_avg))

def classify_targets(bug_info, targ_list):
    SC_list, EL_list = [], []

    for targ in targ_list:
        for (bug_sig, func) in bug_info[targ]:
            if bug_sig == SC and targ not in SC_list and func is not None:
                SC_list.append(targ)
            if bug_sig == EL and targ not in EL_list and func is not None:
                EL_list.append(targ)
    return (SC_list, EL_list)


def parse_fuzz_log_EL(bug_sig, buf, sig_list):
    idx_sig = buf.find(sig_list[0])
    if idx_sig == -1:
        idx_sig = buf.find(sig_list[1])
        if idx_sig == -1:
            return None
        else:
            pattern = rf"\[(\d{{2}}):(\d{{2}}):(\d{{2}}):(\d{{2}})\] Tx#\d+ found {bug_sig} at \w+ \({sig_list[1]}\)"
            match = re.search(pattern, buf)
            if match:
                days, hours, minutes, seconds = match.group(1), match.group(2), match.group(3), match.group(4)
                found_time = int(days) * 86400 + int(hours) * 3600 + int(minutes) * 60 + int(seconds)
                if found_time == 0: return 1
                return found_time
            else:
                return None
    else:
        buf = buf[:idx_sig]
        idx_start = buf.rfind("[")
        idx_end = buf.rfind("]")
        assert(idx_start != -1 and idx_end != -1)
        # Python only supports datetime parsing, and not timedelta parsing.
        buf = buf[idx_start + 1 : idx_end]
        tokens = list(map(int, buf.strip().split(":")))
        sec = tokens[0] * 86400 + tokens[1] * 3600 + tokens[2] * 60 + tokens[3]
        if sec == 0: return 1
        return sec

def analyze_targ(bug_list, result_dir, name, iter, time_map):
    targ = '%s-%d' % (name, iter)
    buf = read_log_file(result_dir, targ)
    found_times = {}
    found_times[SC] = []
    found_times[EL] = []
    for (bug_sig, func) in bug_list:
        if func is not None and "fallback" in func:
            alarm_sig_list = ["%s at %s" % (bug_sig, "fallback")]
            alarm_sig_list.append("(%s)" % ("fallback"))
            found_time = parse_fuzz_log_EL(bug_sig, buf, alarm_sig_list)
            if not (found_time is not None and found_time != 0):
                alarm_sig_list = ["%s at %s" % (bug_sig, func)]
                alarm_sig_list.append("(%s)" % (func))
                found_time = parse_fuzz_log_EL(bug_sig, buf, alarm_sig_list)
        else:
            alarm_sig_list = ["%s at %s" % (bug_sig, func)]
            alarm_sig_list.append("(%s)" % (func))
            found_time = parse_fuzz_log_EL(bug_sig, buf, alarm_sig_list)
        if found_time is not None:
            found_times[bug_sig].append([func, found_time])
    if found_times[SC] != []:
        time_map[(name, SC)] = found_times[SC]
    if found_times[EL] != []:
        time_map[(name, EL)] = found_times[EL]
    return time_map

def analyze_dir(bug_info, targ_dir, iter, time_map):
    target_name = targ_dir.split('/')[-2] if targ_dir.endswith('/') else targ_dir.split('/')[-1]
    bug_list = bug_info[target_name]
    analyze_targ(bug_list, targ_dir, target_name, iter, time_map)

def print_found_time(bug_sig, targ_list, time_map_list, bug_info):
    iter_cnt = len(time_map_list)
    for targ in targ_list:
        found_times = collect_found_times(bug_sig, time_map_list, targ)
        func_list = bug_info[targ]
        func_list = {func: [] for (sig, func) in func_list if bug_sig == sig and func is not None}
        for found_time in found_times:
            for (func, time) in found_time:
                if func not in func_list: func_list[func] = [time]
                else: func_list[func].append(time)
        
        for func in func_list:
            found_times = func_list[func]
            if len(found_times) == 0:
                print("Never found %s from %s ( %s )" % (bug_sig, targ, func))
            elif len(found_times) == iter_cnt:
                sec = ", ".join(map(str, found_times))
                print("Fully found %s from %s ( %s ): [%s] sec" % (bug_sig, targ, func, sec))
            else:
                sec = ", ".join(map(str, found_times))
                print("Partly found %s from %s ( %s ): [%s] sec" % (bug_sig, targ, func, sec))

def main():
    if len(sys.argv) < 2:
        print("Usage: %s [result dirs ...]" % sys.argv[0])
        exit(1)

    bug_info = init_elsc_bug_info(SC, EL)
    target_dirs = sys.argv[1:]
    # iter_cnt = 30
    iter_cnt = len(os.listdir(target_dirs[0]))
    target_dirs.sort()

    time_map_list = []
    for iter in range(1, iter_cnt + 1):
        time_map = {}
        for targ_dir in target_dirs:
            analyze_dir(bug_info, targ_dir, iter, time_map)
        time_map_list.append(time_map)

    targ_list = [ (targ_dir.split('/')[-2] 
                if targ_dir.endswith('/') else targ_dir.split('/')[-1]) 
                for targ_dir in target_dirs ]

    SC_list, EL_list = classify_targets(bug_info, targ_list)
    print_found_time(SC, SC_list, time_map_list, bug_info)
    print("===================================")
    plot_count_over_time(SC, time_map_list)
    print("===================================")
    print_found_time(EL, EL_list, time_map_list, bug_info)
    print("===================================")
    plot_count_over_time(EL, time_map_list)
    print("===================================")

if __name__ == "__main__":
    main()
