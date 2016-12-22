"""
Main module: starts CLI version of Jd2chm.
"""

import sys
import os
import getopt
import re

import utils
import const
import core
import console


def usage():
    """Display Usage."""
    console.set_bright_color()
    print(const.USAGE)
    console.set_color()


def lic():
    """Display License."""
    console.set_color(console.FOREGROUND_YELLOW)
    utils.print_center_block(const.MIT_LICENSE, 70)
    console.set_color()


def thanks():
    """Display thank you message."""
    console.set_color(console.FOREGROUND_GREEN)
    utils.print_center_block(const.MSG_THANKS)
    console.set_color()


@console.style(console.FOREGROUND_GREEN)
def welcome():
    """Display welcome message."""
    utils.print_center_block(const.MSG_WELCOME % const.VERSION)


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
    index_html = os.path.join(javadoc_dir, const.INDEX_HTML)
    if not os.path.exists(index_html):
        console.set_bright_color(console.FOREGROUND_RED)
        print(const.NOT_JAVADOC_DIR_MESSAGE % (javadoc_dir, index_html))
        console.set_color()
        return None
    return index_html


def main():
    welcome()

    # Arguments processing
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hclvd:p:t:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    project_name = None
    project_title = None
    start_dir = os.getcwd()
    javadoc_dir = '.'
    logging = utils.get_logging(const.LOG_LEVEL)
    log = logging.logger

    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit()
        if o == "-c":  # Check HHC compiler
            env = core.ChmEnv()
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
        if o == "-v": # verbose (debug = level)
            logging.set_level(logging.DEBUG)

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
    env = core.ChmEnv()
    env.prepare_env(project_name, javadoc_dir)

    # Create HTML help files
    project = core.ChmProject()
    project.create_project(project_name, project_title)

    # Generate the CHM and clean-up
    env.make()

    # End
    log.info('Compilation completed')
    os.chdir(start_dir)
    thanks()
