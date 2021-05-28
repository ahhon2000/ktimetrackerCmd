
import re
import argparse
from EasyPipe import Pipe
from Task import Task

QDBUS_CMD_BASE = "qdbus org.kde.ktimetracker /KTimeTracker".split()

class KTTCmd:
    def __init__(self, cmdopts):
        self._parseCmdOpts(cmdopts)

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
