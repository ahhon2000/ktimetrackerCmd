
import sys, os
import re
import argparse
import time
import subprocess

from EasyPipe import Pipe
from Task import Task
from History import History

SERVICE_NAME = "org.kde.ktimetracker"
QDBUS_CMD_BASE = f"qdbus {SERVICE_NAME} /KTimeTracker".split()

class KTTCmd:
    def __init__(self, cmdopts):
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

    def execCmd(self, args=[]):
        if not args:
            args = self.commandLineOpts.arguments
        if not args:
            args = ['status']

        cmd = args[0]

        if cmd in ('version',):
            self.runRawCmd('version', output=True)
        elif cmd in ('start', 'stop'):
            if len(args) != 2: raise Exception('wrong # of args')
            t = Task(self, args[1])
            if cmd == 'start': t.start()
            elif cmd == 'stop': t.stop()
        elif cmd in ('id', 'taskid', 'getid', 'getId', 'getTaskId'):
            if len(args) < 2: raise Exception('wrong # of args')
            for t in self.getTasks(args[1:]):
                print(f'{t.name}: {t.ide}')
        elif cmd in ('tasks', 'status', 'st'):
            for t in self.getTasks(args[1:]):
                hrsFld = f'{"*" if t.isActive() else ""}{t.getTotalHours():.2f}'.rjust(6)
                print(f"""
{t.ide}  {t.name:10s}  {hrsFld} h
"""[1:-1])
        elif cmd in ('hist', 'history', 'rep', 'report'):
            hi = History(self, *(args[1:]))
            print(hi)
        elif cmd in ('help',):
            self.runRawCmd(output=True)
        elif cmd in ('raw',):
            self.runRawCmd(*(args[1:]), output=True)
        elif cmd in ('quit', 'exit'):
            self.runRawCmd('quit', output=True)
        else: raise Exception('unsupported command')


    def runRawCmd(self, *parg, stopOnError=True, output=False):
        parg = QDBUS_CMD_BASE + list(parg)
        p = Pipe(parg)
        if stopOnError and p.status:
            raise Exception(f"the command line interface returned an exit code={p.status}\n{p.stderr}")

        if output:
            if re.search(r'[^\s]', p.stdout):
                print(p.stdout.rstrip())

        return p
