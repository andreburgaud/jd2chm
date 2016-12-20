"""
Jd2chm configuration module
"""

import os
import configparser
import win32api
import win32con
import pywintypes
import shutil

import jd2chm_const
import jd2chm_utils

JD2CHM_DIR = '.jd2chm'
PROJECTS_DIR = 'projects'
CSS_DIR = 'css'
CSS_FILE = 'jd2chm.css'

CONF_DEFAULT = 'default.cfg'
CONF_FILE = 'jd2chm.cfg'
MSHHC = 'mshhc'
PYHHC = 'pyhhc'
YES = 'yes'
NO = 'no'

CSS_TEMPLATE = """\
/* Default Jd2chm CSS file */
body { background-color: #FFFFFF; font-size: 10pt; font-family: Helvetica, Arial, sans-serif }
td { background-color: #FFFFFF; font-size: 10pt; font-family: Helvetica, Arial, sans-serif }
/* Table colors */
.TableHeadingColor     { background: #CCCCFF } /* Dark mauve */
.TableSubHeadingColor  { background: #EEEEFF } /* Light mauve */
.TableRowColor         { background: #FFFFFF } /* White */
/* Font used in left-hand frame lists */
.FrameTitleFont   { font-size: 10pt; font-family: Helvetica, Arial, sans-serif}
.FrameHeadingFont { font-size: 10pt; font-family: Helvetica, Arial, sans-serif }
.FrameItemFont    { font-size: 10pt; font-family: Helvetica, Arial, sans-serif }
/* Links */
a:link { color: #0000FF; text-decoration: underligne;}
a:visited { color: #A9A9A9 ; text-decoration: underligne;}
a:active { color: #FF0000; text-decoration: underligne;}
a:hover { color: #FF0000; text-decoration: underligne;}
/* Navigation bar fonts and colors */
.NavBarCell1    { background-color:#EEEEFF;} /* Light mauve */
.NavBarCell1Rev { background-color:#00008B;} /* Dark Blue */
.NavBarFont1    { font-family: Helvetica, Arial, sans-serif; color:#000000;}
.NavBarFont1Rev { font-family: Helvetica, Arial, sans-serif; color:#FFFFFF;}
.NavBarCell2    { font-family: Helvetica, Arial, sans-serif; background-color:#FFFFFF;}
.NavBarCell3    { font-family: Helvetica, Arial, sans-serif; background-color:#FFFFFF;}
"""

CONF_TEMPLATE = """\
# Jd2chm Configuration File
[DEFAULT]
default_css = jd2chm.css
default_compiler = pyhhc
log_notset = 0
log_debug = 1
log_info = 2
log_warning = 3
log_error = 4
log_critical = 5

[files]
# ==============================================================================
# CSS
# To override the default Javadoc CSS provide your own CSS file and copy it
# in the conf directory.
# Default: jd2chm.css
# ==============================================================================
css = %(default_css)s

[paths]
# ==============================================================================
# Projects path by default is jd2chm dir + projects (i.e.
# C:\Documents and Settings\<USER>\.jd2chm\projects
# ==============================================================================
projects =
# ==============================================================================
# Last Javadoc source location (used by the application)
# ==============================================================================
javadoc =

[chm]
# ==============================================================================
# CHM options
# The compiler can be the jd2chm built-in compiler (pyhhc):
# compiler = pyhhc
# Or the Microsoft compiler (mshhc) if installed:
# compiler = mshhc
# Default: pyhhc (built-in compiler)
# ==============================================================================
compiler = %(default_compiler)s
toc_binary = no

[log]
# ==============================================================================
# Last Javadoc source location (used by the application)
# ==============================================================================
level = %(log_info)s
"""

MSG_WARN_PYHHC_NOT_FOUND_1 = """\
The HTML compiler is set to the internal Jd2chm compiler,
but the pyhcc module does not seem to be installed."""

MSG_WARN_PYHHC_NOT_FOUND_2 = """
The compiler from HTML Help Workshop (%s) will be used instead."""

MSG_WARN_NO_COMPILER_FOUND = """
Neither the internal nor external HTML Help compiler are present on your computer.
Though you will be able to generate HTML Help project files, you won't be able to compile an CHM file.
Please consult the Jd2chm documentation for more information."""

MSG_WARN_MSHHC_NOT_FOUND_1 = """\
The HTML compiler is set to the external compiler,
but the Microsoft HTML Compiler was not found on your computer."""

MSG_WARN_MSHHC_NOT_FOUND_2 = """
Jd2chm internal compiler will be used instead."""

MSG_WARN_CSS = """\
CSS file %s not found.
Check the CSS file name or ensure that your created %s in the directory %s.
Existing options unchanged."""

MSG_WARN_PROJECTS_DIR = """\
Could not create projects folder %s.
Default projects folder %s will be used instead."""

MSG_ERROR_PROJECTS_DIR = """\
Could not create the default project folder %s.
Change the projects path in the configuration.
"""


class Jd2chmConfig:
    """Configuration wrapper. Create the default working directory. Holds the
    configuration parameters and manage the configuration files."""

    def __init__(self):
        self.log = jd2chm_utils.get_log()
        self.compiler = None  # pyhhc or mshhc
        self.css_path = None  # CSS file path used during CHM build
        self.javadoc_path = None  # Path of the last Javadoc compiled with jd2chm
        user_dir = os.path.expanduser('~')
        self.work_dir = os.path.join(user_dir, JD2CHM_DIR)
        self.css_dir = os.path.join(self.work_dir, CSS_DIR)
        self.default_css_path = os.path.join(self.css_dir, CSS_FILE)
        self.default_projects_dir = os.path.join(self.work_dir, PROJECTS_DIR)
        self.config_path = os.path.join(self.work_dir, CONF_FILE)

    def init(self):
        self.createWorkingDir()
        self.loadConfigFile()

    def cleanUp(self):
        """Delete working directory: <user_dir>/.jd2chm."""
        if os.path.exists(self.work_dir):
            self.log.info("Delete working directory...")
            shutil.rmtree(self.work_dir)

    def createWorkingDir(self):
        """Default root working directory: <user_dir>/.jd2chm. Other directories:
        <user_dir>/.jd2chm/css."""
        for dir in (self.work_dir, self.css_dir):
            if not os.path.exists(dir):
                os.mkdir(dir)

    def loadConfigFile(self):
        """Create the configuration file. Load the configuration values."""
        default_config_path = os.path.join(self.work_dir, CONF_DEFAULT)
        if not os.path.exists(default_config_path):
            f = open(default_config_path, 'w')
            f.write(CONF_TEMPLATE)
            f.close()
        self.config = configparser.ConfigParser()
        self.config.read(default_config_path)
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        self.loadConfiguration()

    def saveUserFile(self):
        f = open(os.path.join(self.work_dir, CONF_FILE), 'w')
        self.config.write(f)
        f.close()

    def setLogLevel(self):
        jd2chm_utils.get_logging().setLevel(self.level)

    def reloadDefaultConfig(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        self.loadConfigFile()  # Will load the default file and the configuration

    def loadConfiguration(self):
        # Log Level
        self.level = self.getLevel()
        self.log.info("Log level: %d" % self.level)
        self.setLogLevel()
        # CSS File
        self.css_path = self.getCssPath()
        self.log.info("CSS file path: %s" % self.css_path)
        # CHM Compiler
        self.compiler = self.getCompiler()
        self.log.info("CHM compiler: %s" % self.compiler)
        # CHM Options
        self.toc_binary = self.getHhpOptions()
        self.log.info("TOC Binary: %s" % self.toc_binary)
        # Projects folder
        self.projects_dir = self.getProjectsDir()
        self.log.info("Projets path: %s" % self.projects_dir)
        # Last Javadoc path
        self.javadoc_path = self.getJavadoc()
        if self.javadoc_path:
            self.log.info("Last Javadoc path: %s" % self.javadoc_path)

    def getLevel(self):
        level = self.config.getint('log', 'level')
        return level

    def setLevel(self, level):
        self.config.set('log', 'level', str(level))
        self.level = level
        self.setLogLevel()
        self.log.info("Log level set to %s" % level)
        self.saveUserFile()

    def getHhpOptions(self):
        toc_binary = self.config.get('chm', 'toc_binary')
        toc_binary = toc_binary.lower()
        if toc_binary not in (YES, NO):
            toc_binary = NO
        return toc_binary

    def setTocBinary(self, yes_no):
        self.config.set('chm', 'toc_binary', yes_no)
        self.toc_binary = yes_no
        self.log.info("TOC binary set to %s" % yes_no)
        self.saveUserFile()

    def getCompiler(self):
        compiler = self.config.get('chm', 'compiler')
        compiler = compiler.lower()
        self.validate_compiler(compiler)
        return compiler

    def setCompiler(self, compiler):
        self.config.set('chm', 'compiler', compiler)
        self.compiler = compiler
        self.log.info("Compiler set to %s" % compiler)
        self.saveUserFile()

    def get_mshhc_path(self):
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

    def validate_compiler(self, compiler):
        """Check presence of internal compiler and MS compiler. Switch automatically
        to other compiler if the configured compiler is not found.
        """
        global PYHCC
        global MSHHC
        if compiler == "":
            self.log.warning("CHM compiler not set: CHM compilation will not take place.")
            return compiler
        if compiler not in (MSHHC, PYHHC):
            self.log.warning(
                "CHM compiler set to an unknown value '%s'. Jd2chm will attempt to use the built-in compiler (default).")
            compiler = PYHCC
        part_msg = None
        self.mshhc_path = self.get_mshhc_path()
        if compiler == PYHHC:
            # Internal Compiler (PYHCC)
            try:
                import pyhhc
                self.log.debug("Module pyhhc available")
            except ImportError:
                part_msg = MSG_WARN_PYHHC_NOT_FOUND_1
                self.log.info(part_msg)
                if self.mshhc_path:
                    self.log.warning(part_msg + (MSG_WARN_PYHHC_NOT_FOUND_2 % self.mshhc_path))
                    compiler = MSHHC
                else:
                    self.log.warning(MSG_WARN_NO_COMPILER_FOUND)
                    compiler = None
        else:
            # External compiler (MSHHC)
            if not self.mshhc_path:
                part_msg = MSG_WARN_MSHHC_NOT_FOUND_1
                self.log.info(part_msg)
                try:
                    import pyhhc
                    self.log.warning(part_msg + MSG_WARN_MSHHC_NOT_FOUND_2)
                    compiler = PYHHC
                except ImportError:
                    self.log.warning(MSG_WARN_NO_COMPILER_FOUND)
                    compiler = None
        return compiler

    def getCssPath(self):
        css_file = self.getCss()
        css_path = self.validateCss(css_file)
        return css_path

    def getCss(self):
        css_file = self.config.get('files', 'css')
        return css_file

    def setCss(self, css_file):
        css_path = os.path.join(self.css_dir, css_file)
        if not os.path.exists(css_path):
            self.log.warning(MSG_WARN_CSS % (css_path, css_file, self.css_dir))
            return
        self.config.set('files', 'css', css_file)
        self.log.info("CSS file set to %s" % css_file)
        self.css_path = css_path
        self.log.info("CSS file path is %s" % css_path)
        self.saveUserFile()

    def createDefaultCss(self):
        # Create the default CSS file
        f = open(self.default_css_path, 'w')
        f.write(CSS_TEMPLATE)
        f.close()

    def validateCss(self, css_file):
        """Validate presence of CSS file. Create default CSS file if needed. If
        css file in the config not found, the default CSS is used.
        """
        css_path = os.path.join(self.css_dir, css_file)
        if not os.path.exists(css_path):
            if css_file == CSS_FILE:
                self.log.info("Using the default CSS file: %s." % self.default_css_path)
                self.createDefaultCss()
            else:
                self.log.warning("The file %s does not exist, %s will be used instead." % (
                self.full_css_path, self.default_css_path))
                if not os.path.exists(self.default_css_path):
                    self.createDefaultCss()
            css_path = self.default_css_path
        return css_path

    def getProjectsDir(self):
        projects_dir = self.config.get('paths', 'projects')
        if projects_dir:
            if not os.path.exists(projects_dir):
                try:
                    os.makedirs(projects_dir)
                except:
                    self.log.warning(MSG_WARN_PROJECTS_DIR % (projects_dir, self.default_projects_dir))
                    projects_dir = self.default_projects_dir
        else:
            projects_dir = self.default_projects_dir
        if projects_dir == self.default_projects_dir:
            if not os.path.exists(self.default_projects_dir):
                try:
                    os.makedirs(self.default_projects_dir)
                except:
                    self.log.error(MSG_ERROR_PROJECTS_DIR % (self.default_projects_dir))
        return projects_dir

    def setProjectsDir(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                self.log.warning(MSG_WARN_PROJECTS_DIR % (path, self.projects_dir))
                return
        self.config.set('paths', 'projects', path)
        self.projects_dir = path
        self.log.info("Projects folder is %s" % path)
        self.saveUserFile()

    def getJavadoc(self):
        javadoc_path = self.config.get('paths', 'javadoc')
        return javadoc_path

    def setJavadoc(self, path):
        self.config.set('paths', 'javadoc', path)
        self.last_javadoc = path
        self.log.info("Javadoc directory is %s" % path)
        self.saveUserFile()
