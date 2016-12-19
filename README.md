# jd2chm (Javadoc to CHM)

jd2chm is a Python application that creates a set of Microsoft Compiled HTML (CHM) project files from an existing Javadoc API documentation.

After generating the project files, it invokes the HTML Help compiler. The HTML Help Compiler is a prerequisite to generate the final CHM file.

**Note**: `jd2chm` was initially created in 2001 and targeted Python 2.2 and 2.3. I decided to "brush" it again in order to make it compatible with Python 3 and to generate recent Java Documentation (i.e. Java 8).

## HTML Help Compiler

The HTML Help Compiler might already be installed on your Windows System. The presence of the HTML Help compiler can be tested with jd2chm with option `-c`:

```
> python jd2chm.py -c
```

The HTML Help Compiler is available at: https://msdn.microsoft.com/en-us/library/windows/desktop/ms669985(v=vs.85).aspx

## CHM Project Files

jd2chm creates the following HTML Help project files:

* HHP: HTML Help Project file
* HHC: HTML Help Contents file
* HHK: HTML Help Keywords file

## CHM File

A CHM generated with j2chm will look similar to the following one (Groovy 2.5.0):

![jd2chm](https://s3.amazonaws.com/burgaud-download/jd2chm_groovy250.png)

## Usage of jd2chm

1. Clone j2chm: `git clone https://github.com/andreburgaud/jd2chm.git
2. In the newly created j2chm directory, create a Python virtual environment:

```
> py -m venv ENV
```

3. Activate the virtual environment:

```
> ENV\Scripts\activate
(ENV) >
```

4. Install 3rd party library

```
(ENV) > pip install -r requirements.txt
```

5. Execute j2chm with `-h` option to ensure it works:

```
(ENV) >python jd2chm.py -h
Internal compiler not available

=====================================
        jd2chm Version 2.0b
Copyright (c) 2000-2006 Andre Burgaud
     http://www.burgaud.com/
=====================================

Usage:

  jd2chm.py [ -h | -c | -l | [-d dir] [-p project] [-t title] ]

  -h: Displays usage.
  -c: Checks if the HHC compiler is installed.
  -l: Displays license.
  -d dir: 'dir' is the directory containing a Javadoc
          documentation (default: current directory).
  -p name: the base name of the project files will be 'name'
           (project_name.hhp, project_name.chm...).
  -t title: Assign 'title' as the title of the project.

Notes:
- The user is prompted if the project name and document title are not
  provided at the command line. The default values are extracted from
  the Javadoc index.html (see examples below).
- The Javadoc directory is the directory containing the file index.html.

Examples:
jd2chm.py -d C:\beanshell\javadoc
  The user is prompted to possibly modify the default values for the
  project name and document title.

jd2chm.py -d C:\beanshell\javadoc -p bsh20b4 -t "Beanshell 2.0b4"

jd2chm.py -d C:\j2se\docs\api -p j2se142_02 -t "Java(TM) 2 SDK 1.4.2"

jd2chm.py -p jython21 -t "Jython 2.1"
  The Javadoc is assumed to be in the current directory.

jd2chm.py -p SWT30M7 -t "Standard Widget toolkit 3.0M7"
  The Javadoc is assumed to be in the current directory.
```

## Operating System

jd2chm is intended to run on Windows, nevertheless, the generated CHM files can be viewed on other OS (i.e. Linux and Mac OSX)
