
import	binascii
import	collections
import	ctypes
import	hashlib
import	html
import	mt19937
import	optparse
import	os
import	struct
import	sys
import	yaml
import	zlib

import	global_vars

#
# Define our object classes
#
# Note: we can't use __slots__ to save memory because that breaks __dict__ which we need for serialization
#
class	TypeValue(yaml.YAMLObject):
	yaml_tag = u'!TV'
	def	__init__(self, t, v):
		self.t = t
		self.v = v
	def	__repr__(self):
		return "%s(t=%r, v=%r)" % (self.__class__.__name__, self.t, self.v)

class	NameObject(yaml.YAMLObject):
	yaml_tag = u'!NO'
	def	__init__(self, ni, o, ns=None):
		self.ni = ni	# index into names[]
		self.o  = o	# object
		self.ns = ns	# For debugging, the name string from names[]
	def	__repr__(self):
		return "%s(ni=%r, o=%r, ns=%r)" % (self.__class__.__name__, self.ni, self.o, self.ns)

class	String(yaml.YAMLObject):
	yaml_tag = u'!STR'
	def	__init__(self, t, v, s=None):
		self.t = t
		self.v = v	# index into strings[]
		self.s = s	# For debugging, the string
	def	__repr__(self):
		return "%s(t=%r, v=%r, s=%r)" % (self.__class__.__name__, self.t, self.v, self.s)

class	FileInfo(yaml.YAMLObject):
	yaml_tag = u'!FI'
	def	__init__(self, ni, l, o,):
		self.ni	= ni	# index into names[]
		self.l	= l	# original length
		self.o	= o	# original offset
	def	__repr__(self):
		return "%s(ni=%r, l=%r, o=%r)" % (self.__class__.__name__, self.ni, self.l, self.o)

#
# get the size of an int in bytes
#
def	getIntSize(v):
	for s in range(1, 8):
		if v < (1 << (8 * s)):
			return s

def	getUnsignedIntSize(v):
	for s in range(1, 8):
		if v < (1 << (8 * s -1)):
			return s

class	buffer_packer():
	def __init__(self):
		self._buffer = []
		self._offset = 0	# points to the *next* byte to write

	def __call__(self, fmt, data):
		packed_data = struct.pack(fmt, data)
		packed_length = len(packed_data)
		self.setlength(self._offset + packed_length)
		self._buffer[self._offset : self._offset + packed_length] = packed_data
		self._offset += packed_length

	def	length(self):
		return len(self._buffer)

	def	seek(self, offset):
		self.setlength(offset)
		self._offset = offset

	def	setlength(self, length):
		if len(self._buffer) < length:
			self._buffer = self._buffer + [0] * (length - len(self._buffer))

	def	tell(self):
		return self._offset


'''
<	Little endian
>	Big endian
b	signed char
B	unsigned char
H	unsigned 2 bytes
I	unsigned 4 bytes
L	unsigned 4 bytes
Q	unsigned 8 bytes
'''

class	buffer_unpacker():
	def __init__(self, buffer):
		self._buffer = buffer
		self._offset = 0

	def __call__(self, fmt):
		result = struct.unpack_from(fmt, self._buffer, self._offset)
		self._offset += struct.calcsize(fmt)
		return result

	def	seek(self, offset):
		if offset >= 0 and offset < len(self._buffer):
			self._offset = offset
		return self._offset

	def	tell(self):
		return self._offset

	def	length(self):
		return len(self._buffer)

	def	data(self):
		return self._buffer[self._offset : ]

	# Get the next output without moving the offset
	def	peek(self, fmt):
		off = self.tell()
		out = self(fmt)
		self.seek(off)
		return out

	def	peek16(self):
		r = min(16, (self.length() - self.tell()))
		if r > 0:
			return self.peek('<%dB' % r)
		return "EOF"

	def	get_cstr(self):
		for next0 in range(self._offset, len(self._buffer)):
			if self._buffer[next0] == 0:
				s = self._buffer[self._offset : next0]
				self._offset = next0 + 1
				return s.decode('utf-8')

# mdf\0
# PSB\0
class	HDRLEN():
	def	__init__(self):
		self.offset0		= 0
		self.offset1		= 0
		self.signature		= []
		self.length		= 0

	def	pack(self, packer):
		packer('>4s',	self.signature)
		packer('<I',	self.length)

	def	unpack(self, unpacker):
		self.offset0		= unpacker.tell()
		self.signature		= unpacker('>4s')[0]
		self.length		= unpacker('<I')[0]
		self.offset1		= unpacker.tell()


'''

From exm2lib
struct PSBHDR {
	unsigned char signature[4];
	unsigned long type;
	unsigned long unknown1;
	unsigned long offset_names;
	unsigned long offset_strings;
	unsigned long offset_strings_data;
	unsigned long offset_chunk_offsets;
	unsigned long offset_chunk_lengths;
	unsigned long offset_chunk_data;
	unsigned long offset_entries;
};


'''

class	PSB():
	def	__init__(self):
		self.header		= PSB_HDR()

		# Raw copy of each of the sections.
		# If we do not modify anything we can paste these into the output file.
		self.raw_names			= None
		self.raw_entries		= None
		self.raw_strings_offsets	= None
		self.raw_strings_data		= None
		self.raw_chunk_offsets		= None
		self.raw_chunk_lengths		= None
		self.raw_chunk_data		= None

		self.names		= []	# list of strings indexed by NameObject.ni
		self.strings		= [] 	# list of strings index by Type 21-24
		self.chunkdata		= []	# raw data indexed by Type 25-28
		self.chunknames		= []	# CNNNN filenames for each chunk
		self.entries		= None
		self.fileinfo		= []	# Stash of FileInfo objects (easier than walking the entries tree)
		self.subfile_data	= None	# Copy of each subfile from ADB in encrypted/compressed form

	def	__str__(self):
		o = "PSB:\n"
		o += str(self.header)
		for i in range(0, len(self.names)):
			o += "Name %d %s\n" % (i, self.names[i])
		#o += "Strings %s\n" % str(self.strings)
		#o += "Strings Data %s\n" % self.strings_data
		for i in range(0, len(self.strings)):
			o += "String %d %s\n" % (i, self.strings[i])
		#o += "Chunk offsets %s\n" % str(self.chunk_offsets)
		#o += "Chunk lengths %s\n" % str(self.chunk_offsets)
		o += "Entries %s\n" % str(self.entries)
		#for i in range(0, self.entries.names.count):
		#	s = self.entries.names.values[i]
		#	o += "%d %d %s\n" % (i, s, self.name[s])
		return o

	def	pack(self):
		packer = buffer_packer()

		# Write out our dummy header
		self.header.signature	= b'PSB\x00'
		self.header.type	= 2
		self.header.pack(packer)

		# Pack the array of names
		self.pack_names(packer)

		# Pack our tree of entries
		self.pack_entries(packer)

		# Pack the array of strings
		self.pack_strings(packer)

		# Pack the array of chunks
		self.pack_chunks(packer)

		# Rewrite the header with the correct offsets
		packer.seek(0)
		self.header.pack(packer)

		return bytes(packer._buffer)

	def	unpack(self, psb_data):
		unpacker = buffer_unpacker(psb_data)

		if global_vars.verbose:
			print("Parsing header:")
			l = len(unpacker.data())
			print("PSB data length %d 0x%X" % (l, l))

		self.header.unpack(unpacker)
		if self.header.signature != b'PSB\x00':
			if global_vars.verbose > global_vars.debug_level:
				print("Not a PSB file")
				print(self.header.signature)
			return
		if global_vars.verbose:
			print(self.header)

		# Read in the arrays of names
		# These are a complex structure used to remove duplicate prefixes of the file names
		self.unpack_names(unpacker)

		# Read in the array of strings
		self.unpack_strings(unpacker)

		# Read in the array of chunks
		self.unpack_chunks(unpacker)

		# Read in our tree of entries
		self.unpack_entries(unpacker)

	def	print_yaml(self):
		# Create a top-level dict to dump
		level0 = {
			'raw_names':		self.raw_names,
			'raw_entries':		self.raw_entries,
			'raw_strings_offsets':	self.raw_strings_offsets,
			'raw_strings_data':	self.raw_strings_data,
			'raw_chunk_offsets':	self.raw_chunk_offsets,
			'raw_chunk_lengths':	self.raw_chunk_lengths,
			'raw_chunk_data':	self.raw_chunk_data,
			'names':	self.names,
			'strings':	self.strings,
			'chunknames':	self.chunknames,
			'entries':	self.entries,
			'fileinfo':	self.fileinfo,
		}
		return yaml.dump(level0)

	def	load_yaml(self, data):
		# FIXME - use yaml.safe_load
		level0 = yaml.load(data)
		if isinstance(level0, dict):
			self.raw_names			= level0['raw_names']
			self.raw_entries		= level0['raw_entries']
			self.raw_strings_offsets	= level0['raw_strings_offsets']
			self.raw_strings_data		= level0['raw_strings_data']
			self.raw_chunk_offsets		= level0['raw_chunk_offsets']
			self.raw_chunk_lengths		= level0['raw_chunk_lengths']
			self.raw_chunk_data		= level0['raw_chunk_data']

			self.names		= level0['names']
			self.strings		= level0['strings']
			self.chunknames		= level0['chunknames']
			self.entries		= level0['entries']
			self.fileinfo		= level0['fileinfo']

	# Read in our chunk files
	def	read_chunks(self, base_dir):
		self.chunkdata = []
		for cn in self.chunknames:
			filename = os.path.join(base_dir, cn)
			if global_vars.verbose:
				print("Reading chunk '%s'" % filename)
			data = open(filename, 'rb').read()
			self.chunkdata.append(data)

	# Write out our chunk files
	def	write_chunks(self, base_dir):
		# Make sure the output directory exists
		os.makedirs(base_dir, exist_ok = True)
		for i, fn in enumerate(self.chunknames):
			filename = os.path.join(base_dir, fn)
			if os.path.isfile(filename):
				print("File '%s' exists, not over-writing" % filename)
			else:
				if global_vars.verbose:
					print("Writing file %s" % filename)
				# Write out the chunk data
				open(filename, 'wb').write(self.chunkdata[i])

	# Update our FileInfo offset/lengths
	def	update_fileinfo(self):
		assert(len(self.subfile_data) == len(self.fileinfo))
		offset = 0
		for i, fi in enumerate(self.fileinfo):

			# Get the length of the subfile_data entry
			new_length = len(self.subfile_data[i])

			# If we are longer, we need to rewrite the entries section to record the larger size
			# If we are more than 0x800 bytes smaller, we need to rewrite the entries section to fix the offsets of each following entry
			if new_length > fi.l or (new_length + 0x800) < fi.l:
				if global_vars.verbose:
					print("File '%s' length differs, re-writing entries table" % self.names[fi.ni])
					print("Old length %d 0x%X" % (fi.l, fi.l))
					print("New length %d 0x%X" % (new_length, new_length))
				# Clear the cached entries block
				self.raw_entries = None

			# If our offset has changed, we need to rewrite the entries section
			if offset != fi.o:
				# Don't warn about this, they could all be different
				# Clear the cached entries block
				self.raw_entries = None

			# Update the PSB's FileInfo with the new length, offset
			# The FileInfo holds the unpadded length
			self.fileinfo[i].o = offset
			self.fileinfo[i].l = new_length

			# Round the length to a multiple of 0x800 bytes to simulate the padding
			if new_length % 0x800:
				new_length += 0x800 - (new_length % 0x800)

			# Advance our running offset by the padded length
			offset += new_length

	# Join our subfile data array into a single alldata.bin array
	def	join_subfiles(self):
		if not self.fileinfo:
			return

		self.update_fileinfo()

		bin_data	= []
		for i, fi in enumerate(self.fileinfo):

			# Take a copy of the data (so we don't pad the entry in subfile_data)
			fd = self.subfile_data[i][:]

			# Get the unpadded length
			new_length = len(fd)

			# Pad the data to a multiple of 0x800 bytes
			if new_length % 0x800:
				fd += b'\x00' * (0x800 - new_length % 0x800)
			if global_vars.verbose:
				print("Padded length %d 0x%X" % (len(fd), len(fd)))

			# Add the self.subfile to the ADB array
			bin_data.extend(fd)

		return bin_data

	# Read in all our subfiles into a subfile_data array.
	# The data is compressed/encrypted
	def	read_all_subfiles(self, base_dir):
		self.subfile_data	= [None] * len(self.fileinfo)
		for i in range(len(self.fileinfo)):
			self.read_subfile(base_dir, i)

	# Read in a single subfile and return the data
	# The data is compressed/encrypted
	def	read_subfile(self, base_dir, i):
		fi = self.fileinfo[i]
		if global_vars.verbose:
			print("Reading '%s'" % (self.names[fi.ni]))

		# Read in the raw data
		fd = open(os.path.join(base_dir, self.names[fi.ni]), 'rb').read()
		#print("Len %d" % len(fd))

		# Compress/Encrypt and save the data.
		self.replace_subfile(i, fd)

	# Replace the subfile_data entry for the first 'system/roms' file with the given rom data
	def	replace_rom_file(self, fd):
		for i, fi in enumerate(self.fileinfo):
			if 'system/roms' in self.names[fi.ni]:
				print("Replacing '%s'" % self.names[fi.ni])
				self.replace_subfile(i, fd)
				break

	# Compress/Encrypt and save the given data for a single subfile.
	def	replace_subfile(self, i, fd0):
		fi = self.fileinfo[i]

		if global_vars.verbose:
			print("Raw length %d 0x%X" % (len(fd0), len(fd0)))

		# We save sub-psb files as-is
		if self.names[fi.ni].endswith('.psb') or self.names[fi.ni].endswith('.psb.m'):
			fd2 = fd0[:]
		else:
			# Compress the data
			if self.names[fi.ni].endswith('.jpg.m'):
				# JPEG files are stored with minimal compression
				fd1 = compress_data(fd0, 0)
			else:
				fd1 = compress_data(fd0, 9)

			# Obfuscate the data using the original filename for the seed
			fd2 = unobfuscate_data(fd1, self.names[fi.ni])

		if global_vars.verbose:
			print("Compressed length %d 0x%X" % (len(fd2), len(fd2)))

		# Save the compressed/encrypted data in our subfile array
		self.subfile_data[i] = fd2

		# Check the length here.
		# If we are longer, we need to rewrite the entries section to record the larger size.
		# If we are more than 0x800 bytes smaller, we need to rewrite the entries section to fix the offsets of each following entry
		new_length = len(fd2)
		if new_length > fi.l or (new_length + 0x800) < fi.l:
			if global_vars.verbose:
				print("File '%s' length differs, re-writing entries table" % self.names[fi.ni])
				print("Old length %d 0x%X" % (fi.l, fi.l))
				print("New length %d 0x%X" % (new_length, new_length))
			# Clear the cached entries block
			self.raw_entries = None


	# Split our subfiles
	# This splits the alldata.bin data into each sub-file
	# The data is left encrypted/compressed form to save time
	def	split_subfiles(self, bin_data):
		self.subfile_data = []
		for i, fi in enumerate(self.fileinfo):
			#print("%d %s" % (i, fi))
			if global_vars.verbose:
				print("Extracting file %s" % self.names[fi.ni])

			# Get the chunk of data from the alldata.bin file
			fd = bin_data[fi.o : fi.o + fi.l]

			# Add the chunk to our array
			self.subfile_data.append(fd)

	# Extract the subfile_data entry for the first 'system/roms' file.
	# The file data is unencrypted/uncompressed.
	def	write_rom_file(self, filename):
		for i, fi in enumerate(self.fileinfo):
			if 'system/roms' in self.names[fi.ni]:
				self.write_subfile(i, filename)
				break

	# Write out all our subfiles to their disk files.
	# The file data is unencrypted/uncompressed.
	def	write_all_subfiles(self, base_dir):
		if not self.fileinfo:
			return

		assert(len(self.subfile_data) == len(self.fileinfo))
		for i in range(len(self.fileinfo)):
			fi = self.fileinfo[i]
			filename = os.path.join(base_dir, self.names[fi.ni])
			self.write_subfile(i, filename)

	# Write out a single subfile to it's disk file.
	# The file data is unencrypted/uncompressed.
	def	write_subfile(self, i, filename):
		if os.path.isfile(filename):
			print("File '%s' exists, not over-writing" % filename)
			return

		fi = self.fileinfo[i]
		if global_vars.verbose:
			print("Writing '%s'" % filename)
	
		# Make sure the output directory exists
		os.makedirs(os.path.dirname(filename), exist_ok = True)

		# Get a copy of the encrypted/compressed data from our array
		fd2 = self.subfile_data[i][:]
		if global_vars.verbose > global_vars.debug_level:
			open(filename + '.2', 'wb').write(fd2)

		# Compress the data
		if self.names[fi.ni].endswith('.psb') or self.names[fi.ni].endswith('.psb.m'):
			# Write out sub-psb files as-is
			fd0 = fd2
		else:
			# Unobfuscate the data using the original filename for the seed
			fd1 = unobfuscate_data(fd2, self.names[fi.ni])
			if global_vars.verbose > global_vars.debug_level:
				open(filename + '.1', 'wb').write(fd1)

			# Uncompress the data
			fd0 = uncompress_data(fd1)

		# Write out the subfile
		open(filename, 'wb').write(fd0)

	#
	# based on exm2lib get_number()
	#
	def	pack_object(self, packer, name, obj):
		t = obj.t
		if t >= 1 and t <= 3:
			packer('<B', t)
		elif t >=4 and t <= 12:
			# int, 0-8 bytes
			v = obj.v
			if v == 0:
				packer('<B', 4)
			else:
				s = getIntSize(v)
				packer('<B', 4 + s)
				packer('<%ds' % s, v.to_bytes(s, 'little'))
		elif t == 100:
			# Internal only.
			# unsigned int, 0-8 bytes
			# We make sure the most significant bit is not set.
			# Used when repacking the file_info offset, length fields
			v = obj.v
			if v == 0:
				packer('<B', 4)
			else:
				s = getUnsignedIntSize(v)
				packer('<B', 4 + s)
				packer('<%ds' % s, v.to_bytes(s, 'little'))
		elif t >= 13 and t <= 20:
			# array of ints, packed as size of count, count, size of entries, entries[]
			count = len(obj.v)
			s = getIntSize(count)
			packer('<B', 12 + s)
			packer('<%ds' % s, count.to_bytes(s, 'little'))
			# Find our biggest value
			if count:
				max_value = max(obj.v)
			else:
				max_value = 0
			# Pack the number of bytes in each value
			s = getIntSize(max_value)
			packer('<B', s + 12)
			# Pack each value
			for v in obj.v:
				packer('<%ds' % s, v.to_bytes(s, 'little'))
		elif t >= 21 and t <= 24:
			# index into 'strings' array (1-4 bytes)
			s = getIntSize(obj.v)
			packer('<B', 20 + s)
			packer('<%ds' % s, obj.v.to_bytes(s, 'little'))
		elif t >= 25 and t <= 28:
			# index into 'chunks' array, 1-4 bytes
			s = getIntSize(obj.v)
			packer('<B', 24 + s)
			packer('<%ds' % s, obj.v.to_bytes(s, 'little'))
		elif t == 29:
			# 0 byte float
			packer('<B', t)
		elif t == 30:
			# 4 byte float
			packer('<B', t)
			packer('f', obj.v)
		elif t == 31:
			# 8 byte float
			packer('<B', t)
			packer('d', obj.v)
		elif t == 32:
			# array of objects, written as array of offsets (int), array of objects
			packer('<B', t)

			# We need a list of offsets before the objects, so we have to pack each object into a temporary buffer to get the size
			next_offset	= 0
			temp_offsets	= []
			temp_data	= []
			for o in obj.v:
				# Pack our object into a temporary buffer to get the size
				temp_packer = buffer_packer()
				self.pack_object(temp_packer, '', o)

				# Remember our offset
				temp_offsets.append(next_offset)

				# Advance the next offset
				next_offset += temp_packer.length()

				# Remember our object data
				temp_data.append(bytes(temp_packer._buffer))

			# Pack the list of offsets
			self.pack_object(packer, '', TypeValue(13, temp_offsets))

			# Pack the object data
			for od in temp_data:
				l = len(od)
				packer('<%ds' % l, od)
		elif t == 33:
			# array of name/object pairs, written as array of name indexes, array of offsets, array of objects
			packer('<B', t)

			# If the type33 is a "file_info", we ignore the list in the tree and re-populate it from the PSB.fileinfo[]
			if name == '|file_info':
				print("Packing fileinfo struct (%d entries)" % len(self.fileinfo))
				# Make sure our offset/lengths are current
				self.update_fileinfo()

				obj.v=[]
				for fi in self.fileinfo:
					obj.v.append(NameObject(fi.ni, TypeValue(32, [TypeValue(100, fi.o), TypeValue(100, fi.l)]), self.names[fi.ni]))

			# We need a list of offsets before the objects, so we have to pack each object into a temporary buffer to get the size
			next_offset	= 0
			temp_names	= []
			temp_offsets	= []
			temp_data	= []
			for no in obj.v:
				if (type(no) != NameObject):
					print("Expected NameObject, got %s" % type(no))
				if global_vars.verbose:
					print("<<< %s %s" % (name, self.names[no.ni]))

				# Pack our object into a temporary buffer to get the size
				temp_packer = buffer_packer()
				self.pack_object(temp_packer, name + "|%s" % self.names[no.ni], no.o)

				# Remember our name index
				temp_names.append(no.ni)

				# Remember our offset
				temp_offsets.append(next_offset)

				# Advance the next offset
				next_offset += temp_packer.length()

				# Remember our object data
				temp_data.append(bytes(temp_packer._buffer))

			# Pack the list of names
			self.pack_object(packer, '', TypeValue(13, temp_names))

			# Pack the list of offsets
			self.pack_object(packer, '', TypeValue(13, temp_offsets))

			# Pack the object data
			for od in temp_data:
				l = len(od)
				packer('<%ds' % l, od)
		else:
			print("Unknown type")
			print(t)
			assert(False)

	def	unpack_object(self, unpacker, name):
		offset = unpacker.tell()
		if global_vars.verbose:
			print("")
			print(">>> %s @0x%X" % (name, unpacker.tell()))
			print(unpacker.peek16())
		t = unpacker.peek('<B')[0]
		if t >= 1 and t <= 3:
			# from exm2lib & inspection, length = 0, purpose unknown
			t = unpacker('<B')[0]
			v = 0
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value ?" % (name, offset, t))
			return TypeValue(t, None)
		elif t == 4:
			# int, 0 bytes
			t = unpacker('<B')[0]
			v = 0
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value %d 0x%X" % (name, offset, t, v, v))
			return TypeValue(t, 0)
		elif t >= 5 and t <= 12:
			# int, 1-8 bytes
			t = unpacker('<B')[0]
			v = int.from_bytes(unpacker('<%dB' % (t - 5 + 1)), 'little')
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value %d 0x%X" % (name, offset, t, v, v))
			return TypeValue(t, v)
		elif t >= 13 and t <= 20:
			# array of ints, packed as size of count, count, size of entries, entries[]
			t = unpacker('<B')[0]
			size_count = t - 12
			count = int.from_bytes(unpacker('<%dB' % size_count), 'little')
			size_entries = unpacker('<B')[0] - 12
			values = []
			for i in range(0, count):
				v = int.from_bytes(unpacker('<%dB' % size_entries), 'little')
				values.append(v)
			return TypeValue(t, values)
		elif t >= 21 and t <= 24:
			# index into strings array, 1-4 bytes
			t = unpacker('<B')[0]
			v = int.from_bytes(unpacker('<%dB' % (t - 21 + 1)), 'little')
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value string %d" % (name, offset, t, v))
			assert(v <= len(self.strings))
			return String(t, v, self.strings[v])
		elif t >= 25 and t <= 28:
			# index into chunks array, 1-4 bytes
			t = unpacker('<B')[0]
			v = int.from_bytes(unpacker('<%dB' % (t - 25 + 1)), 'little')
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value chunk %d" % (name, offset, t, v))
			assert(v <= len(self.chunkdata))
			return TypeValue(t, v)
		elif t == 29:
			# float, 0 bytes?
			t = unpacker('<B')[0]
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value ?" % (name, offset, t))
			return TypeValue(t, 0.0)
		elif t == 30:
			# float, 4 bytes
			t = unpacker('<B')[0]
			v = unpacker('f')[0]
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value %f" % (name, offset, t, v))
			return TypeValue(t, v)
		elif t == 31:
			# float, 8 bytes
			t = unpacker('<B')[0]
			v = unpacker('d')[0]
			if global_vars.verbose:
				print(">>> %s @0x%X type %d value %f" % (name, offset, t, v))
			return TypeValue(t, v)
		elif t == 32:
			# array of objects
			# from exm2lib, array of offsets of objects, followed by the objects
			t = unpacker('<B')[0]
			offsets = self.unpack_object(unpacker, name + '|offsets')
			seek_base = unpacker.tell()
			if global_vars.verbose:
				print(">>> %s @0x%X (%d entries)" % (name, offset, len(offsets.v)))
			v = []
			for i in range(0, len(offsets.v)):
				o = offsets.v[i]
				if global_vars.verbose:
					print(">>> %s @0x%X entry %d:" % (name, offset, i))
				unpacker.seek(seek_base + o)
				v1 = self.unpack_object(unpacker, name + "|%d" % i)
				v.append(v1)
			return TypeValue(t, v)
		elif t == 33:
			# array of name-objects
			# from exm2lib, array of int name indexes, array of int offsets, followed by objects
			t = unpacker('<B')[0]
			names   = self.unpack_object(unpacker, name + '|names')
			offsets = self.unpack_object(unpacker, name + '|offsets')
			seek_base = unpacker.tell()
			assert(len(names.v) == len(offsets.v))
			if global_vars.verbose:
				print(">>> %s @0x%X (%d entries)" % (name, offset, len(names.v)))

			# For each entry in the name list...
			v = []
			for i, ni in enumerate(names.v):
				# Get the name string and the offset
				ns = self.names[ni]
				o = offsets.v[i]
				if global_vars.verbose:
					print(">>> %s|%s @0x%X entry %d:" % (name, ns, offset, i))
					print(unpacker.peek16())

				# Unpack the object at the offset
				unpacker.seek(seek_base + o)
				v1 = self.unpack_object(unpacker, name + "|%s" % ns)

				# Add the object to our list
				v.append(NameObject(ni, v1, self.names[ni]))

				# If we are a file_info list, each object is a type 32 collection containing the offset & length values of the file data in alldata.bin
				# We build a list of FileInfo objects in the PSB for easy access, then mostly ignore the list in the tree.
				if name == '|file_info':

					# Sanity check our object
					assert(v1.t == 32)
					assert(len(v1.v) == 2)
					assert(v1.v[0].t >= 4)
					assert(v1.v[0].t <= 12)
					assert(v1.v[1].t >= 4)
					assert(v1.v[1].t <= 12)

					# Get the offset and length
					fo = v1.v[0].v
					fl = v1.v[1].v

					# Save the FileInfo in our stash
					self.fileinfo.append(FileInfo(ni, fl, fo))

			return TypeValue(t, v)

		else:
			print(">>> %s @0x%X" % (name, offset))
			print("Unknown type")
			print(unpacker.peek16())

	# Get the chunk filename
	def	getChunkFilename(self, chunk_index):
		name = "C%4.4d" % chunk_index
		return name
		
	def	pack_chunks(self, packer):
		# Build a lists of offsets and lengths
		offsets = []
		lengths	= []
		offset = 0
		for i in range(0, len(self.chunkdata)):
			l = len(self.chunkdata[i])
			offsets.append(offset)
			lengths.append(l)
			offset += l

		# Pack our offsets array
		self.header.offset_chunk_offsets	= packer.tell()
		if self.raw_chunk_offsets:
			packer('<%ds' % len(self.raw_chunk_offsets), bytes(self.raw_chunk_offsets))
		else:
			self.pack_object(packer, 'chunk_offsets', TypeValue(13, offsets))

		# Pack our lengths array
		self.header.offset_chunk_lengths	= packer.tell()
		if self.raw_chunk_lengths:
			packer('<%ds' % len(self.raw_chunk_lengths), bytes(self.raw_chunk_lengths))
		else:
			self.pack_object(packer, 'chunk_lengths', TypeValue(13, lengths))

		# Pack our data
		self.header.offset_chunk_data		= packer.tell()
		if self.raw_chunk_data:
			packer('<%ds' % len(self.raw_chunk_data), bytes(self.raw_chunk_data))
		else:
			for i in range(0, len(self.chunkdata)):
				packer('<%ds' % len(self.chunkdata[i]), self.chunkdata[i])
		
	def	unpack_chunks(self, unpacker):
		self.chunkdata		= []

		# Read in our chunk offsets array (this may be empty)
		unpacker.seek(self.header.offset_chunk_offsets)
		chunk_offsets = self.unpack_object(unpacker, 'chunk_offsets')
		if global_vars.verbose:
			print("Chunk offsets count %d" % len(chunk_offsets.v))
			for i in range(0, len(chunk_offsets.v)):
				print("Chunk offset %d = %d 0x%X" % (i, chunk_offsets.v[i], chunk_offsets.v[i]))
		self.raw_chunk_offsets = unpacker._buffer[self.header.offset_chunk_offsets : unpacker.tell()]


		# Read in our chunk lengths array (this may be empty)
		unpacker.seek(self.header.offset_chunk_lengths)
		chunk_lengths = self.unpack_object(unpacker, 'chunk_lengths')
		if global_vars.verbose:
			print("Chunk lengths count %d" % len(chunk_lengths.v))
			for i in range(0, len(chunk_lengths.v)):
				print("Chunk length %d = %d 0x%X" % (i, chunk_lengths.v[i], chunk_lengths.v[i]))
		self.raw_chunk_lengths = unpacker._buffer[self.header.offset_chunk_lengths : unpacker.tell()]

		assert(len(chunk_offsets.v) == len(chunk_lengths.v))

		# If we have chunk data, split it out
		unpacker.seek(self.header.offset_chunk_data)
		if len(chunk_offsets.v) > 0 and self.header.offset_chunk_data < len(unpacker.data()):
			for i in range(0, len(chunk_offsets.v)):
				o = chunk_offsets.v[i]
				l = chunk_lengths.v[i]

				# Save the chunk data
				unpacker.seek(self.header.offset_chunk_data + o)
				d = unpacker.data()[:l]
				self.chunkdata.append(d)

				# Save the chunk filename
				self.chunknames.append(self.getChunkFilename(i))
		self.raw_chunk_data = unpacker._buffer[self.header.offset_chunk_data : unpacker.tell()]

	def	pack_entries(self, packer):
		if self.raw_entries:
			self.header.offset_entries		= packer.tell()
			packer('<%ds' % len(self.raw_entries), bytes(self.raw_entries))
		else:
			self.header.offset_entries = packer.tell()
			self.pack_object(packer, '', self.entries)

	def	unpack_entries(self, unpacker):
		unpacker.seek(self.header.offset_entries)
		self.entries = self.unpack_object(unpacker, '')
		self.raw_entries = unpacker._buffer[self.header.offset_entries : unpacker.tell()]

	def	pack_names(self, packer):
		if self.raw_names:
			self.header.offset_names		= packer.tell()
			packer('<%ds' % len(self.raw_names), bytes(self.raw_names))
		else:
			# Encode the self.names array back into 3 arrays
			nt = PSB_NameTable()
			nt.build_tables(self.names)

			self.header.offset_names		= packer.tell()
			self.pack_object(packer, 'offsets', TypeValue(13, nt.offsets))
			self.pack_object(packer, 'jumps',   TypeValue(13, nt.jumps))
			self.pack_object(packer, 'starts',  TypeValue(13, nt.starts))

	def	unpack_names(self, unpacker):

		unpacker.seek(self.header.offset_names)

		nt = PSB_NameTable()
		nt.offsets	= self.unpack_object(unpacker, 'offsets').v
		nt.jumps	= self.unpack_object(unpacker, 'jumps').v
		nt.starts	= self.unpack_object(unpacker, 'starts').v

		# Decode the 3 arrays into simple strings
		self.names		= []
		for i in range(0, len(nt.starts)):
			s = nt.get_name(i).rstrip('\0')
			self.names.append(s)
			if global_vars.verbose:
				print("Name %d %s" % (i, s))

		self.raw_names = unpacker._buffer[self.header.offset_names : unpacker.tell()]

		if global_vars.verbose > global_vars.debug_level:
			nt2 = PSB_NameTable()
			nt2.build_tables(self.names)
			# Confirm the nt2 build works ok
			for i in range(0, len(nt.starts)):
				# FIXME - should not need the rstrip
				s1 = nt.get_name(i).rstrip('\0')
				s2 = nt2.get_name(i).rstrip('\0')
				if s1 != s2:
					print(">%d %d '%s'" % (i, len(s1), s1))
					print(">%d %d '%s'" % (i, len(s2), s2))
			# Dump the node trees to see what differs
			nt.build_debug_tree("NT1")
			nt2.build_debug_tree("NT2")

	#
	# Pack our strings[] array, and update our header with the offsets
	#
	def	pack_strings(self, packer):
		# Build the list of offsets
		offsets = []
		offset = 0
		for s in self.strings:
			se = s.encode('utf-8')
			l = len(se) +1	# +1 for the NUL byte
			offsets.append(offset)
			offset += l

		# Pack our offsets array object
		self.header.offset_strings		= packer.tell()
		if self.raw_strings_offsets:
			packer('<%ds' % len(self.raw_strings_offsets), bytes(self.raw_strings_offsets))
		else:
			self.pack_object(packer, 'strings', TypeValue(13, offsets))

		# Pack our data
		self.header.offset_strings_data	= packer.tell()
		if self.raw_strings_data:
			packer('<%ds' % len(self.raw_strings_data), bytes(self.raw_strings_data))
		else:
			for s in self.strings:
				se = s.encode('utf-8')
				l = len(se) +1	# +1 for the NUL byte
				packer('<%ds' % l, se)

	def	unpack_strings(self, unpacker):
		self.strings	= []

		unpacker.seek(self.header.offset_strings)
		strings_array	= self.unpack_object(unpacker, 'strings')
		self.raw_strings_offsets = unpacker._buffer[self.header.offset_strings : unpacker.tell()]

		if global_vars.verbose:
			print("Parsing strings array (%d)" % len(strings_array.v))
		# Read in each string
		for i in range(0, len(strings_array.v)):
			o = strings_array.v[i]
			# Create a python string from the NUL-terminated C-string at offset
			unpacker.seek(self.header.offset_strings_data + o)
			s = unpacker.get_cstr();
			self.strings.append(s)
			if global_vars.verbose:
				print("String %d  @0x%X %s" % (i, o, s))
		self.raw_strings_data = unpacker._buffer[self.header.offset_strings_data : unpacker.tell()]

class	PSB_HDR():
	def	__init__(self):
		self.signature			= []
		self.type			= 0
		# In some (all?) sub PSBs, unknown1 has the same value as offset_names
		self.unknown1			= 0
		self.offset_names		= 0
		self.offset_strings		= 0
		self.offset_strings_data	= 0
		self.offset_chunk_offsets	= 0
		self.offset_chunk_lengths	= 0
		self.offset_chunk_data		= 0
		self.offset_entries		= 0

	def	__str__(self):
		o = "PSB header:\n"
		o += "signature %s\n"			% self.signature
		o += "type 0x%X\n"			% self.type
		o += "unknown1 0x%X\n"			% self.unknown1
		o += "offset_names 0x%X\n"		% self.offset_names
		o += "offset_strings 0x%X\n"		% self.offset_strings
		o += "offset_strings_data 0x%X\n"	% self.offset_strings_data
		o += "offset_chunk_offsets 0x%X\n"	% self.offset_chunk_offsets
		o += "offset_chunk_lengths 0x%X\n"	% self.offset_chunk_lengths
		o += "offset_chunk_data 0x%X\n"		% self.offset_chunk_data
		o += "offset_entries 0x%X\n"		% self.offset_entries
		return o


	def	pack(self, packer):
 		packer('>4s',	bytes(self.signature))
 		packer('<I',	self.type)
 		packer('<I',	self.unknown1)
 		packer('<I',	self.offset_names)
 		packer('<I',	self.offset_strings)
 		packer('<I',	self.offset_strings_data)
 		packer('<I',	self.offset_chunk_offsets)
 		packer('<I',	self.offset_chunk_lengths)
 		packer('<I',	self.offset_chunk_data)
 		packer('<I',	self.offset_entries)

	def	unpack(self, unpacker):
		self.signature			= unpacker('>4s')[0]
		self.type			= unpacker('<I')[0]
		self.unknown1			= unpacker('<I')[0]
		self.offset_names		= unpacker('<I')[0]
		self.offset_strings		= unpacker('<I')[0]
		self.offset_strings_data	= unpacker('<I')[0]
		self.offset_chunk_offsets	= unpacker('<I')[0]
		self.offset_chunk_lengths	= unpacker('<I')[0]
		self.offset_chunk_data		= unpacker('<I')[0]
		self.offset_entries		= unpacker('<I')[0]

#
# Get the XOR key for the given filename
#
def	get_xor_key(filename):
	fixed_seed	= b'MX8wgGEJ2+M47'	# From m2engage.elf
	key_length	= 0x50

	# Take our game hash_seed (always the same), and append our filename
	hash_seed = fixed_seed + os.path.basename(filename).lower().encode('latin-1')
	if global_vars.verbose:
		print("Using hash seed:\t%s" % hash_seed)

	# Take the MD5 hash of the seed+filename
	hash_as_bytes = hashlib.md5(hash_seed).digest()
	hash_as_longs = struct.unpack('<4I', hash_as_bytes)

	# Initialize our mersenne twister
	mt19937.init_by_array(hash_as_longs)

	# Start with an empty key buffer
	key_buffer = bytearray()

	# Initialize our key from the MT
	while len(key_buffer) < key_length:
		# Get the next 32 bits from our MT-PRNG, as a long
		l = mt19937.genrand_int32();
		# Convert to 4 bytes little-endian
		s = struct.pack('<L', l)

		# Add them to our key buffer
		key_buffer.extend(s)
	if global_vars.verbose:
		print("Using key:\t%s," % binascii.hexlify(bytes(key_buffer)))

	return key_buffer
	

#
# Unobfuscate the data
# This returns a copy of the unobfuscated data and leaves the original untouched.
#
def	unobfuscate_data(original_data, filename):
	data = original_data[:]

	header = HDRLEN()
	header.unpack(buffer_unpacker(data))

	if header.signature == b'mdf\x00':
		if global_vars.verbose:
			print("sig=%s" % header.signature)
			print("len=%d (0x%X)" % (header.length, header.length))

		key_buffer = get_xor_key(filename)

		# For each byte after the HDRLEN, XOR in our key
		key_len = len(key_buffer)
		for i in range(len(data) - header.offset1):
			data[i + header.offset1] ^= key_buffer[i % key_len]

	return data

#
# Compress the data and prepend a mdf header
#
def	compress_data(data, level = 9):
	packer = buffer_packer()

	# Create a header
	header = HDRLEN()
	header.signature = b'mdf\x00'
	header.length = len(data)
	header.pack(packer)

	# Compressed the data
	try:
		compressed = zlib.compress(data, level)
		packer('<%ds'% len(compressed), compressed)
	except Exception as e:
		# We could not compress it, use the uncompressed data
		print("Compression failed", e)
		packer('<%ds' % len(data), data)

	return bytearray(packer._buffer)

#
# Uncompress the data
# This returns a separate set of data
# (Daft python call-by-object)
#
def	uncompress_data(data):
	header = HDRLEN()
	header.unpack(buffer_unpacker(data))

	if header.signature == b'mdf\x00':
		# FIXME - need to test if the data really is compressed
		# (Skip the 8 byte MDF header)
		uncompressed = zlib.decompress(bytes(data[header.offset1 : ]))
		if (len(uncompressed) != header.length):
			print("Warning: uncompressed length %d does not match header length %d" % (len(uncompressed), header.length))
		if global_vars.verbose:
			print("Uncompressed Length: %d 0x%X" % (len(uncompressed), len(uncompressed)))
		return uncompressed
	else:
		# Return the data as-is
		return data


#
# Observations:
#
# 1. The jumps can be forwards or backwards
#
# 2.  We constrain the position so the offset is always >= 1
# This is not critical to the algorithm, but avoids size/sign issues when extracting.
# (This is "e = b - d" below).
#
# 3. The same offset is applied to each branch which arrives at a given node.
#
# Because of (1) we can start searching for free locations from the start of the table each time.
#
# Because of (2) we must constrain our search for new table locations to more than the new character.
#
# Because of (3) the node's children must be stored with the same relative offsets.
# If we encode these strings
# A B C
# A B D
# A B F
# The C,D,F can not be contiguous, they must be stored C,D,?,F
# There is no requirement that the C,D,?,F are stored after A,B, only the relative spacing within one set of children is fixed
#
# The simple solution is to always add sets of children to the end of the table.
# Possible optimizations:
# Search the table for a gap large enough to hold the set.
# Insert the sets ordered by decreasing set size.
# Insert the sets ordered by decreasing min-max range.
# In practice, these are not needed.


# PSB_Node:
# This describes a single character in our 'names' table
class	PSB_Node:
	def	__init__(self):
		# These describe each character in our list of names
		self.id		= 0	# Our index into the PSB_NodeTree.nodes list
		self.p		= 0	# Our parent index into the PSB_NodeTree.nodes list
		self.cn		= []	# Our children (index into the PSB_NodeTree.nodes list)
		self.c		= 0	# This node's character
		# These are used to build the PSB_NameTable tables:
		self.ji		= 0	# This holds the index into the PSB_NameTable.jumps list
	def	__repr__(self):
		return "%s(id=%r, p=%r, cn=%r, c=%r)" % (self.__class__.__name__, self.id, self.p, self.cn, self.c)

# PSB_NodeTree:
class	PSB_NodeTree:
	def	__init__(self):
		self.nodes		= []	# List of PSB_Node objects
		self.starting_nodes	= []	# list of indexes into self.nodes

	def	reverse_walk(self, ni):
		if ni == 0:
			return ""
		else:
			c = self.nodes[ni].c
			return self.reverse_walk(self.nodes[ni].p) + chr(c)

	def	add_strings(self, names):

		# Start with an an empty root node
		self.nodes		= []
		self.nodes.append(PSB_Node())

		self.starting_nodes	= []

		# For each string in our list...
		#for name_idx, name_str in enumerate(sorted(names, key=len)):
		for name_idx in range(len(names)):
			name_str = names[name_idx]

			# Start searching the node tree from the top
			node_idx = 0

			# For each char in our string
			for c in name_str.encode('latin-1') + b'\x00':
				# Check if we match any of our children
				for child in self.nodes[node_idx].cn:
					if self.nodes[child].c == c:
						# Found match, use it
						node_idx = child
						break
				else:
					# Allocate a new node
					self.nodes.append(PSB_Node())
					next_idx = len(self.nodes)-1
					self.nodes[next_idx].id = next_idx

					# Set the new node's parent to us
					self.nodes[next_idx].p = node_idx

					# Add the new node to our list of children
					self.nodes[node_idx].cn.append(next_idx)

					# Set the new node to the new char
					self.nodes[next_idx].c = c

					# Point to the new node
					node_idx = next_idx
			else:
				# This is the last node for this string
				# Store the string# -> node
				self.starting_nodes.append(node_idx)

class	PSB_NameTable:
	def	__init__(self):
		self.jumps	= []
		self.offsets	= []
		self.starts	= []
		self.debug_tree	= None

	def	build_debug_tree(self, prefix):
		self.debug_tree	= [None] * len(self.jumps)
		for si in range(len(self.starts)):
			self.get_name(si)
		for ji in range(len(self.jumps)):
			print(prefix, end=" ")
			if not self.debug_tree[ji]:
				print("-")
			else:
				if self.debug_tree[ji].p +1 == ji:
					print("+ ", end="")
				print(self.debug_tree[ji])

	def	get_name(self, index):

		# Get the starting position
		a = self.starts[index]

		# Follow one jump to skip the terminating NUL
		# (Not critical to the walking algorithm)
		b = self.jumps[a]
		b = a

		DEBUG_SEEN	= 1

		if DEBUG_SEEN:
			seen = [0] * len(self.jumps)

		accum = ""

		while b != 0:
			# Get our parent jump index
			c = self.jumps[b]

			# Get the offset from our parent
			d = self.offsets[c]

			# Get our char. (our jump index - parent's offset)
			e = b - d

			# Sanity check our character
			if e < 0:
				print("b: %d " % b, end="")
				print("c: %d " % c, end="")
				print("d: %d " % d, end="")
				print("e: %d " % e, end="")
				print("")

			# Check for loops in the jump table
			if DEBUG_SEEN:
				seen[b] = 1
				if seen[c]:
					print("Loop detected in jump table:")
					print("b: %d " % b, end="")
					print("c: %d " % c, end="")
					print("d: %d " % d, end="")
					print("e: %d " % e, end="")
					print("")
					return accum

			# Prepend our char to our string
			accum = chr(e) + accum

			# If we are building a debug tree, fill in our node and our parent's node
			if self.debug_tree:
				if self.debug_tree[b] == None:
					self.debug_tree[b] = PSB_Node();
					self.debug_tree[b].id = b
				self.debug_tree[b].p = c
				self.debug_tree[b].c = e

				if self.debug_tree[c] == None:
					self.debug_tree[c] = PSB_Node();
					self.debug_tree[c].id = c
				if not b in self.debug_tree[c].cn:
					self.debug_tree[c].cn.append(b)

			# Move to our parent
			b = c

		return accum

	def	build_tables(self, names):
		self.jumps	= []
		self.offsets	= []
		self.starts	= []

		node_tree = PSB_NodeTree()
		node_tree.add_strings(names)

		self.build_jumps(node_tree)
		#self.build_jumps2(node_tree)
		self.build_offsets(node_tree)
		self.build_starts(node_tree)


	def	build_jumps(self, node_tree):
		for ni in range(len(node_tree.nodes)):
			# Skip the root node
			if ni:
				# We may have already processed this node (but not our children) when processing our parent.
				# If we have not already processed this node, find a position for it
				if node_tree.nodes[ni].ji == 0:
					# Constrain the index so the index-char offset >= 1
					min_ji = node_tree.nodes[ni].c + 1

					# Extend the table if needed
					if len(self.jumps) <= min_ji:
						self.jumps.extend([None] * (min_ji - len(self.jumps) +1))

					# Find the first unused jump entry
					for ji in range(min_ji, len(self.jumps)):
						if self.jumps[ji] is None:
							break
					else:
						# We didn't find one, extend the table
						# Set our jump index to the next unused entry
						ji = len(self.jumps)
						# Extend the table by 1
						self.jumps.extend([None] * 1)

					# Save our node's jump index
					node_tree.nodes[ni].ji = ji
					# Set our jump value to our parent's jump index
					p = node_tree.nodes[ni].p
					pji = node_tree.nodes[p].ji
					self.jumps[ji] = pji

			# If we have >1 children, add space for the range of chars
			# We could search for a gap, but it would be very unlikely.
			cn_count = len(node_tree.nodes[ni].cn)
			if cn_count > 1:
				# Get the min, max of our children's characters
				c_min = min(node_tree.nodes[ci].c for ci in node_tree.nodes[ni].cn)
				c_max = max(node_tree.nodes[ci].c for ci in node_tree.nodes[ni].cn)

				# Get the index of the first child
				ji_first = len(self.jumps)

				# Constrain the index so the index-char offset >= 1
				if ji_first < (c_min +1):
					ji_first = c_min +1

				# Get the index of the last child
				ji_last = ji_first - c_min + c_max

				# Extend the jump table
				self.jumps.extend([None] * (ji_last - len(self.jumps) +1))

				# For each child...
				for ci in node_tree.nodes[ni].cn:
					# Set our child node's jump index
					ji_child = ji_first - c_min + node_tree.nodes[ci].c
					node_tree.nodes[ci].ji = ji_child
					# Set our child's jump target to ourselves
					self.jumps[ji_child] = node_tree.nodes[ni].ji

		# Fix any remaining None entries
		fixed=0
		for ji in range(len(self.jumps)):
			if self.jumps[ji] is None:
				self.jumps[ji] = 0
				fixed += 1
		print("Fixed %d gaps" % fixed)

	# Brute-force search for gaps
	# This works ok-ish, but leaves more gaps than build_jumps1!
	def	build_jumps2(self, node_tree):
		self.jumps = [None] * len(node_tree.nodes)
		for ni in range(len(node_tree.nodes)):
			if node_tree.nodes[ni].ji == 0:
				# Find a space for ourselves
				for offset in range(1, len(self.jumps)):
					o = offset + node_tree.nodes[ni].c
					# Make sure the table is long enough
					if len(self.jumps) <= o:
						self.jumps.extend([None] * (o - len(self.jumps) +1))
						print("Extending jumps table to %d entries" % len(self.jumps))
					# If this entry is empty, we can use it.
					if self.jumps[o] is None:
						node_tree.nodes[ni].ji = o
						pi = node_tree.nodes[ni].p
						self.jumps[o] = node_tree.nodes[pi].ji
						# Quit the offset search loop
						break
				else:
					# We got to the end of the jumps table without finding a free slot - extend the table
					offset = len(self.jumps)
					o = offset + node_tree.nodes[ni].c
					# Make sure the table is long enough
					if len(self.jumps) <= o:
						self.jumps.extend([None] * (o - len(self.jumps) +1))
						print("Extending jumps table to %d entries" % len(self.jumps))
					# Use the new empty entry
					node_tree.nodes[ni].ji = o
					pi = node_tree.nodes[ni].p
					self.jumps[o] = node_tree.nodes[pi].ji
			# Find a space for our children
			for offset in range(1, len(self.jumps)):
				# For each child we have...
				for ci in node_tree.nodes[ni].cn:
					o = offset + node_tree.nodes[ci].c
					# Make sure the table is long enough
					if len(self.jumps) <= o:
						self.jumps.extend([None] * (o - len(self.jumps) +1))
						print("Extending jumps table to %d entries" % len(self.jumps))
					# If this entry is used, quit the child loop and try the next offset
					#print(ni, offset, o, len(self.jumps))
					if self.jumps[o] is not None:
						break
				else:
					# We have found a set of unused slots!
					# For each child...
					for ci in node_tree.nodes[ni].cn:
						o = offset + node_tree.nodes[ci].c
						# Make sure the table is long enough
						assert(len(self.jumps) > o)
						# Set our child node's jump index
						node_tree.nodes[ci].ji = o
						# Set our child's jump target to our jump index
						self.jumps[o] = node_tree.nodes[ni].ji
					# Quit the offset search loop
					break
			else:
				# We got to the end of the jumps table without finding a free slot - extend the table
				offset = len(self.jumps)
				# For each child...
				for ci in node_tree.nodes[ni].cn:
					o = offset + node_tree.nodes[ci].c
					# Make sure the table is long enough
					if len(self.jumps) <= o:
						self.jumps.extend([None] * (o - len(self.jumps) +1))
						print("Extending jumps table to %d entries" % len(self.jumps))
					# Set our child node's jump index
					node_tree.nodes[ci].ji = o
					# Set our child's jump target to our jump index
					self.jumps[o] = node_tree.nodes[ni].ji
		# Fix any remaining None entries
		fixed = 0
		for ji in range(len(self.jumps)):
			if self.jumps[ji] is None:
				self.jumps[ji] = 0
				fixed += 1
		print("Fixed %d gaps" % fixed)

	# Fill in the offsets table
	def	build_offsets(self, node_tree):

		# Start with a list of 0s
		self.offsets	= [0] * len(self.jumps)
		for ni in range(1, len(node_tree.nodes)):

			# Calculate our offset (jump index - character)
			o = node_tree.nodes[ni].ji - node_tree.nodes[ni].c

			# Sanity check this meets our >=1
			if o < 1:
				print("ni: %d " % ni, end="")
				print("o: %d " % o, end="")
				print("len(self.jumps): %d " % len(self.jumps), end="")
				print("")
			assert(o >= 1)

			# Get our parent
			p	= node_tree.nodes[ni].p

			# Get our parent's jump index
			pji	= node_tree.nodes[p].ji
			assert(pji >= 0)
			assert(pji < len(self.offsets))

			# Record the offset in our parent
			self.offsets[pji] = o

	# Fill in the starts table
	def	build_starts(self, node_tree):

		# Start with an empty list
		self.starts	= []

		# For each starting node in the node tree
		for si in node_tree.starting_nodes:

			# Get the jump index from the starting node
			ji = node_tree.nodes[si].ji

			# Add it to our list
			self.starts.append(ji)
