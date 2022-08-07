# Requires the 'regex' or 're' module.
# This file partly uses code from https://stackoverflow.com/a/10477490/13055043 by Eli Bendersky.

from fileinput import filename
import regex as re

def get_highlights(commenter_initials, text):
    stuff=""
    count=0
    for char in text:
        if char== fr'\{commenter_initials}{{':
            count += 1
        if count > 0:
            stuff += char
        if char=="}":
            count -= 1
        if count == 0 and stuff != "":
            yield stuff
            stuff=""


file_name = input("\nEnter file to be modified (you can just press enter if it's 'main.tex')\n")
if file_name == '':
    file_name = 'main.tex'
print(f'\nModifying {file_name}\n')

initials = input("Enter initials to remove, separated by spaces:\n  E.g. ST RB HH\n\n").split()

print('\n')

print(list(
    get_highlights("ST", "\ST{dasd}{ad} asd \HH{das}{vc}vc")
))

# for i, line in enumerate(open(file_name)):
#     for comment in get_highlights(initials[0], line):
#         print(f'Line: {i}')
#         print(comment)


# pattern_string = ''
# for initial in initials:
#     pattern_string += fr'\\{initial}' + r'( \{ ( (?: [^}{]+ | (?1))*+ ) \} )'#+ r'\{([^}]+)\}|'
# pattern_string = pattern_string[:-1]

# pattern = re.compile(pattern_string)

# for i, line in enumerate(open(file_name)):
#     for match in re.finditer(pattern, line):
#         print(f'Line {i}:')
#         print(match.group())