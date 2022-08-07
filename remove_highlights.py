def split_after_title(text):
    title_index = text.find('\\title')
    return text[:title_index + 1], text[title_index + 1:] 

def remove_single_comment(string, key):

    key_word_length = len(key)

    index = string.find(key)

    if index == -1:
        return string, {}, index
    else:
        count = 0
        i = 0
        while (count != 0) | (i == 0):
            if string[index + key_word_length + i] == r'{':
                count += 1
            elif string[index + key_word_length + i] == r'}':
                count -= 1
            i += 1

        count = 0
        j = 0
        while (count != 0) | (j == 0):
            if string[index + key_word_length + i + j] == r'{':
                count += 1
            elif string[index + key_word_length + i + j] == r'}':
                count -= 1
            j += 1

        string_before_comment = string[:index]
        mid_string = string[index + key_word_length + i + 1: index + key_word_length + i + j - 1]
        string_after_comment = string[index + key_word_length + i + j:]
        new_string = string_before_comment + mid_string + string_after_comment

        change = {string[index:index + key_word_length + i + j]:mid_string}

        return new_string, change, index

def remove_comments(string, keys):
    index = 0
    split_string = split_after_title(string)
    text_before_title = split_string[0]
    new_string = split_string[1]
    changes = {}

    for key in keys:
        while index != -1:
            new_string, new_change, index = remove_single_comment(new_string, key)
            changes = changes | new_change
        index = 0
    return text_before_title + new_string, changes

file_name = input("\nEnter file to be modified (you can just press enter if it's 'main.tex')\n")
if file_name == '':
    file_name = 'main.tex'
print(f'\nModifying {file_name}\n')

initials = input("Enter initials to remove, separated by spaces:\n  E.g. ST RB HH\n\n").split()
key_words = ["\\" + f'{initial}' for initial in initials]

print('\n')

with open(file_name, "r") as text_file:
    text = text_file.read()
    new_text, changes = remove_comments(text, key_words)

print('Changes are:\n\n')
for old, new in changes.items():
    print(old + '\t====>\t' + new + '\n')

with open(file_name[:-4] + '_new' + '.tex', 'w') as new_file:
    new_file.write(new_text)

print('\n\nDone.')