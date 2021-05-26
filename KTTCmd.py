
import re
import argparse
from EasyPipe import Pipe

QDBUS_CMD_BASE = "qdbus org.kde.ktimetracker /KTimeTracker".split()

class KTTCmd:
    def __init__(self, cmdopts):
        self._parseCmdOpts(cmdopts)

    def _parseCmdOpts(self, cmdopts):
        cmdopts = list(cmdopts)
        argp = argparse.ArgumentParser()

        argp.add_argument("arguments", nargs='*')

        self.commandLineOpts = argp.parse_args(cmdopts)

    def execCmd(self, args=[]):
        if not args:
            args = self.commandLineOpts.arguments
        if not args: raise Exception('no command given')
        cmd = args[0]
        parg = list(QDBUS_CMD_BASE)   # arguments for Pipe

        flgAlreadyProcessed = False

        if cmd in ('version',):
            parg.append(cmd)
        elif cmd in ('start', 'stop'):
            if len(args) != 2: raise Exception('wrong # of args')
            taskId = self.getTaskId(args[1])
            parg.append(
                {
                    'start': 'startTimerFor',
                    'stop': 'stopTimerFor',
                }[cmd]
            )
            parg.append(taskId)
        elif cmd in ('id', 'taskid', 'getid', 'getId', 'getTaskId'):
            if len(args) < 2: raise Exception('1 argument is missing')
            parg += ['taskIdsFromName', args[1]]
        elif cmd in ('status', 'st'):
            if len(args) < 2: raise Exception('task name missing')
            parg += ['isActive', self.getTaskId(args[1])]
            p = Pipe(parg)
            flgAlreadyProcessed = True
            if p.status: raise Exception(f'failed to retrieve the status of {args[1]}')
            st = p.stdout.strip().lower()
            if st == 'false': print('not running')
            elif st == 'true': print('running')
            else: raise Exception('unsupported status message: {st}')
        elif cmd in ('help',):
            pass
        else: raise Exception('unsupported command')

        if flgAlreadyProcessed: return

        p = Pipe(parg)
        if p.status:
            raise Exception(f"The tracker does not seem to be running (exit code={p.status})\n{p.stderr}")

        if re.search(r'[^\s]', p.stdout):
            print(p.stdout.rstrip())

    def getTaskId(self, s):
        if not isinstance(s, str): raise Exception('string expected')
        p = Pipe(QDBUS_CMD_BASE + ['taskIdsFromName', s])
        if p.status: raise Exception(f'could not retrieve the task id for "{s}" (exit code={p.status})')

        ids = list(filter(
            bool,
            map(lambda l: l.strip(), p.stdout.split("\n")),
        ))
        if len(ids) == 0:
            raise Exception(f'no ids found for task "{s}"')
        elif len(ids) > 1:
            raise Exception(f"more than one ids for '{s}' exist:\n{ids}")

        return ids[0]
