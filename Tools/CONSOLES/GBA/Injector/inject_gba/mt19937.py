#!/usr/bin/python3

## a C -> python translation of MT19937, original license below ##

##  A C-program for MT19937: Real number version
##    genrand() generates one pseudorandom real number (double)
##  which is uniformly distributed on [0,1]-interval, for each
##  call. sgenrand(seed) set initial values to the working area
##  of 624 words. Before genrand(), sgenrand(seed) must be
##  called once. (seed is any 32-bit integer except for 0).
##  Integer generator is obtained by modifying two lines.
##    Coded by Takuji Nishimura, considering the suggestions by
##  Topher Cooper and Marc Rieffel in July-Aug. 1997.

##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Library General Public
##  License as published by the Free Software Foundation; either
##  version 2 of the License, or (at your option) any later
##  version.
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
##  See the GNU Library General Public License for more details.
##  You should have received a copy of the GNU Library General
##  Public License along with this library; if not, write to the
##  Free Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
##  02111-1307  USA

##  Copyright (C) 1997 Makoto Matsumoto and Takuji Nishimura.
##  Any feedback is very welcome. For any question, comments,
##  see http://www.math.keio.ac.jp/matumoto/emt.html or email
##  matumoto@math.keio.ac.jp


import sys
import	ctypes
# for debugging
import	binascii

# Period parameters
N = 624
M = 397
MATRIX_A = 0x09908b0df   # constant vector a
UPPER_MASK = 0x080000000 # most significant w-r bits
LOWER_MASK = 0x07fffffff # least significant r bits

# Tempering parameters
TEMPERING_MASK_B = 0x9d2c5680
TEMPERING_MASK_C = 0xefc60000

def TEMPERING_SHIFT_U(y):
    return (y >> 11)

def TEMPERING_SHIFT_S(y):
    return (y << 7)

def TEMPERING_SHIFT_T(y):
    return (y << 15)

def TEMPERING_SHIFT_L(y):
    return (y >> 18)

mt = []   # the array for the state vector
mti = N+1 # mti==N+1 means mt[N] is not initialized

# initializing the array with a NONZERO seed
"""
/* initializes mt[N] with a seed */
void init_genrand(unsigned long s)
{
    mt[0]= s & 0xffffffffUL;
    for (mti=1; mti<N; mti++) {
        mt[mti] = 
	    (1812433253UL * (mt[mti-1] ^ (mt[mti-1] >> 30)) + mti); 
        /* See Knuth TAOCP Vol2. 3rd Ed. P.106 for multiplier. */
        /* In the previous versions, MSBs of the seed affect   */
        /* only MSBs of the array mt[].                        */
        /* 2002/01/09 modified by Makoto Matsumoto             */
        mt[mti] &= 0xffffffffUL;
        /* for >32 bit machines */
    }
}
"""
def init_genrand(seed):
  # setting initial seeds to mt[N] using
  # the generator Line 25 of Table 1 in
  # [KNUTH 1981, The Art of Computer Programming
  #    Vol. 2 (2nd Ed.), pp102]

	#print("init_genrand", seed)
	global mt, mti

	mt = [None] * N
	mt[0] = ctypes.c_uint32(seed).value

	mti = 1
	while (mti < N):
		mt[mti] = ctypes.c_uint32(1812433253 * (mt[mti - 1] ^ (mt[mti - 1] >> 30)) + mti).value
		mti += 1
	return
	print("mti %d" % mti)
	for i in range(0, N):
		print("%X" % mt[i])
# end init_genrand

"""
/* initialize by an array with array-length */
/* init_key is the array for initializing keys */
/* key_length is its length */
/* slight change for C++, 2004/2/26 */
void init_by_array(unsigned long init_key[], int key_length)
{
    int i, j, k;
    init_genrand(19650218UL);
    i=1; j=0;
    k = (N>key_length ? N : key_length);
    for (; k; k--) {
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525UL))
          + init_key[j] + j; /* non linear */
        mt[i] &= 0xffffffffUL; /* for WORDSIZE > 32 machines */
        i++; j++;
        if (i>=N) { mt[0] = mt[N-1]; i=1; }
        if (j>=key_length) j=0;
    }
    for (k=N-1; k; k--) {
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941UL))
          - i; /* non linear */
        mt[i] &= 0xffffffffUL; /* for WORDSIZE > 32 machines */
        i++;
        if (i>=N) { mt[0] = mt[N-1]; i=1; }
    }

    mt[0] = 0x80000000UL; /* MSB is 1; assuring non-zero initial array */ 
}
"""
def	init_by_array(init_key):
	key_length = len(init_key)

	#print("init_by_array len", key_length)

	init_genrand(19650218)
	i = 1
	j = 0
	k = N if N > key_length else key_length
	while (k > 0):
		mt[i] = ctypes.c_uint32((mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525)) + init_key[j] + j).value
		i += 1
		j += 1
		if (i >= N):
			mt[0] = mt[N - 1]
			i = 1
		if (j >= key_length):
			j = 0
		k -= 1

	k = N - 1
	while (k > 0):
		mt[i] = ctypes.c_uint32((mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941)) - i).value
		i += 1
		if (i >= N):
			mt[0] = mt[N - 1]
			i = 1
		k -= 1
	mt[0] = 0x80000000	# MSB is 1; assuring non-zero initial array

"""
/* generates a random number on [0,0xffffffff]-interval */
unsigned long genrand_int32(void)
{
    unsigned long y;
    static unsigned long mag01[2]={0x0UL, MATRIX_A};
    /* mag01[x] = x * MATRIX_A  for x=0,1 */

    if (mti >= N) { /* generate N words at one time */
        int kk;

        if (mti == N+1)   /* if init_genrand() has not been called, */
            init_genrand(5489UL); /* a default initial seed is used */

        for (kk=0;kk<N-M;kk++) {
            y = (mt[kk]&UPPER_MASK)|(mt[kk+1]&LOWER_MASK);
            mt[kk] = mt[kk+M] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        for (;kk<N-1;kk++) {
            y = (mt[kk]&UPPER_MASK)|(mt[kk+1]&LOWER_MASK);
            mt[kk] = mt[kk+(M-N)] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        y = (mt[N-1]&UPPER_MASK)|(mt[0]&LOWER_MASK);
        mt[N-1] = mt[M-1] ^ (y >> 1) ^ mag01[y & 0x1UL];

        mti = 0;
    }
  
    y = mt[mti++];

    /* Tempering */
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9d2c5680UL;
    y ^= (y << 15) & 0xefc60000UL;
    y ^= (y >> 18);

    return y;
}
"""

def genrand_int32():
	global mt, mti

	mag01 = [0x0, MATRIX_A]
	# mag01[x] = x * MATRIX_A  for x=0,1
	y = 0

	if mti >= N: # generate N words at one time
		if mti == N+1:   # if init_genrand() has not been called,
			init_genrand(5489) # a default initial seed is used

		kk = 0
		while (kk < N-M):
			y = (mt[kk]&UPPER_MASK)|(mt[kk+1]&LOWER_MASK)
			mt[kk] = mt[kk+M] ^ (y >> 1) ^ mag01[y & 0x1]
			kk += 1

		while (kk < N-1):
			y = (mt[kk]&UPPER_MASK)|(mt[kk+1]&LOWER_MASK)
			mt[kk] = mt[kk+(M-N)] ^ (y >> 1) ^ mag01[y & 0x1]
			kk += 1

		y = (mt[N-1]&UPPER_MASK)|(mt[0]&LOWER_MASK)
		mt[N-1] = mt[M-1] ^ (y >> 1) ^ mag01[y & 0x1]

		mti = 0

	y = mt[mti]
	mti += 1
	y ^= TEMPERING_SHIFT_U(y)
	y ^= TEMPERING_SHIFT_S(y) & TEMPERING_MASK_B
	y ^= TEMPERING_SHIFT_T(y) & TEMPERING_MASK_C
	y ^= TEMPERING_SHIFT_L(y)

	return y;

"""
double genrand_real2(void)
{
    return genrand_int32()*(1.0/4294967296.0); 
    /* divided by 2^32 */
}
"""

def genrand_real2():
	return genrand_int32()*(1.0/4294967296.0)


def main():
	init = [0x123, 0x234, 0x345, 0x456]
	init_by_array(init);
	#init_genrand(4357) # any nonzero integer can be used as a seed
	try:
		print("1000 outputs of genrand_int32()")
		for j in range(1000):
			if (j % 5) == 0:
				sys.stdout.write('\n%5d ' % j)
			sys.stdout.write('%10d ' % genrand_int32())
		print("")
		print("1000 outputs of genrand_real2()")
		for j in range(1000):
			if (j%8) == 0:
				sys.stdout.write('\n%5d ' % j)
			sys.stdout.write('%10.8f ' % genrand_real2())
		print("")
	except IOError as e: 
		pass


if __name__ == "__main__":
	main()
