#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from Crypto import Random


def debug(s, t):
	print t, list(bytearray(s))


class PKCS7(object):
        # PKCS#7 padding method is described in RFC 5652.
	# https://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS7
	def __call__(self, msg, bs,  mode = True):
		return self._pad(msg, bs) if mode else self._unpad(msg, bs)
			

	def _pad(self, msg, bs):
		pad_bytes = bs - len(msg) % bs
		# divisible case for unpadding
		if pad_bytes == 0: pad_bytes = bs
		return msg + pad_bytes * chr(pad_bytes)


	def _unpad(self, msg, bs):
		pad_bytes = ord(msg[-1])
		return msg[:-pad_bytes:]



class AES_TOTP(object):
    # cb_tuple the base secrect
	def __init__(self, cb_tuple = (1000, 1, 1)):
		hotp_secret = 'xxxxx'

		self._PAD= True
		self._UNPAD = False

		# AES block size is 16 bytes long
		# buffer size 1M
		self._CHUNK_SIZE = 1024 * 1024

		# using PKCS7 as padding function
		self._padfunc = PKCS7()

		from datetime import date
		counter_base = date(*cb_tuple)

		def gen_private_key():
			import pyotp as tp
			# the hash function could be changed. e.g. md5(16)
			from hashlib import sha256 as hfunc # 32 bytes for AES-256

			# calculate day count
			count = (date.today() - counter_base).days
			
			# using HOTP(HMAC-based One-time Password Algorithm) as a secret
			# the secret is a unistring
			secret = tp.HOTP(hotp_secret).at(count)		

			# using sha256 to generate 256-bit private key
			# Private key must be 16 (AES-128), 24 (AES-192), or 32 (AES-256) bytes long.
                        # We apply AES-256 in this case
			h = hfunc(secret)
			return (h.digest(), h.digest_size)
			

		self._key, key_size = gen_private_key()


	def encrypt(self, plaintext):
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self._key, AES.MODE_CBC, iv)
		return iv + cipher.encrypt(self._padfunc(plaintext, AES.block_size, self._PAD))


	def decrypt(self, ciphertext):
		iv = ciphertext[:AES.block_size]
		cipher = AES.new(self._key, AES.MODE_CBC, iv)
		return self._padfunc(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size, self._UNPAD)


	def encrypt_file(self, infile_path, outfile_path):
		cs = self._CHUNK_SIZE 
		self._do_file_cipher(infile_path, outfile_path, cs, self.encrypt)


	def decrypt_file(self, infile_path, outfile_path):
		# chunk size = iv(16) + cipher text block + padding(16)
		cs = self._CHUNK_SIZE + (AES.block_size * 2)
		self._do_file_cipher(infile_path, outfile_path, cs, self.decrypt)

        def decrypt_fileobj(self, infile, outfile):
		# chunk size = iv(16) + cipher text block + padding(16)
		cs = self._CHUNK_SIZE + (AES.block_size * 2)
                self._do_fileobj_cipher(infile, outfile, cs, self.decrypt)
				

	def _do_file_cipher(self, infile_path, outfile_path, chunk_size, cipher_func):
		try:
			with open(infile_path, 'rb') as infile, \
				open(outfile_path, 'wb') as outfile:

				while True:
					chunk = infile.read(chunk_size)
					if not chunk: break
					outfile.write(cipher_func(chunk))
		except (OSError, IOError) as e:
			print e


        def _do_fileobj_cipher(self, infile, outfile, chunk_size, cipher_func):
		while True:
			chunk = infile.read(chunk_size)
			if not chunk: break
			outfile.write(cipher_func(chunk))

                outfile.flush()


if __name__ == '__main__':
	# for test only
	cipher = AES_TOTP()

	def test(p):
		print '|%s|' % p
		m = cipher.encrypt(p)
		try:	
			assert p == cipher.decrypt(m)
		except AssertionError as e:
			print 'not equals!'

    # test with non-ascii 
	test('test這是測試明文123')
	plain = ""
	for i in range(AES.block_size + 1):
		test(plain)
		plain += chr(ord('A') + i)
		

	import os, filecmp
	data = os.urandom(2048)
	prefix = '/tmp/testdata'
	before = prefix +  '.before'
	encrypt = prefix +  '.encrypt'
	after = prefix +  '.after'
	with open(before, 'wb') as f: f.write(data)
	cipher.encrypt_file(before, encrypt)
	cipher.decrypt_file(encrypt, after)
	assert filecmp.cmp(before, after)
	os.remove(before)
	os.remove(encrypt)
	os.remove(after)

	cipher.encrypt_file('/tmp/test', '/tmp/good')

