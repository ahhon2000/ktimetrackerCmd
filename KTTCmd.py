
import sys, os
import re
import argparse
import time
import subprocess
from collections import defaultdict
from pathlib import Path

from EasyPipe import Pipe
from Task import Task
from History import History
from CalFile import CalFile

SERVICE_NAME = "org.kde.ktimetracker"
QDBUS_CMD_BASE = f"qdbus {SERVICE_NAME} /KTimeTracker".split()
HOME = Path(os.environ.get('HOME'))
CALENDAR_FILE = HOME / '.local/share/ktimetracker/ktimetracker.ics'

CMDS_TO_FUNCS = {
    ('version',): '_execVersion',
    ('start',): '_execStart',
    ('stop',): '_execStop',
    ('id', 'taskid', 'getid', 'getId', 'getTaskId'): '_execGetId',
    ('tasks', 'status', 'st'): '_execStatus',
    ('hist', 'history', 'rep', 'report'): '_execHistory',
    ('csv', 'CSV',): '_execCSV',
    ('help',): '_execHelp',
    ('raw',): '_execRaw',
    ('quit', 'exit',): '_execQuit',
}
CMDS_TO_FUNCS = {
    c: f
        for cs, f in CMDS_TO_FUNCS.items()
            for c in cs
}

class KTTCmd:
    def __init__(self, cmdopts):
        self.calFile = CalFile(self, CALENDAR_FILE)
        self._checkConnection()
        self._parseCmdOpts(cmdopts)

    def _checkConnection(self):
        for i in range(2):
            p = Pipe(["qdbus"])
            if p.status: raise Exception(f"the `qdbus' command exited with code={p.status}")
            if p.stdout.find(SERVICE_NAME) >= 0: return
            else:
                if not os.fork():
                    subprocess.Popen(['ktimetracker'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        cwd = '/tmp',
                    )
                    sys.exit(0)
                time.sleep(1)


        raise Exception(f"KTimeTracker isn't running; an attempt to start it has failed")


    def _parseCmdOpts(self, cmdopts):
        cmdopts = list(cmdopts)
        argp = argparse.ArgumentParser()

        argp.add_argument("arguments", nargs='*')

        self.commandLineOpts = argp.parse_args(cmdopts)

    def getTaskNames(self):
        return list(
            filter(
                bool,
                map(
                    lambda l: l.strip(),
                    self.runRawCmd('tasks').stdout.split("\n"),
                )
            )
        )

    def getTasks(self, names=[]):
        if not names:
            names = self.getTaskNames()

        ts = []
        for n in names:
            t = Task(self, n)
            ts.append(t)

        return ts

    def _execVersion(self, args):
        self.runRawCmd('version', output=True)

    def _execStart(self, args):
        if len(args) != 2: raise Exception('wrong # of args')
        t = Task(self, args[1])
        t.start()
        self._execStatus(())

    def _execStop(self, args):
        if len(args) == 2:
            t = Task(self, args[1])
            t.stop()
        elif len(args) == 1:
            self.runRawCmd('stopAllTimersDBUS')
        else: raise Exception('wrong # of args')

        self._execStatus(())

    def _execGetId(self, args):
        if len(args) < 2: raise Exception('wrong # of args')
        for t in self.getTasks(args[1:]):
            print(f'{t.name}: {t.ide}')

    def _execStatus(self, args):
        for t in self.getTasks(args[1:]):
            hrsFld = f'{"*" if t.isActive() else ""}{t.getTotalHours():.2f}'.rjust(6)
            print(f"""
{t.ide}  {t.name:10s}  {hrsFld} h
"""[1:-1])

    def _execHistory(self, args):
        hi = History(self, *(args[1:]))
        print(hi)

    def _execCSV(self, args):
        hi = History(self, *(args[1:]))
        print(hi.getCSV())

    def _execHelp(self, args):
        self.runRawCmd(output=True)

    def _execRaw(self, args):
        self.runRawCmd(*(args[1:]), output=True)

    def _execQuit(self, args):
        self.runRawCmd('quit', output=True)

    def execCmd(self, args=[]):
        if not args:
            args = self.commandLineOpts.arguments
        if not args:
            args = ['status']

        cmd = args[0]

        if cmd not in CMDS_TO_FUNCS: raise Exception('unsupported command')
        f = getattr(self, CMDS_TO_FUNCS.get(cmd))
        f(args)


    def runRawCmd(self, *parg, stopOnError=True, output=False):
        parg = QDBUS_CMD_BASE + list(parg)
        p = Pipe(parg)
        if stopOnError and p.status:
            raise Exception(f"the command line interface returned an exit code={p.status}\n{p.stderr}")

        if output:
            if re.search(r'[^\s]', p.stdout):
                print(p.stdout.rstrip())

        return p
