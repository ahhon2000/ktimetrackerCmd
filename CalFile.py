from collections import defaultdict
import re
from Vevent import Vevent

class CalFile:
    def __init__(self, ktt, path):
        self.ktt = ktt
        self.path = path

    def loadLines(self):
        path = self.path
        if not path.exists(): raise Exception(f"could not find the calendar file: {path}")

        txt = path.read_text()
        ls = txt.split("\n")
        if ls and not ls[-1]: ls.pop()

        return ls

    def getVevents(self):
        ls = self.loadLines()

        vs = []

        vevBuf, inEvent = None, False
        for l in ls:
            if re.search(r'^\s*BEGIN:VEVENT\s*$', l, flags=re.IGNORECASE):
                vevBuf, inEvent = [], True
            elif re.search(r'^\s*END:VEVENT\s*$', l, flags=re.IGNORECASE):
                vs.append(Vevent(vevBuf))
                vevBuf, inEvent = None, False
            elif inEvent:
                vevBuf.append(l)

        vsdic = defaultdict(list)
        for v in vs:
            if not v.relatedTo: continue
            vsdic[v.relatedTo].append(v)

        for vs in vsdic.values():
            vs.sort(key = lambda v: v.dStart.toText() if v.dStart else '')
                
        return vsdic
