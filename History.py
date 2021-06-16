import os
import random
from pathlib import Path
from Date import Date

class History:
    def __init__(self, ktt, dFrom=None, dTo=None):
        self.ktt = ktt

        if dTo and not dFrom: raise Exception(f'no dFrom')

        dn = Date('now')

        dFrom, dTo = (
            (
                d if isinstance(d, Date) else (
                    Date(d) if d else dn
                )
            ).midnight()
                for d in (dFrom, dTo)
        )
        self.dFrom, self.dTo = dFrom, dTo

        dFrom_t, dTo_t = (d.toNiceTextDateOnly() for d in (dFrom, dTo))

        pid = os.getpid()
        rnd = random.randint(1,1000000)
        f = Path(f"/tmp/.ktt.report.csv.{pid}.{rnd}")

        typ = 1
        sep = ','
        quote = ''
        decimalMinutes = True
        allTasks = True

        p = ktt.runRawCmd(
            'exportCSVFile', str(f), dFrom_t, dTo_t,
            str(typ),
            '1' if decimalMinutes else '0',
            '1' if allTasks else '0',
            sep, quote,
        )
        cleanup = lambda: f.exists() and f.unlink()

        if p.status:
            cleanup()
            raise Exception(f"could not export CSV (code={p.status}):\n{p.stderr}")

        self.CSVLines = ls = f.read_text().split("\n")
        cleanup()
        if ls and not ls[-1]: ls.pop()

        self._processCSVLines()

    def _processCSVLines(self):
        ls = self.CSVLines

        fss = [l.split(",") for l in ls]
        ds = list(map(lambda d: Date(d).toNiceTextDateOnly(), fss[0][1:]))
        ts = list(fs[0] for fs in fss[1:])

        self.dailyDict = ddic = {
            d: {
                t: float(fss[i][j])
                    for i, t in enumerate(ts, start=1)
            }
                for j, d in enumerate(ds, start=1)
        }

        self.lines = ls = []

        firstColWidth = 14
        colWidth = max(8, max((len(t) for t in ts), default=8))

        ls.append(" ".join(
            ["Date".ljust(firstColWidth)] + [
                f"{t}".rjust(colWidth) for t in sorted(ts)
            ]
        ))

        ls.extend([
            " ".join(
                [d.ljust(firstColWidth)] + [
                    f"{h:.2f}".rjust(colWidth)
                        for t, h in sorted(ddic[d].items())
                ]
            )
                for d in sorted(ds)
        ])

        ls.append("-" * len(ls[0]))
        ls.append(" ".join(
            ['Total'.ljust(firstColWidth)] + [
                f"{s:.2f}".rjust(colWidth) for s in map(
                    lambda t: sum(ddic[d][t] for d in ds),
                    sorted(ts),
                )
            ]
        ))


    def __str__(self):
        return "\n".join(self.lines)

    def getCSV(self):
        return "\n".join(self.CSVLines)
