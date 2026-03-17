import os
import queue
import subprocess
import sys
import threading
import time
from subprocess import PIPE

from common import BASE_DIR, BENCHMARK_DIR

IMAGE_NAME = "oracle-artifact"
MAX_INSTANCE_NUM = 60
AVAILABLE_BENCHMARKS = ["B-ELSC"]
SUPPORTED_TOOLS = ["Smartian", "Smartian-SmarTest", "Smartian-rlf" "SmarTest", "rlf", "SmarTest-Smartian", "rlf-Smartian"]
WORKQUEUE = queue.Queue()
lock = threading.Lock()


def run_cmd(cmd_str, check=True):
    print("[*] Executing command '%s'" % cmd_str)
    args = cmd_str.split()
    try:
        p = subprocess.run(args, check=check, stdout=PIPE, stderr=PIPE)
        return p.stdout
    except Exception as e:
        print(e)
        exit(1)


def run_cmd_in_docker(container, cmd_str, check=True):
    print("[*] Executing '%s' in container %s" % (cmd_str, container))
    docker_prefix = "docker exec %s /bin/bash -c" % container
    args = docker_prefix.split() + [cmd_str]
    try:
        p = subprocess.run(args, stdout=PIPE, stderr=PIPE)
        return p.stdout
    except Exception as e:
        print(e)
        exit(1)


def check_cpu_count():
    n_str = run_cmd("nproc")
    try:
        if int(n_str) < MAX_INSTANCE_NUM:
            print("Not enough CPU cores, please decrease MAX_INSTANCE_NUM")
            exit(1)
    except Exception as e:
        print(e)
        print("Failed to count the number of CPU cores, abort")
        exit(1)

def decide_outpath(outdir, target):
    i = 0
    while True:
        i += 1
        outpath = os.path.join(outdir, target[0], "%s-%d" % (target[0], i))
        if not os.path.exists(outpath): return outpath

def make_targdir(outdir, targets):
    for target in targets:
        targdir = os.path.join(outdir, target[0])
        os.makedirs(targdir)

def get_ELSC_target_bug(target, tool):
    csv_path = os.path.join(BENCHMARK_DIR, "assets", "B-ELSC-bug.csv")

    with open(csv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue

            parts = line.split(',')
            if target != parts[0]: continue

            sc, el = line.split(',')[2].strip(), line.split(',')[3].strip()

            sc = '' if sc == '-' else sc
            el = '' if el == '-' else el

            if "smartian" in tool:
                sc = f"SC:{sc}" if sc else ''
                el = f"EL:{el}" if el else ''

            elif "SmarTest" in tool:
                sc = f"KA:{sc}" if sc else ''
                el = f"ETH_LEAK:{el}" if el else ''

            if not sc and not el:
                return ''

            separator = ',' if sc and el else ''
            prefix = '-b ' if "smartian" in tool else 'leak kill -target_bug "'
            return f'{prefix}{sc}{separator}{el}'

def get_targets(benchmark):
    list_name = benchmark + ".list"
    list_path = os.path.join(BENCHMARK_DIR, "assets", list_name)
    f = open(list_path, "r")
    targets = []
    for line in f:
        line = line.strip()
        if line != "":
            line = line.split(',')
            targets.append(line)
    f.close()
    return targets

def fetch_works(targets):
    works = []
    for i in range(MAX_INSTANCE_NUM):
        if len(targets) <= 0:
            break
        works.append(targets.pop(0))
    return works

def spawn_container(target, cpu_idx):
    container = target[0] + "-" + str(cpu_idx)
    cmd = "docker run --rm -m=6g --cpuset-cpus=%d -it -d --name %s %s" % \
            (cpu_idx, container, IMAGE_NAME)
    run_cmd(cmd)

def run_fuzzing(benchmark, target, tool, timelimit, opt, cpu_idx):
    targ, name = target
    src = "/home/test/benchmarks/%s/sol/%s.sol" % (benchmark, targ)
    bin = "/home/test/benchmarks/%s/bin/%s.bin" % (benchmark, targ)
    abi = "/home/test/benchmarks/%s/abi/%s.abi" % (benchmark, targ)
    if benchmark == "B-ELSC" and tool in ["smartian", "IConFuzz", "SmarTest"]:
        opt = opt + " " + str(get_ELSC_target_bug(targ,tool))
    args = "%s %d %s %s %s %s '%s'" % (tool, timelimit, src, bin, abi, name, opt)
    if "SmarTest" in tool:
        script = "/home/test/scripts/run_SmarTest.sh"
    elif "smartian" in tool:
        script = "/home/test/scripts/run_smartian.sh"
    elif "rlf" in tool:
        script = "/home/test/scripts/run_rlf.sh"
    cmd = "%s %s" % (script, args)
    container = targ + "-" + str(cpu_idx)
    run_cmd_in_docker(container, cmd)

def store_outputs(target, outdir, cpu_idx):
    targ, _ = target
    cmd = "docker cp %s:/home/test/output %s" % (targ + "-" + str(cpu_idx), outdir)
    run_cmd(cmd)

def cleanup_container(target, cpu_idx):
    targ = target[0]+"-"+str(cpu_idx)
    cmd = "docker kill %s" % targ
    run_cmd(cmd)

def worker(cpu_idx, benchmark, tool, timelimit, outdir, opt):
    while not WORKQUEUE.empty():
        with lock:
            try:
                target = WORKQUEUE.get(block=False)
            except queue.Empty:
                break
        spawn_container(target, cpu_idx)
        run_fuzzing(benchmark, target, tool, timelimit, opt, cpu_idx)
        with lock:
            store_outputs(target, decide_outpath(outdir, target), cpu_idx)
        cleanup_container(target, cpu_idx)
        time.sleep(2)

def main():
    if len(sys.argv) != 7 and len(sys.argv) != 8:
        print("Usage: %s <benchmark> <tool> <timelimit> <iterate> <outdir> <exp_name>" % \
              sys.argv[0])
        exit(1)

    benchmark = sys.argv[1]
    tool = sys.argv[2]
    timelimit = int(sys.argv[3])
    iterate = int(sys.argv[4])
    outdir_base = sys.argv[5]
    exp_name = sys.argv[6]
    outdir = os.path.join(BASE_DIR, outdir_base, exp_name)
    opt = sys.argv[7] if len(sys.argv) == 8 else ""

    if os.path.exists(os.path.join(outdir, tool)):
        print("%s exists, please remove it." % os.path.join(outdir, tool))
        exit(1)

    check_cpu_count()
    if benchmark not in AVAILABLE_BENCHMARKS:
        print("Unavailable benchmark: %s" % benchmark)
        exit(1)
    if tool not in SUPPORTED_TOOLS:
        print("Unsupported tool: %s" % tool)
        exit(1)

    os.makedirs(outdir, exist_ok=True)
    outdir = os.path.join(outdir, benchmark + opt.replace("-a ", "_")) if "-a " in opt \
            else os.path.join(outdir, tool)
    os.makedirs(outdir)
    make_targdir(outdir, get_targets(benchmark))

    targets = []
    for i in range(iterate): targets += get_targets(benchmark)
    for target in targets: WORKQUEUE.put(target)

    active_threads = []
    for i in range(MAX_INSTANCE_NUM):
        thread = threading.Thread(target=worker, args=(i, benchmark, tool, timelimit, outdir, opt))
        thread.start()
        active_threads.append(thread)

    for thread in active_threads:
        thread.join()

if __name__ == "__main__":
    main()
