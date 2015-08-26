#!/usr/bin/env python3

"""
Helper script for building a new release. Each release will be tagged (using git).

Usage:
  python release.py -m "this is a new release"

Important: various git commands and performed in this script, so please make sure any
changes to the code are committed and pushed *before* running this script.

Important: this script must be run in the same location that it is stored in.

This script was developed using commands compatible with git version 2.1.0.
"""


import datetime
import os
import subprocess
import sys
from argparse import ArgumentParser
from mako.template import Template


def getDefaultVersion():
	"""
	Returns the default version number.
	"""
	now = datetime.datetime.utcnow()
	tokens = ["%Y", "%m", "%d", "%H", "%M"]
	tokens = [now.strftime(t) for t in tokens]
	tokens = [str(int(t)) for t in tokens]	# remove leading zeros so the version number is normalised
	return ".".join(tokens)


def buildSetup(version):
	"""
	Builds the setup.py distribution file.
	"""

	with open("setup.py", "wb") as f:
		template = Template(filename="setup.py.mako")
		f.write(template.render_unicode(version=version).encode("utf-8"))


def execute(command):
	"""
	Executes an external command.
	"""
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output = process.communicate()[0]

	if output is not None:
		if isinstance(output, bytes):
			output = output.decode()
		output = output.strip()
		if output:
			print(output)

	if process.returncode != 0:
		raise RuntimeError("Command failed: %r" %command)


parser = ArgumentParser(__doc__)
parser.add_argument("-v", "--version", type=str, default=getDefaultVersion(), help="Version number.")
parser.add_argument("-m", "--message", type=str, required=True, help="Brief description of what was changed or updated. Used on the git tag.")
parser.add_argument("-f", "--folder", type=str, default=".", help="The location of the repo. If not provided, the current directory is assumed.")
parser.add_argument("--nopush", action="store_true", default=False, help="Use this if the release should not be pushed.")
args = parser.parse_args()

# we have to move into the git repo to run the git commands properly;
# save the current dir so we can get back there at the end
savedPath = os.getcwd()

# move into git repo
os.chdir(args.folder)

try:
	print("Building setup.py")
	buildSetup(args.version)

	print("Committing and tagging release")
	execute("git add setup.py")
	execute("git commit . -m \"Release: %s\"" %args.version)
	execute("git tag -a %s -m \"%s\"" %(args.version, args.message))

	print("Release %s built successfully." %args.version)
	if args.nopush:
		print("The release has not been pushed. Please use the following command if you want to push the release:")
		print("  git push origin %s" %args.version)
		print("  git push origin")
	else:
		print("Pushing version %s" %args.version)
		execute("git push origin %s" %args.version)
		execute("git push origin")

except Exception:
	# move back to original dir if there is an error (so 
	# the user can run the script again easily)
	os.chdir(savedPath)
	raise

else:
	# move back to original dir upon completion
	os.chdir(savedPath)
