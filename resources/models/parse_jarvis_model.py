#!/usr/bin/env python
# encoding=utf-8

# Copyright 2020 SAIC AI Lab (Author: Han Xie)

# This python script parses the binary snowboy model file to human-readable format

from __future__ import print_function
import os, struct, argparse
import sys
sys.path.append("../../lib/ubuntu64")
import decrypt

class SnowboyParser:
    def __init__(self, input_file, output_file):
        self.integer = 'i'
        self.float = 'f'
        self.int_size = struct.calcsize(self.integer)
        self.float_size = struct.calcsize(self.float)
        try:
            f_in = open(input_file)
        except:
            print('Unable to open', input_file)
            exit(1)
        if (f_in.read(2) != '\0B'):
            print('Format error', input_file)
            exit(1)
        self.f_in = f_in

        if os.path.exists(output_file):
            print('Target file', output_file, \
                    'already exists, please specify another one')
            exit(1)
        f_out = open(output_file, 'w')
        self.f_out = f_out

    def read_token(self):
        tmp_str = self.f_in.read(1)
        while (tmp_str[-1] != ' '):
            tmp_str += self.f_in.read(1)
        if (tmp_str[0:2] == '\0E'):
            tmp_str = decrypt.DecryptString(tmp_str[2:-1]) + ' '
        return tmp_str

    def read_int(self):
        if (self.f_in.read(1) != '\4'):
            print('possible format error', self.f_in.tell())
        block = self.f_in.read(self.int_size)
        tmp_int = struct.unpack(self.integer, block)[0]
        return tmp_int

    def read_int_vector(self, size):
        if (self.f_in.read(1) != '\4'):
            print('possible format error', self.f_in.tell())
        tmp_vec = []
        for i in range(0, size):
            block = self.f_in.read(self.int_size)
            tmp_vec.append(struct.unpack(self.integer, block)[0])
        return tmp_vec

    def read_float(self):
        if (self.f_in.read(1) != '\4'):
            print('possible format error', self.f_in.tell())
        block = self.f_in.read(self.float_size)
        tmp_float = struct.unpack(self.float, block)[0]
        return tmp_float

    def read_float_vector(self, size):
        tmp_vec = []
        for i in range(0, size):
            block = self.f_in.read(self.float_size)
            tmp_vec.append(struct.unpack(self.float, block)[0])
        return tmp_vec

    def parse_header(self):
        while True:
            token = self.read_token()
            if token == '<SmoothWindow> ' or token == '<SlideWindow> ' or \
                    token == '<NumKws> ' or token == '<SearchMethod> ' or \
                    token == '<SearchNeighbour> ' or token == '<NumPieces> ' or \
                    token == '<DurationPass> ' or token == '<FloorPass> ':
                data = self.read_int()
                str_out = token + str(data) + ' '
                self.f_out.write(str_out)
            elif token == '<Sensitivity> ':
                data = self.read_float()
                str_out = token + str(data) + ' '
                self.f_out.write(str_out)
            elif token == '<Kw> ':
                dim = self.read_int()
                data = []
                str_out = token
                for i in range(0, 7):
                    str_out += str(data[i]) + ' '
                self.f_out.write(str_out)
            elif token == '<SearchMask> ':
                data = self.read_int_vector(8)
                str_out = token
                for i in range(0, 8):
                    str_out += str(data[i]) + ' '
                self.f_out.write(str_out)
            elif token == '<SearchFloor> ':
                if self.read_token() != 'FV ':
                    print('SearchFloor format error at', self.f_in.tell())
                    exit(1)
                dim = self.read_int()
                print('SearchFloor dim', dim)
                data = self.read_float_vector(dim)
                str_out = token
                for i in range(0, dim):
                    str_out += str(data[i]) + ' '
                self.f_out.write(str_out)
            elif token == '<SearchMax> ':
                str_out = token
                str_out += self.f_in.read(1) + ' '
                self.f_out.write(str_out)
            elif token == '<LicenseStart> ':
                print(self.f_in.read(9));
            elif token == '<LicenseDays> ':
                self.read_int()
            elif token == '</KwInfo> ':
                self.f_out.write(token + '\n')
                break
            else:
                self.f_out.write(token)

    def parse_cmvn(self):
        str_out = '<CmvnComponent>\n'
        for i in range(0,2):
            token = self.read_token()
            if self.read_token() != 'FV ':
                print('cmvn component format error at', self.f_in.tell())
                exit(1)
            dim = self.read_int()
            print('cmvn dim', dim)
            data = self.read_float_vector(dim)
            str_out += token + ' '
            for i in range(0, dim):
                str_out += str(data[i]) + ' '
            str_out += '\n'
        token = self.read_token()
        if token != '</CmvnComponent> ':
            print('cmvn component format error at', self.f_in.tell())
            exit(1)
        str_out += token
        self.f_out.write(str_out + '\n')

    def parse_splice(self):
        str_out = '<SpliceComponent>\n'
        token = self.read_token()
        input_size = self.read_int()
        str_out += token + ' ' + str(input_size) + '\n'
        token = self.read_token()
        tmp_dim = self.read_int()
        data = []
        for i in range(0, tmp_dim):
            block = self.f_in.read(self.int_size)
            data.append(struct.unpack(self.integer, block)[0])
        str_out += token + ' '
        str_out += str(tmp_dim) + ' '
        for i in range(0, tmp_dim):
            str_out += str(data[i]) + ' '
        str_out += '\n'
        token = self.read_token()
        data = self.read_int()
        str_out += token + str(data) + '\n'
        token = self.read_token()
        if token != '</SpliceComponent> ':
            print(token)
            print('splice component format error at', self.f_in.tell())
            exit(1)
        str_out += token
        self.f_out.write(str_out + '\n')

    def parse_affine(self):
        str_out = '<AffineComponent>\n'
        token = self.read_token()
        str_out += token
        if self.read_token() != 'FM ':
            print('affine component format error at', self.f_in.tell())
            exit(1)
        rows = self.read_int()
        columns = self.read_int()
        print('affine rows', rows, 'affine columns', columns)
        for i in range(0, rows):
            for j in range(0, columns):
                block = self.f_in.read(self.float_size)
                data = struct.unpack(self.float, block)[0]
                str_out += str(data) +' '
            str_out += '\n'
        token = self.read_token()
        str_out += token
        if self.read_token() != 'FV ':
            print('affine component format error at', self.f_in.tell())
            exit(1)
        dim = self.read_int()
        for i in range(0, dim):
            block = self.f_in.read(self.float_size)
            data = struct.unpack(self.float, block)[0]
            str_out += str(data) + ' '
        str_out += '\n'
        token = self.read_token()
        if token != '</AffineComponent> ':
            print('affine component format error at', self.f_in.tell())
            exit(1)
        str_out += token
        self.f_out.write(str_out + '\n')

    def parse_layer_dim(self, my_token):
        str_out = my_token + '\n'
        token = self.read_token()
        dim = self.read_int()
        str_out += token + str(dim) + '\n'
        token = self.read_token()
        str_out += token
        self.f_out.write(str_out + '\n')

    def parse_nnet2(self):
        while True:
            token = self.read_token()
            if token == '<NumComponents> ':
                data = self.read_int()
                str_out = token + str(data) + ' '
                self.f_out.write(str_out + '\n')
            elif token == '<CmvnComponent> ':
                self.parse_cmvn()
            elif token == '<SpliceComponent> ':
                self.parse_splice()
            elif token == '<AffineComponent> ':
                self.parse_affine()
            elif token == '<RectifiedLinearComponent> ' or \
                    token == '<NormalizeComponent> ' or \
                    token == '<SoftmaxComponent> ':
                self.parse_layer_dim(token)
            elif token == '</Nnet> ':
                self.f_out.write(token + '\n')
                break
            else:
                self.f_out.write(token)
        self.f_in.close()
        self.f_out.close()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='''Parse the binary
            snowboy model file to human-readable format.''')
    arg_parser.add_argument('--source', type=str, default=None,
                            help='''the source binary model file''',
                            required=True)
    arg_parser.add_argument('--target', type=str, default=None,
                            help='''the target model file in human-readable
                            format''', required=True)
    args = arg_parser.parse_args()
    snowboy_parser = SnowboyParser(args.source, args.target)
    snowboy_parser.parse_header()
    snowboy_parser.parse_nnet2()

