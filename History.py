import os
import random
from pathlib import Path
from Date import Date

class History:
    def __init__(self, ktt, dFrom=None, dTo=None):
        self.ktt = ktt

        if dTo and not dFrom: raise Exception(f'no dFrom')

        dn = Date('now')
        if not dFrom: dFrom = dn.midnight()
        if not dTo: dTo = dn.midnight()

        dFrom, dTo = (
            d and (d if isinstance(d, Date) else Date(d)).toNiceTextDateOnly()
                for d in (dFrom, dTo)
        )

        pid = os.getpid()
        rnd = random.randint(1,1000000)
        f = Path(f"/tmp/.ktt.report.csv.{pid}.{rnd}")

        typ = 1
        sep = ','
        quote = ''
        decimalMinutes = True
        allTasks = True

        p = ktt.runRawCmd(
            'exportCSVFile', str(f), dFrom, dTo,
            str(typ),
            '1' if decimalMinutes else '0',
            '1' if allTasks else '0',
            sep, quote,
        )
        cleanup = lambda: f.exists() and f.unlink()

        if p.status:
            cleanup()
            raise Exception(f"could not export CSV (code={p.status}):\n{p.stderr}")

        self.lines = ls = f.read_text().split("\n")
        if ls and not ls[-1]: ls.pop()
        cleanup()

    def __str__(self):
        return "\n".join(self.lines)
