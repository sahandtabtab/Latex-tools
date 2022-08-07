# Latex-tools
## Removing Highlights

### Description:
* Place the 'remove_highlights.exe' or the corresponding Python script into the directory containing the '.tex' file to be modified.

* Inputs:
    * file name: Name of the '.tex' file, e.g. ```'main.tex'```.
    * Initials of the commenters whose highlights you want removed, separated by spaces e.g. ```AB CD EF```.
* The code now looks for all occurances of the pattern 
    ```
    \<initial>{<text to be removed>}{<text to be kept>}
    ```
    for all initials given. The code ignores the occurances before ```\title``` in the tex document.
    
    E.g. for the above initials, the code looks for patterns  ```\AB{...}{...}```, ```\CD{...}{...}```, ```\EF{...}{...}``` occuring after ```\title```.
* The code then changes every ```\<initial>{<text to be removed>}{<text to be kept>}``` to ```<text to be kept>``` and overwrites the tex file.
* All changes are shown on the terminal screen and also saved in a '<file_name>.change_log.txt' file.