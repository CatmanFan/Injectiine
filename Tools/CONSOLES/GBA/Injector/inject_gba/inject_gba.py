#!/usr/bin/env python3

import	fnmatch
import	argparse
import	os

import	psb
import	global_vars

def	load_from_psb(psb_filename):
	if not psb_filename:
		return None

	if global_vars.verbose:
		print("Reading '%s'" % psb_filename)

	# Read in the encrypted/compressed psb data
	psb_data2 = bytearray(open(psb_filename, 'rb').read())

	# Decrypt the psb data using the filename as the key
	psb_data1 = psb.unobfuscate_data(psb_data2, psb_filename)
	if global_vars.verbose > global_vars.debug_level:
		open(psb_filename + '.1', 'wb').write(psb_data1)	# compressed

	if psb_filename.endswith('.psb'):
		# ".psb" files are not compressed, use the decrypted data
		psb_data0 = psb_data2
	else:
		# Uncompress the psb data
		psb_data0 = psb.uncompress_data(psb_data1)
		if global_vars.verbose > global_vars.debug_level:
			open(psb_filename + '.0', 'wb').write(psb_data0)	# raw

	# Check we have a PSB header
	header = psb.HDRLEN()
	header.unpack(psb.buffer_unpacker(psb_data0))
	if header.signature != b'PSB\x00':
		print("PSB header not found")
		return

	# Unpack the PSB structure
	mypsb = psb.PSB()
	mypsb.unpack(psb_data0)

	# Get the base filename without any .psb.m
	# '.psb.m' isn't a single extension :(
	if psb_filename.endswith('.psb'):
		base_filename = psb_filename[:-len('.psb')]
	elif psb_filename.endswith('.psb.m'):
		base_filename = psb_filename[:-len('.psb.m')]
	else:
		return


	# Read in the alldata.bin file if it exists
	bin_filename  = base_filename + '.bin'
	if os.path.isfile(bin_filename):
		if global_vars.verbose:
			print("Reading file %s" % bin_filename)
		bin_data = bytearray(open(bin_filename, 'rb').read())

		# Split the ADB data into each subfile.
		# The data is in compressed/encrypted form
		mypsb.split_subfiles(bin_data)

	return mypsb

# Write out our PSB
def	write_psb(mypsb, filename):
	if not mypsb or not filename:
		return

	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if global_vars.verbose:
		print("Writing '%s'" % filename)

	# Pack our PSB object into the on-disk format
	psb_data0 = mypsb.pack()
	if global_vars.verbose > global_vars.debug_level:
		open(filename + '.0', 'wb').write(psb_data0)	# raw

	if filename.endswith('.psb'):
		# Write out the data as-is
		open(filename, 'wb').write(psb_data0)

	elif filename.endswith('.psb.m'):
		# Compress the PSB data
		psb_data1 = psb.compress_data(psb_data0)
		if global_vars.verbose > global_vars.debug_level:
			open(filename + '.1', 'wb').write(psb_data1)	# compressed

		# Encrypt the PSB data using the filename as the key
		psb_data2 = psb.unobfuscate_data(psb_data1, filename)
		if global_vars.verbose > global_vars.debug_level:
			open(filename + '.2', 'wb').write(psb_data2)	# compressed/encrypted

		# Write out the compressed/encrypted PSB data
		open(filename, 'wb').write(psb_data2)

# Write out the ADB
def	write_bin(mypsb, psb_filename):
	if not mypsb or not psb_filename:
		return

	# Join the subfiles back into a single ADB
	bin_data = mypsb.join_subfiles()
	if bin_data is None:
		return

	if psb_filename.endswith('.psb'):
		basename = psb_filename[:-len('.psb')]
	elif psb_filename.endswith('.psb.m'):
		basename = psb_filename[:-len('.psb.m')]
	else:
		return

	filename = basename + '.bin'

	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if global_vars.verbose:
		print("Writing '%s'" % filename)

	open(filename, 'wb').write(bytes(bin_data))

def	write_rom(mypsb, filename):
	if not mypsb or not filename:
		return

	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if global_vars.verbose:
		print("Writing '%s'" % filename)

	mypsb.write_rom_file(filename)

def	read_rom(mypsb, filename):
	if not mypsb or not filename:
		return

	if global_vars.verbose:
		print("Reading '%s'" % filename)

	fd = open(filename, 'rb').read()
	mypsb.replace_rom_file(fd)


def	main():

	epilog="""
-----

To extract a rom:

%(prog)s --inpsb /path/to/alldata.psb.m --outrom /path/to/new.rom

This will:
* Read in /path/to/alldata{.psb.m, .bin}

* Save the rom as /path/to/new.rom

-----

To inject a rom:

%(prog)s --inpsb /path/to/original/alldata.psb.m --inrom /path/to/new.rom --outpsb /path/to/new/alldata.psb.m

This will:
* Read in /path/to/original/alldata{.psb.m, .bin}

* Replace the original rom with /path/to/new.rom

* Create /path/to/new/alldata{.psb.m, .bin}

-----
"""
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog=epilog)
	parser.add_argument('-v',	'--verbose',	dest='verbose',		help='verbose output',				action='count',		default=0)
	parser.add_argument(		'--inpsb',	dest='inpsb',		help='Read INPSB',				metavar='INPSB',	required=True)
	parser.add_argument(		'--outrom',	dest='outrom',		help='Write the rom file to OUTROM',		metavar='OUTROM')
	parser.add_argument(		'--inrom',	dest='inrom',		help='Replace the rom file with INROM',		metavar='INROM')
	parser.add_argument(		'--outpsb',	dest='outpsb',		help='Write new psb to OUTPSB',			metavar='OUTPSB')
	options = parser.parse_args()

	global_vars.verbose = options.verbose

	# We must have an inpsb (this should be enforced by the parser)
	if not options.inpsb:
		parser.print_help()
	mypsb = load_from_psb(options.inpsb)

	# If we have outrom, write it out
	if options.outrom:
		write_rom(mypsb, options.outrom)

	# If we have inrom, read it in
	if options.inrom:
		read_rom(mypsb, options.inrom)

	# If we have outpsb, write it out
	if options.outpsb:
		write_psb(mypsb, options.outpsb)
		write_bin(mypsb, options.outpsb)

if __name__ == "__main__":
	main()
