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
------
## Highlight Differences between .tex Files
See [this](https://tex.stackexchange.com/a/603351/149101) and [this](https://tex.stackexchange.com/a/603311/149101) answer on Tex.Stackexchange.
I could not make it work for changes before ```\begin{document}``` such as an ```\abstract environment```. 
* Open a new Overleaf project and upload both tex files. I will call them ```old.tex``` and ```new.tex```. 
* Make a new .tex file called ```diff.tex``` with the following contents"
    ```
    \RequirePackage{shellesc}
    \ShellEscape{latexdiff old.tex new.tex > diff_result.tex}
    \input{diff_result}
    \documentclass{dummy}
    ```
* Make sure to have ```diff.tex``` selected and compile for the highlighted PDF!
* You can use the commands in the ```latexdiff``` packages as you would expect. [E.g.](https://www.researchgate.net/post/How-can-I-track-changes-in-LaTeX-especially-abstractenvironment)
    ```
    \RequirePackage{shellesc}
    \ShellEscape{latexdiff --math-markup=1 old.tex new.tex > diff_result.tex}
    \input{diff_result}
    \documentclass{dummy}
    ```
    for coarser highlighting off math expressions. You can also include changes in environments in the preamble — e.g. ```\abstract``` for some journal templates — using
    ```
    \RequirePackage{shellesc}
    \ShellEscape{latexdiff --append-textcmd="abstract" old.tex new.tex >  diff_result.tex}
    \input{diff_result}
    \documentclass{dummy}
    ```
    although I could not get the latter to work myself.