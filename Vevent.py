import re

from Date import Date

class Vevent:
    def __init__(self, ls):
        self.dStart, self.dEnd = None, None
        self.relatedTo = ''
        extractDate = lambda l: Date(re.sub(r'.*(\b[0-9TZ]+)\s*$', r'\1', l))
        for l in ls:
            if re.search(r'^\s*DTSTART\b', l):
                self.dStart = extractDate(l)
            elif re.search(r'^\s*DTEND\b', l): 
                self.dEnd = extractDate(l)
            elif re.search(r'\s*RELATED-TO\b', l):
                self.relatedTo = re.sub(r'.*:\s*([^\s]+)\s*$', r'\1', l)
