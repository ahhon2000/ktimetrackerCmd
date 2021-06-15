import os
import random
from pathlib import Path

class History:
    def __init__(self, ktt):
        self.ktt = ktt

        pid = os.getpid()
        rnd = random.randint(1,1000000)
        f = Path(f"/tmp/.ktt.report.csv.{pid}.{rnd}")

        dFrom = '2021-05-01'
        dTo = '2021-06-15'
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
