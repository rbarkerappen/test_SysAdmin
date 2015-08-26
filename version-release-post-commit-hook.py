#!/usr/bin/env python3

import re
import subprocess

VERSION_CHANGE_RE = re.compile('^(?P<sign>\-|\+)\s*version="(?P<version>\S+)"(,)?$')


def cleanOutput(output: str) -> str:
	"""
	Does some simple cleaning for the provided script output.
	"""
	output = output or ""
	if isinstance(output, bytes):
		output = output.decode()
	output = output.strip()
	return output


def execute(command: str, printOutput=False) -> str:
	"""
	Executes an external command.
	"""
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()

	stdout = cleanOutput(stdout)
	stderr = cleanOutput(stderr)
	
	if stderr:
		print(stderr)

	if process.returncode != 0:
		raise RuntimeError("Command failed: %r" %command)

	if printOutput:
		print(stdout)

	return stdout


def getHashes() -> tuple:
	"""
	Gets the two most recent commit hashes.
	"""
	command = 'git log -n 2 --pretty=format:\"%H\"'
	output = execute(command)
	current, previous = output.split()
	return current, previous


def getSetupDiff(currentHash: str, previousHash: str) -> str:
	"""
	Gets the diff of the given commit hashes for the
	setup.py script.
	"""
	command = "git diff %s %s setup.py" %(previousHash, currentHash)
	output = execute(command)
	return output


def detectVersionChange(diff: str) -> tuple:
	"""
	Parses the commit diff for setup.py to look for
	a version change.
	"""
	previousVersion = None
	currentVersion = None
	
	for line in diff.split("\n"):
		m = VERSION_CHANGE_RE.match(line)
		if m:
			d = m.groupdict()

			# this line is the previous version
			if d["sign"] == "-":
				previousVersion = d["version"]

			# this line is the new/current version
			elif d["sign"] == "+":
				currentVersion = d["version"]

	return previousVersion, currentVersion


currentHash, previousHash = getHashes()

diff = getSetupDiff(currentHash, previousHash)

if diff:
	previousVersion, currentVersion = detectVersionChange(diff)

	if previousVersion and not currentVersion:
		print("Warning: Possible version change detected, but could not determine current version. Please manually tag the commit if the version has changed.")

	elif not previousVersion and currentVersion:
		print("Warning: Possible version change detected, but could not determine current version. Please manually tag the commit if the version has changed.")

	else:
		print("Detected version change from %s to %s" %(previousVersion, currentVersion))
		print("Tagging branch with version %s" %currentVersion)
		command = 'git tag -a %s -m "Release %s"' %(currentVersion, currentVersion)
		execute(command, printOutput=True)
		#print("Pushing new version")
		#execute("git push origin", printOutput=True)
		#command = "git push origin %s" %currentVersion
		#execute(command, printOutput=True)
		print("To make the new version available, please use the following commands:")
		print("  git push origin")
		print("  git push origin %s" %currentVersion)
