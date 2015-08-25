#!/usr/bin/env python3


import datetime
import os
import subprocess
import sys
from argparse import ArgumentParser
from mako.template import Template

DEFAULT_NAME = None	#TODO add default name


def getDefaultVersion():
	"""
	Returns the default version number.
	"""
	now = datetime.datetime.utcnow()
	tokens = ["%Y", "%m", "%d", "%H", "%M"]
	tokens = [now.strftime(t) for t in tokens]
	# remove leading zeros
	tokens = [str(int(t)) for t in tokens]
	return ".".join(tokens)


def buildSetup(args):
	"""
	Builds the setup.py distribution file.
	"""
	context = dict(
		version=args.version,
		name=args.name,
	)

	with open("setup.py", "wb") as f:
		template = Template(filename="setup.py.mako")
		f.write(template.render_unicode(**context).encode("utf-8"))


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
		print(output)

	if process.returncode != 0:
		raise RuntimeError("Command failed: %r" %command)


parser = ArgumentParser(__doc__)
parser.add_argument("-p", "--python", type=str, default="python", help="Specify the python command for running setup.py")
parser.add_argument("-v", "--version", type=str, default=getDefaultVersion(), help="Version name/number.")
parser.add_argument("-n", "--name", type=str, default=DEFAULT_NAME, help="Name of the package.")
parser.add_argument("-m", "--message", type=str, required=True, help="Release message used for the git tag. Brief description of what was changed or updated.")
parser.add_argument("--nopush", action="store_true", default=False, help="Use this if the release should not be pushed to GitHub.")
args = parser.parse_args()


print("Building setup.py")
buildSetup(args)

print("Creating egg file")
execute("%s setup.py bdist_egg" %args.python)

print("Adding new egg file to repository")
execute("git add dist/")

print("Committing release")
execute("git commit . -m \"Release: %s\"" %args.version)

print("Tagging release")
execute("git tag -a %s -m \"%s\"" %(args.version, args.message))

print("Release %s built successfully." %args.version)
if args.nopush:
	print("The release has not been pushed to GitHub. Please use the following command if you want to push the release:\n  git push origin %s" %args.version)
else:
	print("Pushing version %s to GitHub" %args.version)
	execute("git push origin %s" %args.version)

