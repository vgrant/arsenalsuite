#!/usr/bin/env python

import os
import sipconfig
import PyQt4.pyqtconfig as pyqtconfig
import sys
import getopt
import glob

opt_static=0
opt_debug=0

class StoneModuleMakefile(sipconfig.SIPModuleMakefile):
	def __init__(self, *args, **kw):
		"""Initialise an instance of a module Makefile.
		"""
		if not kw.has_key("qt"):
			kw["qt"] = ["QtCore", "QtXml", "QtSql","QtNetwork","QtGui"]
		apply(sipconfig.SIPModuleMakefile.__init__, (self, ) + args, kw)

	# Override target for static builds
	def finalise(self):
		sipconfig.SIPModuleMakefile.finalise(self)
		if self.static:
			self._target = 'py' + self._target

def doit():
	global opt_static
	global opt_debug
	# The name of the SIP build file generated by SIP and used by the build
	# system.
	build_file = "stone.sbf"

	# Get the PyQt configuration information.
	config = pyqtconfig.Configuration()
	config.pyqt_modules = ['QtCore','QtXml','QtNetwork','QtSql']
	config.__dict__["AR"] = "ar r"

	# Get the extra SIP flags needed by the imported qt module.  Note that
	# this normally only includes those flags (-x and -t) that relate to SIP's
	# versioning system.
	#print config.__dict__

	# Run SIP to generate the code.  Note that we tell SIP where to find the qt
	# module's specification files using the -I flag.
	#config.pyqt_sip_dir = "/usr/share/sip/PyQt4"
	#config.pyqt_sip_dir = "c:\\python24\\sip\\PyQt4\\"
	if sys.platform=="win32":
		sip_bin = "..\\sip\\sipgen\\sip.exe"
	else: 
		sip_bin = config.sip_bin
	cmd = " ".join([sip_bin, "-e", "-k", "-c", "sipStone", "-b", "sipStone/"+build_file, "-I", config.pyqt_sip_dir, config.pyqt_sip_flags, "sip/blurqt.sip"])
	ret = os.system(cmd)
	
	if ret:
		sys.exit(ret%255)

	# We are going to install the SIP specification file for this module and
	# its configuration module.

	# Create the Makefile.  The QtModuleMakefile class provided by the
	# pyqtconfig module takes care of all the extra preprocessor, compiler and
	# linker flags needed by the Qt library.
	makefile = StoneModuleMakefile(
		configuration=config,
		build_file=build_file,
		static=opt_static,
		debug=opt_debug,
		# Use the sip mod directory instead in order to adhere to the DESTDIR settings
		install_dir=os.path.join(config.sip_mod_dir,"blur"),
#       install_dir=os.path.join(config.default_mod_dir,"blur"),
		dir="sipStone"
	)
	installs = []
	sipfiles = []
	scriptfiles = []

	scriptfilesprefix = "../../../python/blur"
	for s in glob.glob(scriptfilesprefix + "/*.py"):
		if sys.platform == "win32":
			scriptfilesprefix = scriptfilesprefix.replace("/","\\")
		scriptfiles.append(os.path.join(scriptfilesprefix, os.path.basename(s)))

	installs.append([scriptfiles, os.path.join(config.sip_mod_dir, "blur")])

	for s in glob.glob("sip/*.sip"):
		sipfiles.append(os.path.join("sip", os.path.basename(s)))

	# installs.append([sipfiles, os.path.join(config.sip_mod_dir, "blur")])
	installs.append([sipfiles, os.path.join(config.default_sip_dir, "blur")])

	# Use the sip mod directory instead in order to adhere to the DESTDIR settings
	installs.append(["stoneconfig.py", config.sip_mod_dir])
#   installs.append(["stoneconfig.py", config.default_mod_dir])

	if opt_static == 0:
		if os.name == 'nt':
			installs.append(["stone.dll", os.path.join(config.default_mod_dir, "blur")])

	sipconfig.ParentMakefile(
		configuration=config,
		installs=installs,
		subdirs=["sipStone"]
	).generate()

	# Add the library we are wrapping.  The name doesn't include any platform
	# specific prefixes or extensions (e.g. the "lib" prefix on UNIX, or the
	# ".dll" extension on Windows).
	if sys.platform == "win32":
		makefile.extra_libs = ["stone","QtSql4","QtXml4","QtNetwork4"]
	elif sys.platform == "darwin":
		makefile.extra_libs = ["stone"]
	else:
		makefile.extra_libs = ["stone","QtSql","QtXml","QtNetwork"]
		
	makefile.extra_include_dirs = ["../include"]
	makefile.extra_lib_dirs.append( ".." );

	# Generate the Makefile itself.
	makefile.generate()

	# Now we create the configuration module.  This is done by merging a Python
	# dictionary (whose values are normally determined dynamically) with a
	# (static) template.
	content = {
		# Publish where the SIP specifications for this module will be
		# installed.
		"stone_sip_dir":    config.default_sip_dir,

		# Publish the set of SIP flags needed by this module.  As these are the
		# same flags needed by the qt module we could leave it out, but this
		# allows us to change the flags at a later date without breaking
		# scripts that import the configuration module.
		"stone_sip_flags":  config.pyqt_sip_flags
	}

	# This creates the helloconfig.py module from the helloconfig.py.in
	# template and the dictionary.
	sipconfig.create_config_module("stoneconfig.py", "stoneconfig.py.in", content)

def usage(rcode = 2):
    """Display a usage message and exit.

    rcode is the return code passed back to the calling process.
    """
    print "Usage:"
    print "    python configure.py [-k]"
    print "where:"
    print "  -h      display this help message"
    print "  -k      build the PyQt modules as static libraries"
    sys.exit(rcode)

def main(argv):
	"""Create the configuration module module.

	argv is the list of command line arguments.
	"""

	# Parse the command line.
	try:
		optlist, args = getopt.getopt(argv[1:], "khu")
	except getopt.GetoptError:
		usage()

	global opt_static
	global opt_debug
	
	for opt, arg in optlist:
		if opt == "-h":
			usage(0)
		elif opt == "-k":
			opt_static = 1
		elif opt == "-u":
			opt_debug = 1
	doit()

if __name__ == "__main__":
	main(sys.argv)
