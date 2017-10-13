#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import argparse

ag = argparse.ArgumentParser(description='encryption/decryption file or string')
input_type = ag.add_subparsers(help='string|file')
string_parser = input_type.add_parser('str', help='do file cipher ')
file_parser = input_type.add_parser('file', help='do string cipher')

string_parser.add_argument('-m', '--mode', help='[enc|dec] --> encryption/decryption', required=True)
string_parser.add_argument('string', help='the string need to be ciphered')

file_parser.add_argument('-m', '--mode', help='[enc|dec] --> encryption/decryption', required=True)
file_parser.add_argument('-i', '--input', help='input file path', required=True)
file_parser.add_argument('-o', '--output', nargs='?', help='output file path. default is /tmp/data[enc|dec]')

args = ag.parse_args()

from simple_cipher import AES_TOTP
import sys
cipher = AES_TOTP()

funcs = {'enc': None, 'dec': None}
if args.mode not in funcs: 
	ag.print_help()
	exit(1)

if hasattr(args, 'string'):
	# do string cipher
	funcs = {'enc': cipher.encrypt, 'dec': cipher.decrypt}
	sys.stdout.write(funcs[args.mode](args.string))
elif hasattr(args, 'input'):
	# do file cipher
	funcs = {'enc': cipher.encrypt_file, 'dec': cipher.decrypt_file}
	output = '/tmp/data.enc' if args.mode == 'enc' else '/tmp/data.dec'
	if hasattr(args, 'output') and args.output is not None: output = args.output

	funcs[args.mode](args.input, output)
	print "file output to %s" %  output

