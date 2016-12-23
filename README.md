# jd2chm (Javadoc to CHM)

jd2chm is a Python application that creates a set of Microsoft Compiled HTML (CHM) project files from an existing Javadoc API documentation.

After generating the project files, it invokes the HTML Help compiler. The HTML Help Compiler is a prerequisite to generate the final CHM file.

`j2dchm` was tested with Python 3.5.2.

**Note**: `jd2chm` was initially created in 2001 and ended up targeting Python 2.2 and 2.3 in 2004. I decided to "brush" it again in order to make it compatible with Python 3 and to generate CHM files from recent Javadocs (i.e. Java 8 API).

## HTML Help Compiler

The HTML Help Compiler might already be installed on your Windows System. The presence of the HTML Help compiler can be tested with jd2chm with option `-c`.

The HTML Help Compiler is available at: https://msdn.microsoft.com/en-us/library/windows/desktop/ms669985(v=vs.85).aspx

## CHM Project Files

`jd2chm` creates the following HTML Help project files:

* HHP: HTML Help Project file
* HHC: HTML Help Contents file
* HHK: HTML Help Keywords file

## CHM File

A CHM generated with `jd2chm` will look similar to the following one (Groovy 2.5.0):

![jd2chm](https://s3.amazonaws.com/burgaud-download/jd2chm_groovy250.png)

## Usage of jd2chm

* Clone jd2chm:

```
> git clone https://github.com/andreburgaud/jd2chm.git
```

* In the newly created jd2chm directory, create a Python virtual environment:

```
> py -m venv ENV
```

* Activate the virtual environment:

```
> ENV\Scripts\activate
(ENV) >
```

* Install 3rd party libraries

```
(ENV) > pip install -r requirements.txt
```

* Execute `jd2chm` with `-h` option to ensure it works:

```
(ENV) > python jd2chm.py -h

                         jd2chm version 1.0.0b1
                 Copyright (c) 2001-2016 Andre Burgaud
                        http://www.burgaud.com/

Usage:

  jd2chm.py [ -h | -c | -l | [-p path] [-o output] [-t title] [-v] ]

  -h: Displays usage.
  -c: Checks if the HHC compiler is installed.
  -l: Displays license.
  -v: Verbose (displays debug information)
  -p path:   'path' is the directory containing a Javadoc
             documentation (default: current directory).
  -o output: base name of the CHM output file
             Ex.: -o 'product' will result in a CHM file named 'product.chm'.
  -t title:  Assign 'title' as the title of the project.

Notes:
- The user is prompted if the project name and document title are not
  provided at the command line. The default values are extracted from
  the Javadoc index.html (see examples below).
- The Javadoc directory is the directory containing the file index.html.

Examples:
jd2chm.py -p C:\beanshell\javadoc
  The user is prompted to possibly modify the default values for the
  project name and document title.

jd2chm.py -p C:\beanshell\javadoc -o bsh20b4 -t "Beanshell 2.0b4" -v

jd2chm.py -p C:\j2se\docs\api -o j2se142_02 -t "Java(TM) 2 SDK 1.4.2"

jd2chm.py -o jython21 -t "Jython 2.1"
  The Javadoc is assumed to be in the current directory.

jd2chm.py -o SWT30M7 -t "Standard Widget toolkit 3.0M7"
  The Javadoc is assumed to be in the current directory.
```

## Operating Systems

`jd2chm` is intended to run on Windows, nevertheless, the generated CHM files can be viewed on other OS (i.e. Linux and Mac OSX).
