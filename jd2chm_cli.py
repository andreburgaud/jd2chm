"""
Main module: starts CLI version of Jd2chm.
"""

import sys
import os
import getopt
import re

import jd2chm_utils
import jd2chm_const
import jd2chm_core
import lib_console as console


def usage():
    """Display Usage."""
    console.setBrightColor()
    print(jd2chm_const.USAGE)
    console.setColor()


def lic():
    """Display License."""
    console.setBrightColor(console.FOREGROUND_BLUE)
    print(jd2chm_const.MIT_LICENSE)
    console.setColor()


def thanks():
    """Display thank you message."""
    console.setBrightColor(console.FOREGROUND_BLUE)
    print(jd2chm_const.MSG_THANKS)
    console.setColor()


def welcome():
    """Display welcome message."""
    console.setBrightColor(console.FOREGROUND_GREEN)
    print(jd2chm_const.MSG_WELCOME % jd2chm_const.VERSION)
    console.setColor()


def get_title(index_html):
    """Extracts the default title from the root Javadoc index.html file."""
    title = 'Javadoc Title'
    re_title = re.compile(r'<title>\s*([^<]*)\s*</title>')
    fo = open(index_html)
    data = fo.read()
    fo.close()
    match = re_title.search(data)
    if match:
        title = match.group(1)
        title = title.strip()
    return title


def get_project_name(title):
    """Generate default title from the title."""
    name = title.lower()
    name = name.replace(' ', '_')
    name = name.replace('.', '-')
    return name


def get_index_html(javadoc_dir):
    """Checks and returns the index.html path."""
    # TODO: Check if directory exists and provide a different message (directory does not exist vs.
    # there is no index.html)
    index_html = os.path.join(javadoc_dir, jd2chm_const.INDEX_HTML)
    if not os.path.exists(index_html):
        console.setBrightColor(console.FOREGROUND_RED)
        print(jd2chm_const.NOT_JAVADOC_DIR_MESSAGE % (javadoc_dir, index_html))
        console.setColor()
        return None
    return index_html


def main():
    welcome()

    # Arguments processing
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcld:p:t:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    project_name = None
    project_title = None
    start_dir = os.getcwd()
    javadoc_dir = '.'
    log = jd2chm_utils.getLog()

    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit()
        if o == "-c":  # Check HHC compiler
            env = jd2chm_core.ChmEnv()
            hhc = env.get_html_compiler_path()
            log.info("HTML Help Compiler installed and found: %s" % hhc)
            sys.exit()
        if o == "-l":
            lic()
            sys.exit()
        if o == "-p":
            project_name = a
        if o == "-t":
            project_title = a
        if o == "-d":
            javadoc_dir = a

    index_html = get_index_html(javadoc_dir)
    if not index_html:
        sys.exit(1)

    if not project_title:
        try:
            title = get_title(index_html)
            print("The title will be assign to the CHM window")
            project_title = input("Enter the project title [%s]: " % title)
            if not project_title:
                project_title = title
        except KeyboardInterrupt:
            print()
            print('Bye!')
            sys.exit()

    if not project_name:
        try:
            name = get_project_name(project_title)
            project_name = input("Enter the project name [%s]: " % name)
            if not project_name:
                project_name = name
        except KeyboardInterrupt:
            print()
            print('Bye!')
            sys.exit()

    # End arguments processing
    log.info("Starts building the project")
    log.info("Project: %s" % project_name)
    log.info("Title: %s" % project_title)

    log.debug("javadoc_dir: {}".format(javadoc_dir))
    os.chdir(javadoc_dir)

    # Prepare Environment
    env = jd2chm_core.ChmEnv()
    env.prepare_env(project_name, javadoc_dir)

    # Create HTML help files
    project = jd2chm_core.ChmProject()
    project.create_project(project_name, project_title)

    # Generate the CHM and clean-up
    env.make()

    # End
    log.info('Compilation completed')
    os.chdir(start_dir)
    thanks()

