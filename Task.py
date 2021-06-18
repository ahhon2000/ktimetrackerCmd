from Date import Date
from History import History

class Task:
    def __init__(self, ktt, nameOrId):
        if not nameOrId: raise Exception('either name or id must be given')
        self.ktt = ktt

        ns = ktt.getTaskNames()
        if nameOrId in ns:
            self.name = nameOrId
            self.ide = self.retrieveId(self.name)
        else:
            self.name = None
            self.ide = nameOrId
            for n in ns:
                p = ktt.runRawCmd('taskIdsFromName', n)
                ides = list(
                    filter(
                        bool,
                        map(
                            lambda l: l.strip(),
                            p.stdout.split("\n")
                        )
                    )
                )
                if self.ide in ides:
                    self.name = n
                    break

            if self.name is None: raise Exception(f"`{nameOrId}' is neither a task name nor a task id")


    def isActive(self):
        ktt = self.ktt
        p = ktt.runRawCmd('isActive', self.ide)
        
        st = p.stdout.strip().lower()
        if st == 'false': return False
        elif st == 'true': return True

        raise Exception('unsupported status message: {st}')

    def retrieveId(self, s):
        if not isinstance(s, str): raise Exception('string expected')
        ktt = self.ktt
        p = ktt.runRawCmd('taskIdsFromName', s)

        ids = list(filter(
            bool,
            map(lambda l: l.strip(), p.stdout.split("\n")),
        ))
        if len(ids) == 0:
            raise Exception(f'no ids found for task "{s}"')
        elif len(ids) > 1:
            raise Exception(f"more than one ids for '{s}' exist:\n{ids}")

        return ids[0]

    def start(self):
        ktt = self.ktt
        p = ktt.runRawCmd('startTimerFor', self.ide)

    def stop(self):
        ktt = self.ktt
        p = ktt.runRawCmd('stopTimerFor', self.ide)

    def getTotalHours(self):
        ktt = self.ktt
        p = ktt.runRawCmd('totalMinutesForTaskId', self.ide)
        return float(p.stdout.split("\n")[0]) / 60
