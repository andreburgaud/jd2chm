"""jd2chm core engine. Processes Javadoc files, builds the project
files and initiate the hhc compilation."""

import sys
import re
import os
import shutil
import time
import tempfile
import urllib
import urllib.parse
import win32api
import win32con
import pywintypes

import jd2chm_const
import jd2chm_utils

try:
    import pyhhc
    EXTERNAL_COMPILER = 0
except ImportError:
    # TODO: Provide better information
    # Set compiler to external and check if external compiler available
    # Merge with information obtained in the configuration
    print("Internal compiler not available")
    EXTERNAL_COMPILER = 1


# ===============================================================================
# CLASSES
# ===============================================================================
class Hhp:
    """Creates the HTML Help Project file (HHP file)
    """

    def __init__(self, project_name, project_title, default_file):
        self.project_name = project_name
        self.project_title = project_title
        self.default_file = default_file
        self.log = jd2chm_utils.get_log()

    def create_hhp(self):
        hhp_file_name = self.project_name + ".hhp"
        self.hhp_file = open(hhp_file_name, 'w')

        # Create the project file: .HHP
        self.hhp_file.write(
            jd2chm_const.FORMAT_PROJECT % (self.project_name,  # chm name
                                           self.project_name,  # hhc name (contents)
                                           self.project_name,  # hhk name (index)
                                           self.default_file,  # default topic
                                           self.project_title,  # project title
                                           self.project_title,  # main wnd title
                                           self.project_name,  # hhc for wnd
                                           self.project_name,  # hhk for wnd
                                           self.default_file,  # default topic for wnd
                                           self.default_file)  # home topic for wnd
        )
        self.create_file_section()
        self.hhp_file.close()

    def create_file_section(self):
        """Parses the directory tree to collect the HTML files"""
        walktree(".", self.write_file_section)
        print()  # Carriage return after the dots...

    def write_file_section(self, html_file_path):
        """Writes only if '.html' files.
        Doesn't write the './' at the begining of the path"""
        if html_file_path[html_file_path.rfind('.'):] == '.html':
            self.hhp_file.write(html_file_path[2:] + '\n')


class Hhc:
    """Creates the contents file (HHC file)
    """

    def __init__(self, project_name, content_file, default_file):
        self.cpt = 0
        self.hhc_file_name = project_name + ".hhc"
        self.content_file = content_file
        self.default_file = default_file
        self.log = jd2chm_utils.get_log()
        # Regex to extract href and title for a book topic
        self.re_anchor_book = re.compile(r'^<li><a\shref="([^"]*)".*>(.*)</a></li>', re.I)
        # Regex to extract href, type (interface or class), title for a page topic
        # The attribute 'title' is new in Java 1.4 but for backward compatibility
        # is not used in the regexp
        # self.re_anchor_page = re.compile(r'^<A\s+HREF="([^"]*)"\s+title="(\w+)\s+.*">(?:<I>)?([^<]*)(?:</I>)?</A>')
        #self.re_anchor_page = re.compile(r'^<li><a\shref="(.*)"[^>]*>(:?<span> class="interfaceName")?(.*)(:?</span>)?</a>', re.I)
        # Capture 3 groups if interface. Group 1 = url to class/interface. Group 2 flags if interface. Group 3 = title.
        self.re_anchor_page = re.compile(r'^<li><a\shref="([^"]*)"[^<]*>([^>]*>)?([^>]*)(?:<\/span>)?<\/a><\/li>', re.I)
        # Regex to extract the url from the prefix "../"
        self.re_href = re.compile(r'(../)*(.*)')
        # Regex to extract inner class from class html file
        # self.re_inner = re.compile(r'<TD>.*<A\s+HREF="([^"]*)"\s+title="(\w+)\s+.*">([^<]*)</A></B></CODE>')
        self.re_inner = re.compile(r'<td>.*<a\s+href="([^"]*)"[^>]*>([^<]*)</a></b></code>', re.I)
        # Regex to extract methods from class html file
        self.re_method = re.compile(r'<td><code><b><a\s+href="([^"]*)">([^<]*)</a></b>(\([^)]*\))?</code>', re.I)
        # Regex to extract the type and the variable of an 'anchored' argument
        self.re_args = re.compile(r'<a\s+href=[^>]*>([^<]*)</a>(.*;.*)', re.I)

    def create_hhc(self):
        self.hhc_file = open(self.hhc_file_name, 'w')
        str_time = time.strftime("%B-%d-%Y", time.localtime(time.time()))
        self.hhc_file.write(jd2chm_const.FORMAT_TOC_HEADER % str_time)
        self.hhc_file.write('<ul>\n')
        if os.path.exists(self.default_file):
            title = "Overview"
            self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_CLASS_ITEM % (self.default_file, title))
        if os.path.exists(jd2chm_const.OVERVIEW_TREE):
            title = "Hierarchy For All Packages"
            self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_CLASS_ITEM % (jd2chm_const.OVERVIEW_TREE, title))
        if self.content_file == jd2chm_const.JDK_BOOK_FILE:
            # Content file is "overview-frame.html"
            self.create_packages(self.content_file)
        else:
            # Content file is "allclasses-frame.html"
            # self.hhc_file.write(jd2chm_const.FORMAT_ALLCLASSES_CONTENT_ITEM % self.default_file)
            self.hhc_file.write(jd2chm_const.FORMAT_ALLCLASSES_CONTENT_ITEM)
            html_class = "allclasses-frame.html"
            if os.path.exists(html_class):
                self.hhc_file.write('<ul>\n')
                self.create_classes('', html_class, "All Classes")
                self.hhc_file.write('</ul>\n')
        self.hhc_file.write('</ul>\n</body>\n</html>\n')
        self.hhc_file.close()

    def create_packages(self, html_file):
        """Parses overview-frame.html file"""
        self.log.debug(html_file)
        fd = open(html_file)
        lines = fd.readlines()
        fd.close()
        # href = None
        title = None
        html_class = ''
        html_package = ''
        for line in lines:
            res = self.re_anchor_book.search(line)
            if res:
                # href = res.group(1)
                title = res.group(2)
                if title != "All Classes":
                    # The book is associated with the package info (package-summary)
                    path = title.replace('.', '/')
                    html_package = "%s/package-summary.html" % path
                    html_class = "%s/package-frame.html" % path
                else:
                    # All Class: associated with default file
                    # Processes the allclass file only if there is no "overview-frame.html"
                    # Application with no package
                    # ~ if (self.content_file != jdk_book_file):
                    # ~ html_package = self.default_file
                    # ~ path = '' # Current path
                    # ~ html_class = "allclasses-frame.html" # file that will be parsed to generate content topics
                    # The TOC entry should point to the list of the class, not to the overview.
                    # html_package = self.default_file
                    html_package = "allclasses-noframe.html"
                    path = ''  # Current path
                    html_class = "allclasses-frame.html"  # file that will be parsed to generate content topics
                if os.path.exists(html_class):
                    self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_BOOK_ITEM % (title, html_package))
                    self.hhc_file.write('<ul>\n')
                    self.create_classes(path, html_class, title)
                    self.hhc_file.write('</ul>\n')

    def create_inners(self, html_class):
        fd = open(html_class)
        data = fd.read()
        fd.close()
        iteration = re.finditer(self.re_inner, data)
        if iteration:
            for match in iteration:
                href = match.group(1)
                title = match.group(2)
                try:
                    (clazz, inner) = title.split('.')
                except ValueError:
                    # This is a method (not an inner class or interface)
                    continue
                title = inner  # Keeps only the inner class name. Will be shown as a child of the class
                res = self.re_href.search(href)  # removes the prefix ../..
                if res:
                    href = res.group(2)
                self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_CLASS_ITEM % (href, title))
                if (os.path.exists(href)):
                    # We do not build the method level for the All Class book
                    self.hhc_file.write('<ul>\n')
                    self.create_methods(href)
                    self.hhc_file.write('</ul>\n')

    def create_classes(self, path, html_file, package_name):
        """Parses package-frame.html file"""
        package_tree_path = os.path.join(path, jd2chm_const.PACKAGE_TREE_HTML)
        if os.path.exists(package_tree_path):
            title = "Hierarchy For Package %s" % package_name
            self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_CLASS_ITEM % (package_tree_path, title))
        package_use_path = os.path.join(path, jd2chm_const.PACKAGE_USE)
        if os.path.exists(package_use_path):
            title = "Uses of Package %s" % package_name
            self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_CLASS_ITEM % (package_use_path, title))
        fo = open(html_file)
        lines = fo.readlines()
        fo.close()
        href = None
        title = None
        # type = None
        for line in lines:
            self.cpt = print_dot(self.cpt)
            res = self.re_anchor_page.match(line)
            if res:
                href = res.group(1)  # url
                if href.find(jd2chm_const.PACKAGE_SUMMARY) > 0:
                    # The package summary url is caught by the class regexp, skip
                    continue
                title = res.group(3)  # title
                interface = res.group(2)  # interface or class
                res = self.re_href.search(href)  # removes the prefix ../..
                if res:
                    href = res.group(2)
                    if path:
                        href = "%s/%s" % (path, href)
                if interface:
                    title = "%s (Interface)" % title
                # Inner class: Class.Inner
                # Inner class handled in the class. Skipped if public static, and
                # therefore visible in the package-frame file
                if title.find('.') == -1:
                    self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_CLASS_ITEM % (href, title))
                    if os.path.exists(href):
                        # We do not build the method level for the All Class book
                        self.hhc_file.write('<ul>\n')
                        self.create_inners(href)
                        self.create_methods(href)
                        self.hhc_file.write('</ul>\n')

    def create_methods(self, html_file):
        fo = open(html_file)
        data = fo.read()
        fo.close()
        iteration = re.finditer(self.re_method, data)
        arg = None
        for match in iteration:
            href = match.group(1)
            name = match.group(2)
            if name.find('.') > 0:
                # This is an inner class of interface, skip
                continue
            res = self.re_href.search(href)  # removes the prefix ../..
            if res:
                href = res.group(2)
            arg = match.group(3)
            if arg:  # This is a method
                # Remove parenthesis
                arg = arg[1:-1]
                # Split to process multiple parameter
                args = arg.split(',')
                new_args = []
                for arg in args:
                    # Remove leading and trailing whitespace(s)
                    new_arg = arg.strip()
                    # Process possible anchor
                    res = re.search(self.re_args, new_arg)
                    if res:
                        new_arg = "%s%s" % (res.group(1), res.group(2))
                    # Add to the clean list of parameter
                    new_args.append(new_arg)
                args = ''
                if len(new_args) == 1:
                    args = new_args[0]
                else:
                    args = ', '.join(new_args)
                name = "%s (%s)" % (name, args)
            self.hhc_file.write(jd2chm_const.FORMAT_CONTENT_METHOD_ITEM % (name, href))


class Hhk:
    """Creates the index file (format file_name.hhk)

    Parses all the file in the index-file directory or the unique index file
    in the main dir.
    Write an object bloc that includes href, title and class information.

    """

    def __init__(self, project_name):
        self.hhk_file_name = project_name + ".hhk"
        # Regexp to extract the href and title
        # First capture is the url, second is the entry in the index
        self.re_index = re.compile(r'<dt><span class=".*"><a href="(.*)">(.*)</a></span>', re.I)
        # Regexp to extract the Java class name
        self.re_class = re.compile(r'(.*).html')
        # Regexp to eliminate the "../.." prefix
        self.re_href = re.compile(r'(../)*(.*)')
        self.cpt = 0
        self.log = jd2chm_utils.get_log()

    def create_hhk(self):
        self.hhk_file = open(self.hhk_file_name, 'w')
        str_time = time.strftime("%B-%d-%Y", time.localtime(time.time()))
        self.hhk_file.write(jd2chm_const.FORMAT_INDEX_HEADER % str_time)
        self.hhk_file.write('<ul>\n')
        self.create_index()
        print()  # Add a CR after the dots
        self.hhk_file.write('</ul>\n</body>\n</html>\n')
        self.hhk_file.close()

    def create_index(self):
        if os.path.exists(jd2chm_const.INDEX_ALL):
            # Javadoc generated with one unique index file in the main dir
            self.parse_re_idxfile(jd2chm_const.INDEX_ALL)
        else:
            # Javadoc generated with splitted index files in the index dir
            for index_file in os.listdir(jd2chm_const.INDEX_DIR):
                index_file = '%s/%s' % (jd2chm_const.INDEX_DIR, index_file)
                self.parse_re_idxfile(index_file)

    @staticmethod
    def sanitize_title(title):
        """During the compilation, any keyword with more than 488 triggers and error from the CHM compiler:
        Warning: Keyword string: ... The maximum is 488 characters
        """
        if len(title) > jd2chm_const.MAX_SIZE_KEYWORD:
            return title[:jd2chm_const.MAX_SIZE_KEYWORD] + "..."
        return title

    def parse_re_idxfile(self, index_file):
        fo = open(index_file)
        data = fo.read()
        fo.close()
        iteration = re.finditer(self.re_index, data)
        self.kword = ''
        self.entries = []
        for match in iteration:
            self.cpt = print_dot(self.cpt)
            href = match.group(1)
            res_href = self.re_href.search(href)  # Removes the (../)* preceding the url
            if res_href:
                href = res_href.group(2)
            title = match.group(2)
            res_class = self.re_class.match(href)
            java_class = ''
            if res_class:
                java_class = res_class.group(1)
                java_class = java_class.replace('/', '.')  # substitute / separator by .
            if len(href) < jd2chm_const.MAX_SIZE_KEYWORD and len(title) < jd2chm_const.MAX_SIZE_KEYWORD:
                # Too long href or title causes the HHC compiler too crash (example with createArray method in Groovy).
                # It is better to simply skip those exceptional cases.
                self.write_index(href, self.sanitize_title(title), java_class)
        if self.kword:
            self.write_index()

    def write_index(self, href="", title="", java_class=""):
        if self.kword and self.kword != title:
            if len(self.entries) == 1:
                # only one item, no need for sub-entries in the index
                self.hhk_file.write(jd2chm_const.FORMAT_INDEX_ITEM % (self.entries[0][0], self.kword))
            else:
                # Multiple entries so subindex for the same kword
                self.hhk_file.write(jd2chm_const.FORMAT_INDEX_KEYWORD % (self.kword, self.kword))
                self.hhk_file.write('<ul>\n')
                for entry in self.entries:
                    # entry[0] is href, entry[1] is java_class
                    self.hhk_file.write(jd2chm_const.FORMAT_INDEX_ITEM % (entry[0], "in " + entry[1]))
                self.hhk_file.write('</ul>\n')
            self.kword = title
            self.entries = []
        else:
            if not self.kword:
                self.kword = title
        self.entries.append((href, java_class))


class ChmProject:
    """Main class"""

    def __init__(self):
        self.content_file = ''
        self.default_file = ''
        self.log = jd2chm_utils.get_log()

    def parse_re_index_html(self):
        """Parses index.html file to retrieve the files to be parsed in order to create
        the contents table and to set the default page

        JavaDoc with multiple packages:
        Takes the attribute src in the 1st tag <FRAME>, "overview-frame.html" and in
        the 3rd tag <FRAME>, "overview-summary.html"

        JavaDoc with one package:
        Takes the attribute src in the 1st tag <FRAME>, "allclasses-frame.html" and
        in the 2nd tag <FRAME>, example: "com/sun/javadoc/package-summary.html"
        """
        fo = open(jd2chm_const.INDEX_HTML)
        lines = fo.readlines()
        fo.close()
        self.re_src = re.compile(r'^<frame src="([^"]*)"')
        for line in lines:
            res = self.re_src.match(line)
            if res:
                if not self.content_file:
                    self.content_file = res.group(1)
                else:
                    self.default_file = res.group(1)

    def create_project(self, project_name, project_title):
        self.parse_re_index_html()
        self.log.debug('Content file: %s' % self.content_file)
        self.log.debug('Default file: %s' % self.default_file)
        hhp = Hhp(project_name, project_title, self.default_file)
        self.log.info("Creating HTML Help Project")
        hhp.create_hhp()
        # Create hhc file (contents)
        # The default file is passed to be used in case of a single package
        hhc = Hhc(project_name, self.content_file, self.default_file)
        self.log.info("Creating HTML Help Contents")
        hhc.create_hhc()
        # Create hhk file (index)
        hhk = Hhk(project_name)
        print()  # Add a CR after the dots
        self.log.info("Creating HTML Help Index")
        hhk.create_hhk()


class ChmEnv:
    """Creates a temporary environment to build and compile the project

    Copies all the source file into the temporary directory. Generates the common
    files (CSS, About). Cleans-up the HTML files: especially, the white-spaces in
    some URL's (method with more than one parameter).

    """

    def __init__(self):
        self.log = jd2chm_utils.get_log()

    def prepare_env(self, project_name, jdoc_dir):
        self.project_name = project_name
        self.start_dir = os.getcwd()

        if EXTERNAL_COMPILER:
            # If HH Compiler not installed, it prompts
            # the user and stops
            self.html_compiler = self.get_html_compiler_path()
        else:
            self.log.info('Using internal compiler (module pyhhc)')

        # Check if a project with the same name is already open
        chm_file = os.path.join(self.start_dir, '%s.chm' % project_name)
        if os.path.exists(chm_file):
            while 1:
                try:
                    os.unlink(chm_file)
                    break
                except OSError:
                    # TODO: this will have to be handled differently via the GUI (not with a raw input...)
                    self.log.warning("The file %s is open" % chm_file)
                    print("\nThe file %s is open" % chm_file)
                    print("Close the corresponding Window and type any key")
                    input()

        # Copy full javadoc files into working directory
        self.temp_dir = self.copy_javadoc(jdoc_dir)
        # Working directory becomes current dir
        os.chdir(self.temp_dir)
        # Modifiy files (URL clean-up)
        self.re_method = re.compile(r'<td><code><b><a\s+href="([^"]*)">')
        self.re_bookmark = re.compile(r'<a name="([^"]*)">')
        self.clean_html_files()
        # Create CSS file
        if jd2chm_const.CUSTOM_CSS:
            self.create_css()
        # Create about file
        create_about()

    def get_html_compiler_path(self):
        """HTML Help Workshop may be installed and found in %programfiles(x86)%\HTML Help Workshop.
        If installed via the installer found at http://bit.ly/hhdownload, the path may be found in the
        registry. The comiler is hhc.exe. If no compiler found stop the
        """
        hhc_path = os.path.join(os.environ['programfiles(x86)'], 'HTML Help Workshop', 'hhc.exe')
        if not os.path.exists(hhc_path):
            hhc_path = None
            try:
                hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, jd2chm_const.HTML_HELP_WSHOP_KEY)
                data, key_type = win32api.RegQueryValueEx(hkey, "InstallDir")
                win32api.RegCloseKey(hkey)
            except pywintypes.error:
                self.log.info("HTML Help Workshop does not seem to be installed.")
                # self.log.info("From http://www.burgaud.com/jd2chm_res.html, you will find the link to download the latest version of Microsoft HTML Help Compiler")
                # os.system('start hh mk:@MSITStore:%s\\dialogs.chm::/compiler.htm' % sys.path[0])
                return None
            hhc_path = os.path.join(data, 'hhc.exe')
            self.log.debug(hhc_path)
            if not os.path.exists(hhc_path):
                self.log.warning(
                    "HTML Help Workshop has a valid key in the registry, but the compiler {} was not found.".format(
                        hhc_path))
                self.log.warning("You may have to reinstall HTML Help Workshop.")
                # os.system('start hh mk:@MSITStore:%s\\dialogs.chm::/compiler.htm' % sys.path[0])
                hhc_path = None
        return hhc_path

    def make(self, handle=0):
        # Copy the generated files in the starting dir
        # for file in glob.glob("%s.hh?" % project_name):
        #  print "Copy:", file
        #  shutil.copyfile(file, os.path.join(start_dir, file))

        if EXTERNAL_COMPILER:
            # Call the compiler
            compiler = win32api.GetShortPathName(self.html_compiler)
            self.log.info('HTML Help Compilation (Microsoft HTML Help compiler)')
            if handle:
                # TODO: Start compilation in a thread
                os.system('%s %s.hhp' % (compiler, self.project_name))
            else:
                os.system('%s %s.hhp' % (compiler, self.project_name))
        else:
            self.log.info('Compiling %s' % self.project_name)
            pyhhc.compileHHP('%s.hhp' % self.project_name)

        # Copy back the compiled chm file (if any)
        chm = '%s.chm' % self.project_name
        if os.path.isfile(chm):
            shutil.copyfile(chm, os.path.join(self.start_dir, chm))
        else:
            self.log.error("No compiled HTML %s file generated" % chm)

        # Come back to the starting directory
        # Could be needed to start the chm for example
        os.chdir(self.start_dir)

        # ~ def delete_work_dir(self, dir):
        # ~ # TODO: seems to take some time with the JDK
        # ~ # a os.system("delete %s" % dir), though not elegant could
        # ~ # improve the performance. To be tested
        # ~ if os.path.isdir(dir):
        # ~ shutil.rmtree(dir)

    def copy_javadoc(self, jdoc_dir):
        """Copy the current tree into the temporary working directory"""
        tmp_dir = tempfile.gettempdir()
        tmp_dir = os.path.join(tmp_dir, jd2chm_const.WORKING_DIR, self.project_name)

        if not jd2chm_const.REUSE_TEMP_FILES:
            if os.path.isdir(tmp_dir):
                self.log.info("Deleting old directory %s" % tmp_dir)
                try:
                    shutil.rmtree(tmp_dir)
                except OSError as ose:
                    # TODO: will need to abort something here
                    self.log.error(ose)
            cpt = 0
            while True:
                try:
                    cpt += 1
                    self.log.info("Copying Javadoc files to {}.".format(tmp_dir))
                    self.log.info("It may take a while for a large size Java Documentation.")
                    shutil.copytree(jdoc_dir, tmp_dir)
                    break
                except PermissionError as pe:
                    self.log.warn("First attempt copying Javadoc file failed...")
                    if cpt > 3:
                        print("There was an error copying the Javadoc files to a temporary directory")
                        print(pe)
                        sys.exit(4)
                    time.sleep(5)
        return tmp_dir

    def clean_html_files(self):
        # Assume current directory
        os.walk('.', self.clean_html, None)

    def clean_html(self, junk, dirname, names):
        del junk  # We don't use it. Eliminate warning in PyChecker
        for html_file in names:
            if os.path.splitext(html_file)[1] == ".html":
                lines_modified = 0
                new_lines = []
                html_dir = os.path.abspath(dirname)
                path = os.path.join(html_dir, html_file)
                fo = open(path)
                lines = fo.readlines()
                fo.close()
                for line in lines:
                    # Check link method
                    new_line = self.quote_url(self.re_method, line)
                    if new_line:
                        line = new_line
                        lines_modified += 1
                        new_lines.append(line)
                        # Should not have the link and anchor on the same line
                        continue
                    # Check bookmark method
                    new_line = self.quote_url(self.re_bookmark, line)
                    if new_line:
                        line = new_line
                        lines_modified += 1
                    new_lines.append(line)
                if lines_modified:
                    self.log.info('%s: %s lines modified' % (html_file, lines_modified))
                    fo = open(path, "w")
                    fo.writelines(new_lines)
                    fo.close()

    def quote_url(self, regex, line):
        match = regex.search(line)
        new_line = None
        # The line can be a method line (link or anchor)
        if match:
            method = match.group(1)
            # if the last char is ')', it is a method (not a field)
            # if if has a space, need to be modified
            if method[-1] == ')' and method.find(' ') != -1:
                href = urllib.parse.quote(method, safe='()/,#')
                new_line = line.replace(method, href)
        return new_line

    def create_css(self):

        """Creates a custom CSS file (stylesheet.css) generated by the Javadoc and
        saves the original Javadoc css file (stylesheet.css) unless already saved.
        """

        css_file_bak = jd2chm_const.CSS_FILE_NAME + ".bak"
        if os.path.exists(jd2chm_const.CSS_FILE_NAME):
            if not os.path.exists(css_file_bak):
                self.log.info(
                    "Saves the original Javadoc css file (%s) as %s" % (jd2chm_const.CSS_FILE_NAME, css_file_bak))
                shutil.copyfile(jd2chm_const.CSS_FILE_NAME, jd2chm_const.CSS_FILE_NAME + ".bak")
        css_file = open(jd2chm_const.CSS_FILE_NAME, 'w')
        css_file.write(jd2chm_const.FORMAT_CSS)
        css_file.close()


def create_about():
    """Creates an HTML about file to be included in the project."""
    about_file = open(jd2chm_const.ABOUT_FILE, 'w')
    about_file.write(jd2chm_const.ABOUT_TEXT)
    about_file.close()


# TODO: Replace walktree by os.path.walk or better
# by os.walk available in Python 2.3
def walktree(folder, callback):
    """Recursively descends the directory rooted at dir, calling the callback
    function for each HTML file
    """

    # debug("[walktree] Directory: %s" % dir)
    sys.stdout.write('.')
    if folder == './' + jd2chm_const.INDEX_DIR:
        print()  # Carriage return after the dots...
        print("Skipping %s" % folder)
        return
    for f in os.listdir(folder):
        pathname = '%s/%s' % (folder, f)
        if os.path.isdir(pathname):
            walktree(pathname, callback)
        elif os.path.isfile(pathname):
            callback(pathname)  # Writes the line in the project file section
        else:
            print()  # Carriage return after the dots...
            print("Skipping %s" % pathname)


def print_dot(cpt):
    """Print dots '.' to show activity in progress"""
    cpt += 1
    if cpt > 100:
        sys.stdout.write('.')
        cpt = 0
    return cpt
