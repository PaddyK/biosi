.. EMG-Visualization-Project documentation Materials and Method file.
   Gives an overview over used technologies such as numpy, IPython notebook

*********************
Materials and Methods
*********************
This chapter introduces technologies used in the scope of this project. For more
details refer to the respective official documentations.

======
Pandas
======
Pandas is a python library for data analysis. Pandas primarly provides simple to
use and efficient data structures and is intended to use in conjunction with
other libraries providing, for example modeling functionality.
todo:: Describe how exactly Pandas is used in context of this project

================
IPython Notebook
================
IPython Notebook as part of IPython providing a rich architecture for
interactive computing. As the name suggests, IPython focuses on Python as
language. The architecture of IPython, however, is designed such that support
of other languages such as Haskell or R is possible. For the remainder of this
document python is meant if referred to code or programming.

IPython Notebook is a web-based, interactive compuational environment and
allows the combination of source code, and other components such as rich text
and rich media.

A notebook consists of different types of executable cells:
* Code cells
* Markdown cells
* Raw cells
* Heading cells

**Code** cells are the default type and intended to hold program code. There are no
limitations to what can be written inside, everything that would work in a
regular python script works here as well. If a code cell is executed, the
contained program code is evaluated and the result shown below the cell.

**Markdown Cells** contain text in the markdown format, it is also possible to
include LaTeX with the standard latex `$$` notation. If a Markdown cell is
executed, the content is parsed and displayed.

**Raw Cells** are not executed, or expressing it differently, the output is
exactly the same as the input.

**Heading Cells** are also rendered to rich text and used to give some
structure to the notebook. There are six different headings.

A notebook is thus a completely new way of "programming". Consider a usual
python (or R or octave or whatever) script. One would have a source file
containing all the program code and possibly some comments. Each time a new
part is added, the whole script has to be evaluated which might be time
consuming depending on the task. Descriptions and documentation to what the
program does exist in separate files.

With a notebook it is possible to have all this in one place. To a task or
snipped of code a markdown cell can be written describing what the cell does,
even if the description contains tricky formulas. Cells can be executed
independently of each other and the result of the computation is immediatly
visible.

