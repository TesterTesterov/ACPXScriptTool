import struct


class ACPXCommandLib:
    # Library.
    # Opcode, arguments, visible name.

    command_library = (
        ('ff', 'I', 'SAMPLE'),
    )
    technical_instances = ('<', '>')
    Q_instances = ('q', 'Q')
    I_instances = ('i', 'I')
    H_instances = ('h', 'H')
    B_instances = ('b', 'B')
    s_instances = ('s',)
    S_instances = ('S',)
    O_instances = ('O',)
    offsets_library = ('O', 'I')

    def __init__(self, bin_encoding: str, txt_encoding: str, string_bank: tuple = None, offset_bank: tuple = None,
                 label_definer: tuple = None, offset_beginner: int = 0):
        """bin_encoding -- encoding of the bin script.
        txt_encoding -- encoding of the txt file.
        string_bank -- the script's strings.
        offset_bank -- the script's code's offsets.
        label_definer -- the script's labels definitions.
        offset_beginner -- the beginning of the script's code's offsets."""
        if offset_bank is None:
            offset_bank = []
        if string_bank is None:
            string_bank = []
        if label_definer is None:
            label_definer = []
        self.bin_encoding = bin_encoding
        self.txt_encoding = txt_encoding
        self.string_bank = string_bank
        self._offset_bank = offset_bank
        self.label_definer = label_definer
        self.offset_beginner = offset_beginner

    # Properties.

    @property
    def offset_bank(self):
        return self._offset_bank

    @offset_bank.setter
    def offset_bank(self, value):
        self._offset_bank = value

    @offset_bank.deleter
    def offset_bank(self):
        self._offset_bank = tuple()

    # Structs.

    # # Struct getters.

    def get_args(self, in_file, args: str) -> list:
        """Extract arguments from the file."""
        arguments_list = []
        appendix = ""
        for argument in args:
            if argument in self.technical_instances:
                appendix = argument
            elif argument in self.Q_instances:
                result = self.get_Q(in_file, appendix + argument)
                arguments_list.append(result)
            elif argument in self.I_instances:
                result = self.get_I(in_file, appendix + argument)
                arguments_list.append(result)
            elif argument in self.H_instances:
                result = self.get_H(in_file, appendix + argument)
                arguments_list.append(result)
            elif argument in self.B_instances:
                result = self.get_B(in_file, appendix + argument)
                arguments_list.append(result)
            elif argument in self.s_instances:
                result = self.get_s(in_file)
                arguments_list.append(result)
            elif argument in self.O_instances:
                result = self.get_O(in_file)
                arguments_list.append(result)
        return arguments_list

    @staticmethod
    def get_B(file_in, definer: str) -> int:
        """Extract B/b structure."""
        dummy = struct.unpack(definer, file_in.read(1))[0]
        return dummy

    @staticmethod
    def get_H(file_in, definer: str) -> int:
        """Extract H/h structure."""
        dummy = struct.unpack(definer, file_in.read(2))[0]
        return dummy

    @staticmethod
    def get_I(file_in, definer: str) -> int:
        """Extract I/i structure."""
        dummy = struct.unpack(definer, file_in.read(4))[0]
        return dummy

    @staticmethod
    def get_Q(file_in, definer: str) -> int:
        """Extract I/i structure."""
        dummy = struct.unpack(definer, file_in.read(8))[0]
        return dummy

    def get_s(self, file_in) -> str:
        """Extract linked string from file."""
        str_num = self.get_I(file_in, 'I')
        string = self.string_bank[str_num]
        return string

    @staticmethod
    def get_S(in_file, encoding: str) -> str:
        """Extract string from the file."""
        string = b''
        byte = in_file.read(1)
        while byte != b'\x00':
            string += byte
            byte = in_file.read(1)
        return string.decode(encoding)

    def get_O(self, file_in) -> str:
        """Extract offset from the file."""
        offset = self.get_I(file_in, 'I') + self.offset_beginner
        offset_num = self.offset_bank.index(offset)
        offset_string = "*{}".format(self.label_definer[offset_num])
        return offset_string

    @classmethod
    def get_len_from_structure(cls, stru):
        """Get length of known structure -- stru.
        Currently works with B, H, I, Q with variations."""
        summ = 0
        for structer in stru:
            if structer in cls.Q_instances:
                summ += 8
            elif structer in cls.I_instances:
                summ += 4
            elif structer in cls.H_instances:
                summ += 2
            elif structer in cls.B_instances:
                summ += 1
            elif structer in cls.s_instances:
                summ += 4
            elif structer in cls.O_instances:
                summ += 4
            elif structer in cls.technical_instances:
                summ += 0
            elif structer in cls.S_instances:
                raise TypeError("Incorrect struct type: S!")
        return summ

    # # Struct setters.

    def set_args(self, argument_list: list, args: str) -> bytes:
        """Set arguments."""
        args_bytes = b''
        appendix = ""
        current_argument = 0
        for argument in args:
            if argument in self.technical_instances:
                appendix = argument
                continue
            # Argument number changing.
            if argument in self.Q_instances:
                args_bytes += self.set_Q(argument_list[current_argument], appendix + argument)
            if argument in self.I_instances:
                args_bytes += self.set_I(argument_list[current_argument], appendix + argument)
            elif argument in self.H_instances:
                args_bytes += self.set_H(argument_list[current_argument], appendix + argument)
            elif argument in self.B_instances:
                args_bytes += self.set_B(argument_list[current_argument], appendix + argument)
            elif argument in self.s_instances:
                args_bytes += self.set_s(argument_list[current_argument], self.bin_encoding)
            elif argument in self.O_instances:
                args_bytes += self.set_O(argument_list[current_argument])
            current_argument += 1  # Since argument may not change with new command.
        return args_bytes

    @staticmethod
    def set_B(arg: int, definer: str) -> bytes:
        """Set B/b structure."""
        return struct.pack(definer, arg)

    @staticmethod
    def set_H(arg: int, definer: str) -> bytes:
        """Set H/h structure."""
        return struct.pack(definer, arg)

    @staticmethod
    def set_I(arg: int, definer: str) -> bytes:
        """Set I/i structure."""
        return struct.pack(definer, arg)

    @staticmethod
    def set_Q(arg: int, definer: str) -> bytes:
        return struct.pack(definer, arg)

    def set_s(self, arg: str, encoding: str) -> bytes:
        """Set linked string structure."""
        str_number = len(self.string_bank)
        self.string_bank.append(arg)
        arg_bytes = self.set_I(str_number, 'I')
        return arg_bytes

    @staticmethod
    def set_S(arg: str, encoding: str) -> bytes:
        """Set string structure."""
        arg_bytes = arg.encode(encoding) + b'\x00'
        return arg_bytes

    def set_O(self, arg: str) -> bytes:
        """Set offset structure."""
        offset_num = arg[1:]
        offset_index = self.label_definer.index(offset_num)
        offset = self.offset_bank[offset_index] - self.offset_beginner
        result = self.set_I(offset, 'I')
        return result

    # Just a simple methods.

    @classmethod
    def get_command_index(cls, command: str) -> int:
        """Get index of command in command_library.
        command -- normal name of command.
        For normal name see "get_true_name"."""
        for i in range(len(cls.command_library)):
            if command == cls.command_library[i][0]:
                return i
        for i in range(len(cls.command_library)):
            if command == cls.command_library[i][2]:
                return i
        return -1

    @classmethod
    def find_command_index(cls, byer) -> int:
        """Find index of command from bytes or int."""
        nou = 0
        if isinstance(byer, bytes):
            nou = byer[0]
        elif isinstance(byer, int):
            nou = byer
        else:
            raise TypeError("Incorrect type: " + str(type(byer)) +
                            "!\nНекорректный тип: " + str(type(byer)) + "!")
        hexer = cls.to_fully_hex(nou)

        result = -1
        for i in range(len(cls.command_library)):
            if hexer == cls.command_library[i][0]:
                result = i
                break
        return result

    @classmethod
    def get_true_name(cls, index: int) -> str:
        """Get the true name of the command with index."""
        test = cls.command_library[index][2]
        if (test == '') or (test is None):
            return cls.command_library[index][0]
        else:
            return cls.command_library[index][2]

    @staticmethod
    def to_fully_hex(inter):
        """Get full hex name of the command inter from bytes or int."""
        if isinstance(inter, bytes):
            nou = inter[0]
        elif isinstance(inter, int):
            nou = inter
        else:
            raise TypeError("Incorrect type: " + str(type(inter)) +
                            "!\nНекорректный тип: " + str(type(inter)) + "!")
        zlo = hex(nou)[2:]
        if len(zlo) == 1:
            zlo = "0" + zlo
        return zlo

    def extract_all_offsets(self, arguments: str, file_in) -> list:
        """Extract all offset data from the file by arguments.
        arguments -- structure arguments.
        file_in -- input file"""

        true_pos = file_in.tell()
        offsets = []
        prefix = ''

        for a in arguments:
            if a in self.technical_instances:
                prefix = a
                continue
            indexer = self.offsets_library[0].find(a)
            if indexer == -1:
                filler = self.get_len_from_structure(a)
                file_in.seek(filler, 1)
            else:
                b = self.offsets_library[1][indexer]
                data = self.get_args(file_in, prefix+b)[0]
                data += self.offset_beginner
                offsets.append(data)

        file_in.seek(true_pos, 0)
        return offsets

    def get_all_linked_strings(self, arguments: str, arg_data: list) -> list:
        """Extract all linked strings from the list of arguments.
        arguments -- structure of arguments.
        arg_data -- data of arguments."""

        strings = []

        for t in self.technical_instances:
            arguments.replace(t, '')
        for a, d in zip(arguments, arg_data):
            if a in self.s_instances:
                strings.append(d)

        return strings


class ACPXCommandLibVer1_00(ACPXCommandLib):
    command_library = (
        ('00', '', 'NULL'),
        ('01', 'O', 'CALL'),
        ('02', 'O', 'JMP'),
        ('03', 'O', 'JZ'),
        ('04', '', 'END'),
        ('05', 'i', 'PUSH_INT'),
        ('06', '', ''),
        ('07', 's', 'PUSH_STR'),
        ('08', '', ''),
        ('09', '', ''),
        ('0d', '', ''),
        ('0e', '', ''),

        ('11', '', ''),
        ('14', '', ''),
        ('18', '', ''),
        ('19', '', ''),
        ('1b', '', ''),
        ('1d', '', ''),
        ('1f', '', ''),

        ('21', 'I', ''),
        ('22', '', ''),
        ('23', 'I', 'FLOW_WINDOW'),
        ('24', '', ''),
        ('26', '', ''),
        ('27', '', ''),
        ('2a', '', 'MESSAGE'),
        ('2b', 'I', 'SPEAKER'),
        ('2c', '', 'MENU'),
        ('2d', '', ''),
        ('2f', 'I', ''),

        ('32', 'I', ''),
        ('33', 'I', ''),
        ('34', '', ''),
        ('36', '', ''),
        ('38', '', ''),
        ('39', '', ''),
        ('3a', 'I', ''),
        ('3b', '', ''),
        ('3e', '', ''),
        ('3f', '', ''),

        ('43', '', ''),
        ('44', '', ''),
        ('4a', '', ''),
        ('4b', '', ''),
        ('4d', '', ''),
        ('4e', '', ''),
        ('4f', '', ''),

        ('51', '', ''),
        ('52', '', ''),
        ('53', '', ''),
        ('54', '', ''),
        ('55', '', ''),
        ('56', '', ''),
        ('57', '', ''),
        ('58', '', 'RETURN'),
        ('59', '', ''),
        ('5a', '', ''),
        ('5b', '', ''),
        ('5d', '', ''),
        ('5f', '', 'TITLE'),

        ('61', '', ''),
        ('6a', '', ''),
        ('6b', '', ''),
        ('6c', '', ''),
        ('6d', '', ''),
        ('6e', '', ''),
        ('6f', '', ''),

        ('70', '', ''),
        ('71', '', ''),
        ('72', '', ''),
        ('73', '', ''),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
