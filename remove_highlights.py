from fileinput import filename

def remove_single_comment(string, key, change = {}):

    key_word_length = len(key)

    index = string.find(key)

    if index == -1:
        return string, change, index
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

def remove_comments(string, key):
    index = 0
    new_string = string
    changes = {}
    while index != -1:
        new_string, new_change, index = remove_single_comment(new_string, key, changes)
        changes = changes | new_change
    return new_string, changes

file_name = input("\nEnter file to be modified (you can just press enter if it's 'main.tex')\n")
if file_name == '':
    file_name = 'main.tex'
print(f'\nModifying {file_name}\n')

initials = input("Enter initials to remove, separated by spaces:\n  E.g. ST RB HH\n\n").split()

print('\n')















print(list(
    get_highlights("ST", "\ST{dasd}{ad} asd \HH{das}{vc}vc")
))
