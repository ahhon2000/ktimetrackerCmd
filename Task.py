
class Task:
    def __init__(self, ktt, name="", ide=""):
        if not name  and  not ide: raise Exception('either name or ide arguments must be given')

        self.ktt = ktt
        if not ide:
            ide = self.retrieveId(name)

        self.name = name
        self.ide = ide

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
