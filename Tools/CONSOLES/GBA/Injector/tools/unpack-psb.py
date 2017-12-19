#!/usr/bin/env python3

import	fnmatch
import	optparse
import	os

import	psb
import	global_vars


def	load_from_psb(psb_filename):

	if not options.quiet:
		print("Reading '%s'" % psb_filename)

	# Read in the encrypted/compressed psb data
	psb_data2 = bytearray(open(psb_filename, 'rb').read())

	# Decrypt the psb data using the filename, or --key if provided.
	if options.key:
		psb_data1 = psb.unobfuscate_data(psb_data2, options.key)
	else:
		psb_data1 = psb.unobfuscate_data(psb_data2, psb_filename)
	if options.debug:
		open(psb_filename + '.1', 'wb').write(psb_data1)	# compressed

	if psb_filename.endswith('.psb'):
		# ".psb" files are not compressed, use the decrypted data
		psb_data0 = psb_data2
	else:
		# Uncompress the psb data
		psb_data0 = psb.uncompress_data(psb_data1)
		if options.debug:
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
		if not options.quiet:
			print("Reading file %s" % bin_filename)
		bin_data = bytearray(open(bin_filename, 'rb').read())

		# Split the ADB data into each subfile.
		# The data is in compressed/encrypted form
		mypsb.split_subfiles(bin_data)

	return mypsb


def	load_from_yaml(yaml_filename):

	if not options.quiet:
		print("Reading '%s'" % yaml_filename)

	yaml_data = open(yaml_filename, 'rt').read()

	mypsb = psb.PSB()
	mypsb.load_yaml(yaml_data)

	# Read in our subfiles
	# This will update the PSB.fileinfo[] entries with the new lengths etc
	if not options.quiet:
		print("Reading subfiles")
	mypsb.read_all_subfiles(os.path.dirname(yaml_filename))

	# Read in our chunk files
	if not options.quiet:
		print("Reading chunk files")
	mypsb.read_chunks(os.path.dirname(yaml_filename))

	return mypsb


# Write out the yaml file
def	write_yaml(mypsb):
	filename = options.basename + '.yaml'

	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if not options.quiet:
		print("Writing '%s'" % filename)

	open(filename, 'wt').write(mypsb.print_yaml())

# Write out our PSB
def	write_psb(mypsb):
	filename = options.output

	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if not options.quiet:
		print("Writing '%s'" % filename)

	# Pack our PSB object into the on-disk format
	psb_data0 = mypsb.pack()
	if options.debug:
		open(filename + '.0', 'wb').write(psb_data0)	# raw

	if filename.endswith('.psb'):
		# Write out the data as-is
		open(filename, 'wb').write(psb_data0)

	elif filename.endswith('.psb.m'):
		# Compress the PSB data
		psb_data1 = psb.compress_data(psb_data0)
		if options.debug:
			open(filename + '.1', 'wb').write(psb_data1)	# compressed

		# Encrypt the PSB data
		if options.key:
			psb_data2 = psb.unobfuscate_data(psb_data1, options.key)
		else:
			psb_data2 = psb.unobfuscate_data(psb_data1, filename)
		if options.debug:
			open(filename + '.2', 'wb').write(psb_data2)	# compressed/encrypted

		# Write out the compressed/encrypted PSB data
		open(filename, 'wb').write(psb_data2)

# Write out our rom file
def	write_rom_file(mypsb):
	if not mypsb.fileinfo:
		return

	filename = options.basename + '.rom'
	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if not options.quiet:
		print("Writing '%s'" % filename)

	mypsb.write_rom_file(filename)

# Write out our subfiles
def	write_subfiles(mypsb):
	if not mypsb.fileinfo:
		return

	if not options.quiet:
		print("Writing subfiles")

	base_dir = options.basename + '.files'
	mypsb.write_all_subfiles(base_dir)

# Write out our chunks
def	write_chunks(mypsb):
	if not options.quiet:
		print("Writing chunk files")

	base_dir = options.basename + '.chunks'
	mypsb.write_chunks(base_dir)

# Write out the ADB
def	write_bin(mypsb):

	# Join the subfiles back into a single ADB
	bin_data = mypsb.join_subfiles()
	if bin_data is None:
		return

	filename = options.basename + '.bin'

	if os.path.isfile(filename):
		print("File '%s' exists, not over-writing" % filename)
		return

	if not options.quiet:
		print("Writing '%s'" % filename)

	open(filename, 'wb').write(bytes(bin_data))


def	replace_rom_file(mypsb):
	if options.rom:
		filename = options.rom
		if not options.quiet:
			print("Reading '%s'" % filename)

		fd = open(filename, 'rb').read()

		mypsb.replace_rom_file(fd)

def	main():

	class MyParser(optparse.OptionParser):
		def format_epilog(self, formatter):
			return self.expand_prog_name(self.epilog)

	parser = MyParser(usage='Usage: %prog [options] <filename>', epilog=
"""
-----
To insert a rom:

%prog -r /path/to/new.rom -o workdir/alldata.psb.m originaldir/alldata.psb.m

This will:
* Read in originaldir/alldata{.psb.m, .bin}

* Save the original rom in workdir/alldata.rom

* Replace the original rom with /path/to/new.rom

* Create workdir/alldata{.psb.m, .bin}
The file workdir/alldata.psb.m will be encrypted with 'alldata.psb.m'

-----
Examples:

%prog -o output.psb.m alldata.psb.m
This will:

* Read alldata.psb.m (and alldata.bin)
* Save the original rom in output.rom
* Create output{.psb.m, .bin}
The file output.psb.m will be encrypted with 'output.psb.m'


%prog -y -f -o output.psb.m alldata.psb.m

This will:
* Read alldata.psb.m (and alldata.bin)
* Create output{.psb.m, .bin}
* Create output.yaml
* Save any sub-files in output.files/
* Save any chunks in output.files/


%prog -o output2.psb.m -k mysecretkey output.yaml

This will:
* Read output.yaml (and output.files/* and output.chunks/*)
* Create output2{.psb.m, .bin}
The file output2.psb.m will be encrypted with 'mysecretkey'

""")
	parser.add_option('-q',	'--quiet',	dest='quiet',		help='quiet output',				action='store_true',	default=False)
	parser.add_option('-v',	'--verbose',	dest='verbose',		help='verbose output',				action='store_true',	default=False)
	parser.add_option('-d',	'--debug',	dest='debug',		help='debugging output',			action='store_true',	default=False)
	parser.add_option('-f',	'--files',	dest='files',		help='write output.files/*',			action='store_true',	default=False)
	parser.add_option('-y',	'--yaml',	dest='yaml',		help='write output.yaml',			action='store_true',	default=False)
	parser.add_option('-k',	'--key',	dest='key',		help='encrypt output.psb.m using KEY',		metavar='KEY')
	parser.add_option('-o',	'--output',	dest='output',		help='write new psb to OUTPUT',			metavar='OUTPUT')
	parser.add_option('-r',	'--rom',	dest='rom',		help='replace the rom file with ROM',		metavar='ROM')
	(options, args) = parser.parse_args()

	if options.verbose:
		global_vars.verbose = 1

	if not args:
		parser.print_help()

	# Remove the extension from the output filename
	if options.output:
		filename = options.output
		# '.psb.m' isn't a single extension :(
		if filename.endswith('.psb'):
			options.basename = filename[:-len('.psb')]
		elif filename.endswith('.psb.m'):
			options.basename = filename[:-len('.psb.m')]

	for filename in args:
		if filename.endswith('.psb') or filename.endswith('.psb.m'):
			mypsb = load_from_psb(filename)
		elif filename.endswith('.yaml'):
			mypsb = load_from_yaml(filename)

		if options.basename:
			# Make sure the directory exists
			base_dir = os.path.dirname(options.basename)
			if base_dir:
				os.makedirs(base_dir, exist_ok = True)

			# Write out the existing rom *before* we replace it
			write_rom_file(mypsb)

			replace_rom_file(mypsb)

			# Write out the YAML first for debugging
			if options.yaml:
				write_yaml(mypsb)

			write_psb(mypsb)
			write_bin(mypsb)

			if options.files:
				write_subfiles(mypsb)
				write_chunks(mypsb)


if __name__ == "__main__":
	main()
