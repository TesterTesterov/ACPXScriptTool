import struct
import json
from acpx_command_lib import ACPXCommandLibVer1_00


# Made by Tester.
# Some notes about ACPX Bin Script Format.
# --- Header ---
# 8 bytes -- signature. I have found only ESCR1_00, so I'll tell only about it.
# 4 bytes -- string number.
# # 4 bytes each strings offsets.
# 4 bytes -- offset of the string block (from code block offset + 4).
# --- Code block ---
# Opcodes are 1 byte each. For more data, look in acpx_command_lib.py.
# --- String block ---
# # 4 bytes -- section length.
# #


class ACPXBinScript:
    versions_lib = (
        ("ESCR1_00", ACPXCommandLibVer1_00),
    )
    default_version = "ESCR1_00"

    def __init__(self, bin_file: str, txt_file: str, bin_encoding: str = "cp932", txt_encoding: str = "cp932",
                 version: str = None, debug: bool = False) -> None:
        """Initialize ACPXBin class.
        bin_encoding -- encoding of the script.
        txt_encoding -- encoding of the txt file.
        version -- the script version."""

        self.bin_file = bin_file
        self.txt_file = txt_file
        self.bin_encoding = bin_encoding
        self.txt_encoding = txt_encoding
        self._version = None
        self.version = version
        self.command_lib = self.get_command_lib(self.version)
        self._debug = debug

    # Interface.

    def assemble(self):
        """Assemble the script."""
        if self._debug:
            print("=== Assembling of {} from {} started.".format(self.bin_file, self.txt_file))

        # First, we should get all the strings. Without that, we cannot calculate the offsets.

        strings, offsets, labels, string_block_len_pointer = self._get_pre_data()
        if self._debug:
            print("= Strings.")
            print(*strings, sep='\n')

        # Next, we should calculate the start of the code block and fix the offsets.

        code_block_start = 8 + 4 + 4 * len(strings) + 4
        offsets = [code_block_start + i for i in offsets]
        self.command_lib.offset_bank = tuple(offsets)
        self.command_lib.label_definer = tuple(labels)
        self.command_lib.offset_beginner = code_block_start
        self.command_lib.string_bank = ['']
        if self._debug:
            print("Offsets:", offsets)
            print("Labels:", labels)
            print("Code block start:", code_block_start)
            print("Code block end:", string_block_len_pointer)

        # Next, we should assemble the script itself.
        # # Assemble the header, assemble the code, assemble the strings and rewrite the strings offset
        # # and the length of the strings block.

        self._assemble(strings, string_block_len_pointer)

        if self._debug:
            print("=== Assembling of {} from {} ended.".format(self.bin_file, self.txt_file))

    def disassemble(self, version_autochange=True, string_autochange=True, offsets_autochange=True):
        """Disassemble the script.
        version_autochange -- get version from the script.
        string_autochange -- get strings from the script.
        offsets_autochange -- automatically change the start code block offsets."""
        if self._debug:
            print("=== Disassembling of {} to {} started.".format(self.bin_file, self.txt_file))

        version, string_offsets, code_block_offset, string_block_offset = self._unpack_header()
        if self._debug:
            print("= Header disassembled.")
            print("Version:", version)
            print("String number:", len(string_offsets))
            print("String offsets:", string_offsets)
            print("String block offset:", string_block_offset)
            print("Code block offset:", code_block_offset)
        if version_autochange:
            self.version = version
        if offsets_autochange:
            self.command_lib.offset_beginner = code_block_offset
            offsets = self._extract_offsets(code_block_offset, string_block_offset)
            self.command_lib.offset_bank = sorted(set(offsets))
            self.command_lib.label_definer = tuple(range(len(offsets)))
        if self._debug:
            print("Offsets:", self.command_lib.offset_bank)
            print("Offsets number:", len(self.command_lib.offset_bank))

        strings = self._unpack_strings(string_block_offset, string_offsets)
        if self._debug:
            print("= Strings unpacked.")
            print(*strings, sep='\n')
        if string_autochange:
            self.command_lib.string_bank = strings

        self._disassemble_code(code_block_offset, string_block_offset)

        if self._debug:
            print("=== Disassembling of {} to {} ended.".format(self.bin_file, self.txt_file))

    # Technical methods.

    # # For assembling.

    def _get_pre_data(self) -> tuple:
        """Get data for the future assembling: strings, offsets and offsets' labels."""
        strings = ['']
        offsets = []
        labels = []

        with open(self.txt_file, 'r', encoding=self.txt_encoding, errors='replace') as df:
            pointer = 0
            while True:
                new_line = df.readline()
                if new_line == '':
                    break
                new_line = new_line.rstrip()
                if new_line[0] == '*':  # Label.
                    offsets.append(pointer)
                    labels.append(new_line[1:])
                elif new_line[0] == '#':  # Command.
                    if len(new_line) == 1:  # Some extra checks.
                        continue
                    if new_line[1] == '0':
                        free_bytes = new_line.split('>')[1]
                        free_bytes = [i for i in free_bytes.split(' ') if (len(i) == 2) and (i[0] != '<')]
                        pointer += len(free_bytes)
                    elif new_line[1] == '1':
                        pointer += 1  # For the opcode.
                        command = new_line.split('>')[1]
                        command = command.split(' ')[0]  # In case of debug mode was enabled.
                        index = self.command_lib.get_command_index(command)
                        if index == -1:
                            raise TypeError("Incorrect opcode {}!".format(command))
                        arguments = self.command_lib.command_library[index][1]
                        pointer += self.command_lib.get_len_from_structure(arguments)
                        arg_data = json.loads(df.readline())
                        strings.extend(self.command_lib.get_all_linked_strings(arguments, arg_data))
                elif new_line[0] == '@':  # To be safe.
                    continue

        return strings, offsets, labels, pointer

    def _assemble(self, strings: list, string_block_len_pointer: int) -> None:
        """Assemble the script.
        strings -- the script's strings.
        string_block_len_pointer -- pointer to the end of the strings block."""
        with (open(self.bin_file, 'wb') as af,
              open(self.txt_file, 'r', encoding=self.txt_encoding, errors='replace') as df):
            tech_strings = [i.encode(self.bin_encoding) + b'\x00' for i in strings]
            str_block_len = self._assemble_header(af, tech_strings, string_block_len_pointer)
            self._assemble_code(af, df)
            self._assemble_strings(af, tech_strings, str_block_len)

    def _assemble_header(self, af, bstrings, string_block_len_pointer) -> int:
        """Assemble the header and get len of string block.
        af -- assembly file.
        bstrings -- byte strings.
        string_block_len_pointer -- pointer to the end of the strings block."""
        af.write(self.version.encode('cp932'))  # Signature. Do not change this line!!!
        af.write(struct.pack('I', len(bstrings)))
        pointer = 0
        for bstr in bstrings:
            af.write(struct.pack('I', pointer))
            pointer += len(bstr)
        af.write(struct.pack('I', string_block_len_pointer))  # String block length structure offset.

        return pointer

    def _assemble_code(self, af, df) -> None:
        """Assemble the code and return its end.
        af -- assembly file.
        df -- disassembled file."""

        while True:
            new_line = df.readline()
            if new_line == '':
                break
            new_line = new_line.rstrip()
            if new_line[0] == '#':  # Command.
                if len(new_line) == 1:  # Some extra checks.
                    continue
                if new_line[1] == '0':
                    free_bytes = new_line.split('>')[1]
                    free_bytes = [i for i in free_bytes.split(' ') if (len(i) == 2) and (i[0] != '<')]
                    free_bytes = " ".join(free_bytes)
                    af.write(bytes.fromhex(free_bytes))
                elif new_line[1] == '1':
                    command = new_line.split('>')[1]
                    command = command.split(' ')[0]  # In case of debug mode was enabled.
                    index = self.command_lib.get_command_index(command)
                    if index == -1:
                        raise TypeError("Incorrect opcode {}!".format(command))
                    command_byte = bytes.fromhex(self.command_lib.command_library[index][0])
                    af.write(command_byte)

                    arguments = self.command_lib.command_library[index][1]
                    arg_data = self.read_args(df)
                    arg_bytes = self.command_lib.set_args(arg_data, arguments)
                    af.write(arg_bytes)
            elif new_line[0] == '@':  # Just to be safe.
                continue

    def _assemble_strings(self, af, bstrings: list, str_block_len: int) -> None:
        """Assemble strings.
        af -- assembly file.
        bstrings -- byte strings.
        str_block_len -- length of the string block."""

        af.write(struct.pack('I', str_block_len))
        for bstr in bstrings:
            af.write(bstr)

    # # For disassembling.

    def _unpack_header(self) -> tuple:
        """Unpack bin script header.
        Returns...
        (version, string offsets, code_block_offset, string_block_offset)"""
        version = ""
        string_offsets = []
        code_block_offset = 0
        string_block_offset = 0
        with open(self.bin_file, 'rb') as sf:
            version = sf.read(8).decode('cp932')  # Signature. Do not change this line!!!
            off_num = struct.unpack('I', sf.read(4))[0]
            for _ in range(off_num):
                string_offsets.append(struct.unpack('I', sf.read(4))[0])
            string_block_offset = struct.unpack('I', sf.read(4))[0]
            code_block_offset = sf.tell()
            string_block_offset += code_block_offset  # As the offset from the beginning of the code block.
        return version, string_offsets, code_block_offset, string_block_offset

    def _unpack_strings(self, string_block_start: int, string_offsets: tuple) -> tuple:
        """Unpack bin script strings.
        string_block_start -- start of the string section.
        string_offsets -- offsets of the strings in the section."""
        strings = []

        with open(self.bin_file, 'rb') as sf:
            for offset in string_offsets:
                new_offset = string_block_start + 4 + offset
                sf.seek(new_offset, 0)
                new_string = self.command_lib.get_S(sf, self.bin_encoding)
                strings.append(new_string)

        return tuple(strings)

    def _extract_offsets(self, start_offset: int, end_offset: int) -> tuple:
        """Get offsets from the code of the script.
        start_offset -- offset of the code section's start.
        end_offset -- offset of the code section's end."""
        offsets = []

        with open(self.bin_file, 'rb') as af:
            af.seek(start_offset, 0)

            while True:
                pointer = af.tell()

                if pointer >= end_offset:  # String section start.
                    break
                current_byte = af.read(1)
                if current_byte == b'':  # In case of broken end offset.
                    break
                command_index = self.command_lib.find_command_index(current_byte)

                if command_index != -1:
                    command_args = self.command_lib.command_library[command_index][1]
                    args_len = self.command_lib.get_len_from_structure(command_args)
                    new_offsets = self.command_lib.extract_all_offsets(command_args, af)
                    offsets.extend(new_offsets)
                    af.seek(args_len, 1)

        return tuple(offsets)

    def _disassemble_code(self, start_offset: int, end_offset: int) -> None:
        """Disassemble the code of the script.
        start_offset -- offset of the code section's start.
        end_offset -- offset of the code section's end."""

        with open(self.bin_file, 'rb') as af, open(self.txt_file, 'w', encoding=self.txt_encoding) as df:
            af.seek(start_offset, 0)
            free_bytes = b''
            free_bytes_offset = 0

            while True:
                pointer = af.tell()

                if pointer in self.command_lib.offset_bank:
                    offset_index = self.command_lib.offset_bank.index(pointer)
                    offset_num = self.command_lib.label_definer[offset_index]
                    offset_str = "*{}".format(offset_num)
                    print(offset_str, file=df)

                if pointer >= end_offset:  # String section start.
                    break
                current_byte = af.read(1)
                if current_byte == b'':  # In case of broken end offset.
                    break
                command_index = self.command_lib.find_command_index(current_byte)

                if command_index == -1:  # "Free bytes" system. So the program don't break too easy.
                    free_bytes += current_byte
                    if free_bytes_offset == 0:
                        free_bytes_offset = pointer
                else:  # Such command is in the library.
                    if free_bytes:
                        free_bytes_str = '#0>{}{}'.format(free_bytes.hex(' '), self.offset_string(free_bytes_offset))
                        print(free_bytes_str, file=df)
                        free_bytes = b''
                        free_bytes_offset = 0
                    true_command_name = self.command_lib.get_true_name(command_index)
                    command_str = "#1>{}{}".format(true_command_name, self.offset_string(pointer))
                    print(command_str, file=df)
                    commands_arguments = self.command_lib.get_args(af,
                                                                   self.command_lib.command_library[command_index][1])
                    json.dump(commands_arguments, df, ensure_ascii=False)
                    df.write('\n')

            if free_bytes:  # Kind of crutch, but oh well.
                free_bytes_str = '#0>{}{}'.format(free_bytes.hex(' '), self.offset_string(free_bytes_offset))
                print(free_bytes_str, file=df)
                free_bytes = b''
                free_bytes_offset = 0

    # Properties.

    @property
    def version(self):
        """Script's version."""
        return self._version

    @version.setter
    def version(self, version: str) -> bool:
        """Set the script's version."""
        for entry in self.versions_lib:
            if version == entry[0]:
                self._version = version
                return True
        if (self._version is None) or (self._version == ""):
            self._version = self.default_version
        return False

    @version.deleter
    def version(self):
        """Restore the script's version for default."""
        self._version = self.default_version

    # Supplement methods.

    def offset_string(self, offset):
        off_str = " <{}>".format(offset) * self._debug
        return off_str

    def get_command_lib(self, version):
        """Get command library from the version."""
        for entry in self.versions_lib:
            if version == entry[0]:
                return entry[1](self.bin_encoding, self.txt_encoding)
        return None

    @staticmethod
    def read_args(filer) -> list:
        """Read arguments from disassembled file."""
        arg_line = ""
        while True:
            arg_line = filer.readline()
            if arg_line[0] != '@':
                break
        arg_data = json.loads(arg_line)
        return arg_data
