import os, sys
import re
import json

OUTDIR = "/home/test/SmarTest-workspace/output"
BUGDIR = "/home/test/SmarTest-workspace/output/bugs"

def parse_disproven(line):
  pattern = r'\[\d+\] \[(\w+)\].*?line (\d+).*?\{(\w+)\}.*?(\d+\.\d+s)'
  matched = re.search(pattern, line)
  if matched:
    bug_type = matched.group(1)
    line_number = matched.group(2)
    func_name = matched.group(3)
    found_time = matched.group(4)
    found_time = str(round(float(found_time[:-1]),2))
    int_part, frac_part = found_time.split('.')
    days = int(int_part) // 86400
    hours = (int(int_part) % 86400) // 3600
    minutes = (int(int_part) % 3600) // 60
    seconds = int(int_part) % 60
    if days == 0 and hours == 0 and minutes == 0 and seconds == 0: seconds = 1
    return (bug_type, f'[{days:02}:{hours:02}:{minutes:02}:{seconds:02}]', line_number, func_name)
  else: return None

def mk_log_file():
  STDOUT = OUTDIR + "/stdout.txt"
  LOG = OUTDIR + "/log.txt"
  std = open(STDOUT, "r")
  log = open(LOG, "w")
  L = std.readlines()
  seq = []
  bugs = []
  i = 0; 
  while i < len(L):
    line = L[i].strip()
    if line != "":
      ret = parse_disproven(line)
      if ret is not None:
        bugs.append(ret)
        bug_type, _, l_num, _ = ret
        i += 1
        while L[i].strip() != "":
          seq.append(L[i])
          i += 1
        fname = ""
        if bug_type == "IO":
          fname = BUGDIR + f"/IO_line_{l_num}"
        elif bug_type == "KA":
          fname = BUGDIR + f"/KA_line_{l_num}"
        elif bug_type == "ETH_LEAK":
          fname = BUGDIR + f"/ETH_LEAK_line_{l_num}"
        with open(fname, "w") as f:
          for t in seq:
            f.write(t)
        seq.clear()
    i += 1
  bugs.sort()
  for bug_type, found_time, line_number, func_name in bugs:
    if bug_type == "IO":
      log.write(f'{found_time} Found IntegerBug at {line_number}\n')
    elif bug_type == "KA":
      log.write(f'{found_time} Found SuicidalContract at {func_name}\n')
    elif bug_type == "ETH_LEAK":
      log.write(f'{found_time} Found EtherLeak at {func_name}\n')
  log.close()
  std.close()
          
if __name__ == '__main__':
    mk_log_file()