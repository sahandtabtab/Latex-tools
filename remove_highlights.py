# This file partly uses code from https://stackoverflow.com/a/10477490/13055043 by Eli Bendersky

import re

initials = input("Enter initials to remove, separated by spaces:\n").split()

pattern_string = ''
for initial in initials:
    pattern_string += fr'\\{initial}|'
pattern_string = pattern_string[:-1]

pattern = re.compile(pattern_string)

for i, line in enumerate(open('main.tex')):
    for match in re.finditer(pattern, line):
        print ('Found on line %s: %s' % (i+1, match.group()))