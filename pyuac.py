#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4

"""User Access Control for Microsoft Windows Vista and higher.  This is
only for the Windows platform.

This will relaunch either the current script - with all the same command
line parameters - or else you can provide a different script/program to
run.  If the current user doesn't normally have admin rights, he'll be
prompted for an admin password. Otherwise he just gets the UAC prompt.

Note that the prompt may simply shows a generic python.exe with "Publisher:
Unknown" if the python.exe is not signed.

This is meant to be used something like this::

	if not pyuac.isUserAdmin():
		return pyuac.runAsAdmin()

	# otherwise carry on doing whatever...

See L{runAsAdmin} for the main interface.

"""

import os
import sys
import traceback
import types


def is_user_admin():
	"""@return: True if the current user is an 'Admin' whatever that
	means (root on Unix), otherwise False.

	Warning: The inner function fails unless you have Windows XP SP2 or
	higher. The failure causes a traceback to be printed and this
	function to return False.
	"""

	if os.name == 'nt':
		import ctypes
		# WARNING: requires Windows XP SP2 or higher!
		try:
			return ctypes.windll.shell32.IsUserAnAdmin()
		except:
			traceback.print_exc()
			print("Admin check failed, assuming not an admin.")
			return False
	else:
		# Check for root on Posix
		return os.getuid() == 0


def run_as_admin(cmd_line=None, wait=True):
	"""Attempt to relaunch the current script as an admin using the same
	command line parameters.  Pass cmdLine in to override and set a new
	command.  It must be a list of [command, arg1, arg2...] format.

	Set wait to False to avoid waiting for the sub-process to finish. You
	will not be able to fetch the exit code of the process if wait is
	False.

	Returns the sub-process return code, unless wait is False in which
	case it returns None.

	@WARNING: this function only works on Windows.
	"""

	if os.name != 'nt':
		raise RuntimeError("This function is only implemented on Windows.")

	import win32con, win32event, win32process
	from win32com.shell.shell import ShellExecuteEx
	from win32com.shell import shellcon

	python_exe = sys.executable

	if cmd_line is None:
		cmd_line = [python_exe] + sys.argv
	elif type(cmd_line) not in (types.TupleType, types.ListType):
		raise ValueError("cmdLine is not a sequence.")
	cmd = '"%s"' % (cmd_line[0],)
	# XXX TODO: isn't there a function or something we can call to massage command line params?
	params = " ".join(['"%s"' % (x,) for x in cmd_line[1:]])
	# cmdDir = ''
	show_cmd = win32con.SW_SHOWNORMAL
	lp_verb = 'runas'  # causes UAC elevation prompt.

	# print "Running", cmd, params

	# ShellExecute() doesn't seem to allow us to fetch the PID or handle
	# of the process, so we can't get anything useful from it. Therefore
	# the more complex ShellExecuteEx() must be used.

	# procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

	proc_info = ShellExecuteEx(nShow=show_cmd,
								fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
								lpVerb=lp_verb,
								lpFile=cmd,
								lpParameters=params)

	if wait:
		proc_handle = proc_info['hProcess']
		obj = win32event.WaitForSingleObject(proc_handle, win32event.INFINITE)
		rc = win32process.GetExitCodeProcess(proc_handle)
	else:
		rc = None

	return rc


def test():
	"""A simple test function; check if we're admin, and if not relaunch the script as admin."""
	if not is_user_admin():
		print("You're not an admin.", os.getpid(), "params: ", sys.argv)
		rc = run_as_admin()
	else:
		print("You are an admin!", os.getpid(), "params: ", sys.argv)
		rc = 0
	input('Press Enter to exit.')
	return rc


if __name__ == "__main__":
	res = test()
	sys.exit(res)
