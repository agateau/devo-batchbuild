import re
import subprocess
import sys
import time

from batchbuilderror import BatchBuildError


PERCENT_RX = re.compile(r"\[ *(\d+%)\]")


def format_duration(duration):
    hours, rest = divmod(duration, 3600)
    minutes, seconds = divmod(rest, 60)
    lst = []
    if hours > 0:
        lst.append("%dh" % hours)
    if minutes > 0 or hours > 0:
        lst.append("%dm" % minutes)
    lst.append("%ds" % seconds)
    return " ".join(lst)


def extract_progress(line):
    match = PERCENT_RX.search(line)
    if match:
        return match.group(1)
    else:
        return None


class Runner(object):
    def __init__(self, log_file, verbose):
        self.log_file = log_file
        self.verbose = verbose

    def run(self, cwd, command, env=None, report_progress=False):
        command = command.strip()
        stamp = time.strftime("%H:%M")
        msg = "%s %s" % (stamp, command)
        if self.verbose:
            print msg
        else:
            sys.stdout.write(msg)

        sys.stdout.flush()
        self.log_file.write("devo-batchbuild: %s\n" % command)
        self.log_file.flush()

        start_time = time.time()
        self.reported_progress = False
        try:
            process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            while True:
                out = process.stdout.readline()
                self._log_output(out, report_progress)
                process.poll()
                ret = process.returncode
                if ret is not None:
                    if ret != 0:
                        raise BatchBuildError("Command '%s' failed with exit code %d" % (command, ret))
                    else:
                        return
        finally:
            duration = time.time() - start_time
            txt = "took %s" % format_duration(duration)
            if self.verbose:
                print txt
            else:
                print " - " + txt

    def _log_output(self, out, report_progress):
        self.log_file.write(out)
        self.log_file.flush()

        if self.verbose:
            sys.stdout.write(out)
            sys.stdout.flush()
            return

        if not report_progress:
            return

        percent = extract_progress(out)
        if percent is None:
            return

        if not self.reported_progress:
            # Do not overwrite current line
            sys.stdout.write("\n")
            sys.stdout.flush()
            self.reported_progress = True
        sys.stdout.write("\r" + percent)
        sys.stdout.flush()
