import os
import threading
import ctypes
import locale
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror, showwarning, showinfo
from tkinter.filedialog import askopenfilename, askdirectory
from acpx_script import ACPXBinScript


class ACPXBinScriptGUI:
    default_width = 400
    default_height = 500
    default_max_thread_activity = 10

    possible_languages = ("eng", "rus")
    format_name = "bin"
    ver_sep = " - "

    def_encodings = (
        "cp932",
        "utf-8",
        "utf-16",
        "windows-1251",
        "cp949",
    )

    _strings_lib = {
        "eng": (
            "ACPXScriptTool by Tester",  # 0
            "Single file",
            "Directory",
            "Enter a name of the .bin file:",
            "Enter a name of the directory with .bin files:",
            "Enter a title of the .txt file:",  # 5
            "Enter a name of the directory with .txt files:",
            "All files",
            "ACPX bin scripts",
            "Choice of bin script",
            "Choice of directory with bin scripts",  # 10
            "Text files",
            "Choice of directory with txt files",
            "Choice of text file",
            "Commands:",
            "Status:",  # 15
            "Help:",
            "Common",
            "Usage",
            "Breaks",
            "Disassemble",  # 20
            "Assemble",
            "Warning",
            "File bin or a directory of them is not chosen.",
            "File txt or a directory of them is not chosen.",
            "Managing files...",  # 25
            "Error",
            "Disassembling failed. ",
            "Disassembling succeed. ",
            "Assembling failed. ",
            "Assembling succeed. ",  # 30
            "Choose the script version:",
            "Bin encoding:",
            "Txt encoding:",
        ),
        "rus": (
            "ACPXScriptTool от Tester-а",  # 0
            "По файлами",
            "По папкам",
            "Введите название файла .bin:",
            "Введите название директории с файлами .bin:",
            "Введите название файла .txt:",  # 5
            "Введите название директории с файлами .txt:",
            "Все файлы",
            "Скрипты bin ACPX",
            "Выбор скрипта bin",
            "Выбор директории со скриптами bin",  # 10
            "Текстовые файлы",
            "Выбор директории с файлами txt",
            "Выбор текстового файла",
            "Команды:",
            "Статус:",  # 15
            "Справка:",
            "Общая",
            "Использование",
            "Переносы",
            "Дизассемблировать",  # 20
            "Ассемблировать",
            "Предупреждение",
            "Файл bin или их директория не выбраны",
            "Файл txt или их директория не выбраны",
            "Обрабатываем файлы...",  # 25
            "Ошибка",
            "Дизассемблирование не удалось. ",
            "Дизассемблирование удалось. ",
            "Ассемблирование не удалось. ",
            "Ассемблирование удалось. ",  # 30
            "Выберите версию скриптов:",
            "Кодировка bin:",
            "Кодировка txt:",
        )
    }

    common_help = {
        'eng': """
Dual languaged (rus+eng) tool for disassembling and assembling scripts .bin from the visual novel's engine ACPX. Very incomplete list of games on this engine you can find on vndb. With it thou can fully edit all thecode, not just strings. Thou can add message breaks and change scenarios without restrictions!
Definations: "#0>" are "free bytes", "#1>" are commands (and "[...]" are arguments below), "*" are labels, "@" есть комментарии.
    """,
        'rus': """
Двуязычное (рус+англ) средство для разборки и сборки скриптов .bin движка визуальных новелл ACPX. С неполным списком игр на нём вы можете ознакомиться на vndb. С ним вы можете полностью редактирвоать код, а не только строки; по вашему повелению добавлять разрывы между сообщений и даже менять сценарии по своему замыслу!
Определения: "#0>" есть "вольные байты", "#1>" есть команды (и под ними "[...]" аргументы), "*" есть метки, "@" есть комментарии.
    """
    }
    usage_help = {
        'eng': """
    1. Choose the mode, file or directory. In first mode you will work with one .bin - .txt pair, in second -- with all files in a pair of directories.
    2. Enter a name of the .bin file in the top entry (do see, with extension) or the directory name. Thou can also enter relative or absolute path. You can also click on "..." to choose.
    3. Choose the version of script file.
    4. Enter a name of the .txt file (do see, with extension) or the directory name. Thou can also enter relative or absolute path. You can also click on "..." to choose.
    5. Choose or enter the encodings: for .bin and .txt files. By default, ACPX engine's scripts use cp932 encoding.
    6. For dissassemble push the button "Disassemble".
    7. For assemble push the button "Assemble".
    8. Status will be displayed on the text area below.
    """,
        'rus': """
    1. Выберите режим: файл или директорию. В первом вы будете работать с парой .bin - .txt, во втором -- со всеми файлами в паре директорий.
    2. Введите название файла .bin в верхней форме (заметьте, с расширением) или имя директории. Также можно вводить относительный или абсолютный до него путь. Также вы можете нажать на кнопку "...", чтобы выбрать.
    3. Введите название файла .txt в нижней форме (заметьте, с расширением) или имя директории. Также можно вводить относительный или абсолютный до него путь. Также вы можете нажать на кнопку "...", чтобы выбрать.
    4. Выберите версию скрипта.
    5. Выберите или введите кодировки: .bin и .txt файлов. По умолчанию в скриптах движка ACPX используется cp932.
    6. Для разборки нажмите на кнопку "Дизассемблировать".
    7. Для сборки нажмите на кнопку "Ассемблировать".
    8. Статус сих операций будет отображаться на текстовом поле ниже.
    """,
    }

    breaks_help = {
        'eng': """
Sometimes there could be a very big problem: text may not fully get in textbox. But with this tool thou don't need to cut some part of text, no. Thou can use line and message breaks. Methods are below.
>>> For line breaks add to lines <r>.

>>> For message breaks insert this below the current message ("SomeString" -> text on the new message).

#1>MESSAGE 
[]
#1>21 
[0]
    """,
        'rus': """
Иногда можно столкнуться с одной большой-пребольшой проблемой: текст может не полностью влезать в текстовое окно. Однако, с сим средством вам не нужно обрезать его, отнюдь. Вы можеет организовывать переносы по строкам и сообщениям. Методы указаны ниже.
>>> Для переносов по строкам добавляйте в них <r>.

>>>Для переносов по сообщениям добавьте под текущее сообщение следующий код ("Какая_то_строка" -> текст на новой строке).

#1>MESSAGE 
[]
#1>21 
[0]
    """
    }

    def __init__(self, **kwargs):
        """Arguments: width, height, language ("eng", "rus"), max_thread_activity..."""
        self._width = kwargs.get("width", self.default_width)
        self._height = kwargs.get("height", self.default_height)
        self._language = kwargs.get("language", self.init_language())
        self._max_thread_activity = kwargs.get("max_thread_activity", self.default_max_thread_activity)
        self._thread_semaphore = threading.BoundedSemaphore(self._max_thread_activity)
        self._unlocker_count = 0
        self._count_lock = threading.Lock()
        self._print_lock = threading.Lock()
        self._status_lock = threading.Lock()

        self._root = tk.Tk()
        self._root.lang_index = 0
        self._root.geometry('{}x{}+{}+{}'.format(
            self._width,
            self._height,
            self._root.winfo_screenwidth() // 2 - self._width // 2,
            self._root.winfo_screenheight() // 2 - self._height // 2))

        self._mes_file = tk.StringVar()  # Name (with path) of Silky Engine's .mes archive.
        self._txt_file = tk.StringVar()  # Name (with path) of txt file.
        self._input_mode = tk.IntVar()  # How to input. 0 -- file, 1 -- directory.
        self._last_indexer = 0  # Some logic only for actual change.

        self._mode_rdb = []
        for i in range(2):
            new_radio = tk.Radiobutton(master=self._root,
                                       variable=self._input_mode,
                                       background="white",
                                       font=('Helvetica', 14),
                                       value=i)
            new_radio.lang_index = i + 1
            self._mode_rdb.append(new_radio)

        self._rus_btn = tk.Button(master=self._root,
                                  text="Русский",
                                  command=lambda: self.translate("rus"),
                                  font=('Helvetica', 15),
                                  bg='white')
        self._eng_btn = tk.Button(master=self._root,
                                  text="English",
                                  command=lambda: self.translate("eng"),
                                  font=('Helvetica', 15),
                                  bg='white')

        self._scr_point_lbl = tk.Label(master=self._root,
                                       bg='white',
                                       font=('Helvetica', 12))
        self._scr_name_ent = tk.Entry(master=self._root,
                                      bg='white',
                                      textvariable=self._mes_file)
        self._scr_find_btn = tk.Button(master=self._root,
                                       text="...",
                                       command=self._find_scr,
                                       font=('Helvetica', 12),
                                       bg='white')

        self._txt_point_lbl = tk.Label(master=self._root,
                                       bg='white',
                                       font=('Helvetica', 12))
        self._txt_name_ent = tk.Entry(master=self._root,
                                      bg='white',
                                      textvariable=self._txt_file)
        self._txt_find_btn = tk.Button(master=self._root,
                                       text="...",
                                       command=self._find_txt,
                                       font=('Helvetica', 12),
                                       bg='white')

        self._input_mode.trace_add("write", lambda *garbage: self._change_input_mode())
        self._input_mode.set(self._last_indexer)

        self._scr_enc_lbl = tk.Label(master=self._root,
                                     bg='white',
                                     font=('Helvetica', 12))
        self._txt_enc_lbl = tk.Label(master=self._root,
                                     bg='white',
                                     font=('Helvetica', 12))
        self._scr_enc_lbl.lang_index = 32
        self._txt_enc_lbl.lang_index = 33

        self._scr_enc = tk.StringVar()
        self._txt_enc = tk.StringVar()
        self._scr_enc_cmb = ttk.Combobox(
            master=self._root,
            font=('Helvetica', 12),
            textvariable=self._scr_enc,
            values=self.def_encodings,
        )
        self._txt_enc_cmb = ttk.Combobox(
            master=self._root,
            font=('Helvetica', 12),
            textvariable=self._txt_enc,
            values=self.def_encodings,
        )
        self._scr_enc.set(self.def_encodings[0])
        self._txt_enc.set(self.def_encodings[0])

        self._commands_lfr = tk.LabelFrame(master=self._root,
                                           font=('Helvetica', 14),
                                           bg='white',
                                           relief=tk.RAISED)
        self._commands_lfr.lang_index = 14
        self._status_lfr = tk.LabelFrame(master=self._root,
                                         font=('Helvetica', 14),
                                         bg='white',
                                         relief=tk.RAISED)
        self._status_lfr.lang_index = 15
        self._help_lfr = tk.LabelFrame(master=self._root,
                                       font=('Helvetica', 14),
                                       bg='white',
                                       relief=tk.RAISED)
        self._help_lfr.lang_index = 16

        self._status_txt = tk.Text(master=self._status_lfr,
                                   wrap=tk.WORD,
                                   font=('Helvetica', 14),
                                   bg='white',
                                   relief=tk.SUNKEN,
                                   state=tk.DISABLED)

        self._common_help_btn = tk.Button(master=self._help_lfr,
                                          command=lambda: showinfo(title=self._strings_lib[self._language][17],
                                                                   message=self.common_help[self._language]),
                                          font=('Helvetica', 12),
                                          bg='white')
        self._common_help_btn.lang_index = 17
        self._usage_help_btn = tk.Button(master=self._help_lfr,
                                         command=lambda: showinfo(title=self._strings_lib[self._language][18],
                                                                  message=self.usage_help[self._language]),
                                         font=('Helvetica', 12),
                                         bg='white')
        self._usage_help_btn.lang_index = 18
        self._breaks_help_btn = tk.Button(master=self._help_lfr,
                                          command=lambda: showinfo(title=self._strings_lib[self._language][19],
                                                                   message=self.breaks_help[self._language]),
                                          font=('Helvetica', 12),
                                          bg='white')
        self._breaks_help_btn.lang_index = 19

        commands = (self._disassemble, self._assemble)
        self._action_btn = []
        for num, comm in enumerate(commands):
            new_btn = tk.Button(
                master=self._commands_lfr,
                command=comm,
                font=('Helvetica', 12),
                bg='white',
            )
            new_btn.lang_index = 20 + num
            self._action_btn.append(new_btn)

        self._init_strings()

        self.place_widgets()
        self.start_gui()

        self._version_lbl = tk.Label(master=self._root,
                                     bg='white',
                                     font=('Helvetica', 12))
        self._version_lbl.lang_index = 31

        self._version = tk.StringVar()

        possible_versions = [i[0] for i in ACPXBinScript.versions_lib]
        self._version_cmb = ttk.Combobox(
            master=self._root,
            font=('Helvetica', 12),
            textvariable=self._version,
            values=possible_versions,
            state="readonly",
        )
        if possible_versions:
            self._version.set(ACPXBinScript.default_version)

        self.translate(self.init_language())
        self.place_widgets(zlo=True)
        self.start_gui(zlo=True)

    def place_widgets(self, zlo=False) -> None:
        """Place widgets of the GUI."""
        if not zlo:
            return
        # Top buttons.
        self._rus_btn.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=0.05)
        self._eng_btn.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=0.05)

        # Input/output files/dirs choosers widgets.

        for num, widget in enumerate(self._mode_rdb):
            widget.place(relx=0.5 * num, rely=0.05, relwidth=0.5, relheight=0.05)
        self._scr_point_lbl.place(relx=0.0, rely=0.1, relwidth=1.0, relheight=0.05)
        self._scr_name_ent.place(relx=0.0, rely=0.15, relwidth=0.9, relheight=0.05)
        self._scr_find_btn.place(relx=0.9, rely=0.15, relwidth=0.1, relheight=0.05)
        self._txt_point_lbl.place(relx=0.0, rely=0.2, relwidth=1.0, relheight=0.05)
        self._txt_name_ent.place(relx=0.0, rely=0.25, relwidth=0.9, relheight=0.05)
        self._txt_find_btn.place(relx=0.9, rely=0.25, relwidth=0.1, relheight=0.05)

        self._version_lbl.place(relx=0.0, rely=0.3, relwidth=1.0, relheight=0.05)
        self._version_cmb.place(relx=0.0, rely=0.35, relwidth=1.0, relheight=0.05)

        self._scr_enc_lbl.place(relx=0.0, rely=0.4, relwidth=0.5, relheight=0.05)
        self._txt_enc_lbl.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.05)
        self._scr_enc_cmb.place(relx=0.0, rely=0.45, relwidth=0.5, relheight=0.05)
        self._txt_enc_cmb.place(relx=0.5, rely=0.45, relwidth=0.5, relheight=0.05)

        # Commands.

        for i, widget in enumerate(self._action_btn):
            widget.place(relx=0.0+i*0.5, rely=0.0, relwidth=0.5, relheight=1.0)

        # Text area.

        self._status_txt.pack()

        # Help buttons.

        self._common_help_btn.place(relx=0.0, rely=0.0, relwidth=0.33, relheight=1.0)
        self._usage_help_btn.place(relx=0.33, rely=0.0, relwidth=0.34, relheight=1.0)
        self._breaks_help_btn.place(relx=0.67, rely=0.0, relwidth=0.33, relheight=1.0)

        # And finally label frames.

        self._commands_lfr.place(relx=0.0, rely=0.5, relwidth=1.0, relheight=0.15)
        self._status_lfr.place(relx=0.0, rely=0.65, relwidth=1.0, relheight=0.2)
        self._help_lfr.place(relx=0.0, rely=0.85, relwidth=1.0, relheight=0.15)

    def start_gui(self, zlo=False) -> None:
        """Start the GUI."""
        # To make more space for patching.
        if zlo:
            self._root.mainloop()

    # Choose input/output files/dirs.

    def _change_input_mode(self) -> None:
        """Change of mode of the input: text or directory."""
        indexer = self._input_mode.get()
        self._scr_point_lbl.lang_index = 3 + indexer
        self._txt_point_lbl.lang_index = 5 + indexer
        if indexer == 0 and indexer != self._last_indexer:  # Filenames now.
            self._mes_file.set("")
            self._txt_file.set("")
        else:
            self._mes_file.set(os.path.splitext(self._mes_file.get())[0])
            self._txt_file.set(os.path.splitext(self._txt_file.get())[0])
        self._last_indexer = indexer
        self._init_strings()

    def _find_scr(self) -> None:
        """Find mes file or a directory with them."""
        if self._input_mode.get() == 0:  # File mode.
            file_types = [(self._strings_lib[self._language][8], '*.{}'.format(self.format_name)),
                          (self._strings_lib[self._language][7], '*')]
            file_name = askopenfilename(filetypes=file_types, initialdir=os.getcwd(),
                                        title=self._strings_lib[self._language][9])
            if file_name:
                file_name = os.path.normpath(file_name)
                relpath = os.path.relpath(file_name, os.getcwd())
                end_arc = file_name
                if relpath.count(os.sep) < file_name.count(os.sep):
                    end_arc = relpath
                self._mes_file.set(end_arc)
                if self._txt_file.get() == "":
                    self._txt_file.set(os.path.splitext(end_arc)[0] + ".txt")
        else:  # Dir mode.
            dir_name = askdirectory(initialdir=os.getcwd(), title=self._strings_lib[self._language][10])
            if dir_name:
                dir_name = os.path.normpath(dir_name)
                relpath = os.path.relpath(dir_name, os.getcwd())
                end_dir = dir_name
                if relpath.count(os.sep) < dir_name.count(os.sep):
                    end_dir = relpath
                self._mes_file.set(end_dir)

    def _find_txt(self) -> None:
        """Find txt file or a directory with them."""
        if self._input_mode.get() == 0:  # File mode.
            file_types = [(self._strings_lib[self._language][1], '*.txt'),
                          (self._strings_lib[self._language][7], '*')]
            file_name = askopenfilename(filetypes=file_types, initialdir=os.getcwd(),
                                        title=self._strings_lib[self._language][13])
            if file_name:
                file_name = os.path.normpath(file_name)
                relpath = os.path.relpath(file_name, os.getcwd())
                end_arc = file_name
                if relpath.count(os.sep) < file_name.count(os.sep):
                    end_arc = relpath
                self._txt_file.set(end_arc)
                if self._mes_file.get() == "":
                    self._mes_file.set(os.path.splitext(end_arc)[0] + ".{}".format(self.format_name))
        else:  # Dir mode.
            dir_name = askdirectory(initialdir=os.getcwd(), title=self._strings_lib[self._language][12])
            if dir_name:
                dir_name = os.path.normpath(dir_name)
                relpath = os.path.relpath(dir_name, os.getcwd())
                end_dir = dir_name
                if relpath.count(os.sep) < dir_name.count(os.sep):
                    end_dir = relpath
                self._txt_file.set(end_dir)

    # Activity (un)locking.

    def _lock_activity(self) -> None:
        """Lock disassemble and assemble actions while managing other files."""
        self._status_txt["state"] = tk.NORMAL
        self._status_txt.delete(1.0, tk.END)
        self._status_txt.insert(1.0, self._strings_lib[self._language][25])
        self._status_txt["state"] = tk.DISABLED
        for widget in self._action_btn:
            widget["state"] = tk.DISABLED

    def _unlock_activity(self) -> None:
        """Unlock disassemble and assemble actions after managing other files."""
        for widget in self._action_btn:
            widget["state"] = tk.NORMAL

    # Disassembling.

    def _disassemble(self) -> bool:
        """Disassemble a mes script or a group of them to a text file or a group of them"""
        mes_file, txt_file, status = self._get_scr_and_txt()
        if not status:
            return False

        self._lock_activity()
        if self._input_mode.get() == 0:  # File mode.
            self._unlocker_count = 1
            new_thread = threading.Thread(daemon=False, target=self._disassemble_this_scr,
                                          args=(mes_file, txt_file))
            new_thread.start()
        else:  # Dir mode.
            files_to_manage = []
            os.makedirs(txt_file, exist_ok=True)
            ezz = len(mes_file.split(os.sep))
            for root, dirs, files in os.walk(mes_file):
                for file_name in files:
                    new_file_array = []  # mes_file, txt_file

                    basic_path = os.sep.join(os.path.join(root, file_name).split(os.sep)[ezz:])
                    rel_mes_name = os.path.normpath(os.path.join(mes_file, basic_path))
                    rel_txt_name = os.path.normpath(os.path.join(txt_file, os.path.splitext(basic_path)[0] + ".txt"))

                    new_file_array.append(rel_mes_name)
                    new_file_array.append(rel_txt_name)
                    files_to_manage.append(new_file_array)

                    # Why did I not initiate file management right away, thou ask?

            self._unlocker_count = len(files_to_manage)  # ...That is the answer.
            for file_mes, file_txt in files_to_manage:
                new_thread = threading.Thread(daemon=False, target=self._disassemble_this_scr,
                                              args=(file_mes, file_txt))
                new_thread.start()

        return True

    def _disassemble_this_scr(self, scr_file: str, txt_file: str) -> None:
        """Disassemble this mes script."""

        try:
            self._thread_semaphore.acquire()
            os.makedirs(os.path.dirname(txt_file), exist_ok=True)
            script_obj = ACPXBinScript(scr_file, txt_file, debug=False, version=self._version.get(),
                                       bin_encoding=self._scr_enc.get(), txt_encoding=self._txt_enc.get())
            script_obj.disassemble()
            self._status_lock.acquire()
            self._status_txt["state"] = tk.NORMAL
            self._status_txt.delete(1.0, tk.END)
            self._status_txt.insert(1.0, scr_file + ": ")
            self._status_txt.insert(2.0, self._strings_lib[self._language][28])
            self._status_txt["state"] = tk.DISABLED
            self._status_lock.release()
            self._print_lock.acquire()
            print("Disassembling of {0} succeed./Дизассемблирование {0} прошло успешно.".format(scr_file))
            self._print_lock.release()
        except Exception as ex:
            self._print_lock.acquire()
            print("Disassembling of {0} error./Дизассемблирование {0} не удалось.".format(scr_file))
            self._print_lock.release()
            showerror(title=self._strings_lib[self._language][26], message=scr_file + "\n" + str(ex))
            self._status_lock.acquire()
            self._status_txt["state"] = tk.NORMAL
            self._status_txt.delete(1.0, tk.END)
            self._status_txt.insert(1.0, scr_file + ": ")
            self._status_txt.insert(2.0, self._strings_lib[self._language][27])
            self._status_txt["state"] = tk.DISABLED
            self._status_lock.release()
        finally:
            self._count_lock.acquire()
            self._unlocker_count -= 1
            self._count_lock.release()
            if self._unlocker_count == 0:
                self._unlock_activity()
            self._thread_semaphore.release()

    def _assemble(self) -> bool:
        """Assemble a mes script or a group of them from the text file or a group of them"""
        mes_file, txt_file, status = self._get_scr_and_txt()
        if not status:
            return False

        self._lock_activity()
        if self._input_mode.get() == 0:  # File mode.
            self._unlocker_count = 1
            new_thread = threading.Thread(daemon=False, target=self._assemble_this_scr,
                                          args=(mes_file, txt_file))
            new_thread.start()
        else:  # Dir mode.
            files_to_manage = []
            os.makedirs(txt_file, exist_ok=True)
            ezz = len(txt_file.split(os.sep))
            for root, dirs, files in os.walk(txt_file):
                for file_name in files:
                    new_file_array = []  # mes_file, txt_file

                    basic_path = os.sep.join(os.path.join(root, file_name).split(os.sep)[ezz:])
                    rel_mes_name = os.path.normpath(os.path.join(mes_file, os.path.splitext(basic_path)[0] + ".{}"
                                                                 .format(self.format_name)))
                    rel_txt_name = os.path.normpath(os.path.join(txt_file, basic_path))

                    new_file_array.append(rel_mes_name)
                    new_file_array.append(rel_txt_name)
                    files_to_manage.append(new_file_array)

                    # Why did I not initiate file management right away, thou ask?

            self._unlocker_count = len(files_to_manage)  # ...That is the answer.
            for file_mes, file_txt in files_to_manage:
                new_thread = threading.Thread(daemon=False, target=self._assemble_this_scr,
                                              args=(file_mes, file_txt))
                new_thread.start()

        return True

    def _assemble_this_scr(self, scr_file: str, txt_file: str) -> None:
        """Assemble this mes script."""
        try:
            self._thread_semaphore.acquire()
            os.makedirs(os.path.dirname(scr_file), exist_ok=True)
            script_obj = ACPXBinScript(scr_file, txt_file, debug=False, version=self._version.get(),
                                       bin_encoding=self._scr_enc.get(), txt_encoding=self._txt_enc.get())
            script_obj.assemble()
            self._status_lock.acquire()
            self._status_txt["state"] = tk.NORMAL
            self._status_txt.delete(1.0, tk.END)
            self._status_txt.insert(1.0, scr_file + ": ")
            self._status_txt.insert(2.0, self._strings_lib[self._language][30])
            self._status_txt["state"] = tk.DISABLED
            self._status_lock.release()
            self._print_lock.acquire()
            print("Assembling of {0} succeed./Ассемблирование {0} прошло успешно.".format(scr_file))
            self._print_lock.release()
        except Exception as ex:
            self._print_lock.acquire()
            print("Assembling of {0} error./Ассемблирование {0} не удалось.".format(scr_file))
            self._print_lock.release()
            showerror(title=self._strings_lib[self._language][26], message=txt_file + "\n" + str(ex))
            self._status_lock.acquire()
            self._status_txt["state"] = tk.NORMAL
            self._status_txt.delete(1.0, tk.END)
            self._status_txt.insert(1.0, scr_file + ": ")
            self._status_txt.insert(2.0, self._strings_lib[self._language][29])
            self._status_txt["state"] = tk.DISABLED
            self._status_lock.release()
        finally:
            self._count_lock.acquire()
            self._unlocker_count -= 1
            self._count_lock.release()
            if self._unlocker_count == 0:
                self._unlock_activity()
            self._thread_semaphore.release()

    def _get_scr_and_txt(self) -> tuple:
        """Get mes, txt files or directories and check status."""
        status = True

        # Check if there is a mes file/dir.

        mes_file = self._mes_file.get()
        if mes_file == '':
            status = False
            showwarning(title=self._strings_lib[self._language][22],
                        message=self._strings_lib[self._language][23])

        # Check if there a txt file/dir.

        txt_file = self._txt_file.get()
        if txt_file == '':
            status = False
            showwarning(title=self._strings_lib[self._language][22],
                        message=self._strings_lib[self._language][24])
        mes_file = os.path.abspath(mes_file)
        txt_file = os.path.abspath(txt_file)

        return mes_file, txt_file, status

    # Language technical methods.

    def translate(self, language: str) -> None:
        """Change the GUI language on "rus" or "eng"."""
        if language not in self.possible_languages:
            print("Error! Incorrect language!/Ошибка! Некорректный язык!")
            return
        self._language = language
        self._init_strings()

    def _init_strings(self) -> None:
        """Initialize strings of the GUI's widgets."""

        # Quite an elegant solution I through off. Hope this works.
        def _init_all_children_strings(widget):
            for elem in widget.winfo_children():
                if hasattr(elem, "lang_index"):
                    elem["text"] = self._strings_lib[self._language][elem.lang_index]
                if isinstance(elem, tk.Frame) or isinstance(elem, tk.LabelFrame):
                    _init_all_children_strings(elem)

        self._root.title(self._strings_lib[self._language][self._root.lang_index])
        _init_all_children_strings(self._root)

    @staticmethod
    def init_language() -> str:
        """Get default language from the system. Works only on Windows."""
        lang_num = 0
        try:
            windll = ctypes.windll.kernel32
            super_locale = locale.windows_locale[windll.GetUserDefaultUILanguage()][:2]
            to_rus_locales = ('ru', 'uk', 'sr', 'bg', 'kk', 'be', 'hy', 'az')
            if super_locale in to_rus_locales:
                lang_num = 1
        except Exception:  # Yes, yes, I know this is a bad practice, but it does not matter here.
            pass
        return ACPXBinScriptGUI.possible_languages[lang_num]
