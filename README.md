# ACPXScriptTool
# English
Dual languaged (rus+eng) tool for disassembling and assembling scripts .bin from the visual novel's engine ACPX. Very incomplete list of games on this engine you can find on vndb. With it thou can fully edit all thecode, not just strings. Thou can add message breaks and change scenarios without restrictions!

Definations: "#0>" are "free bytes", "#1>" are commands (and "[...]" are arguments below), "*" are labels, "@" есть комментарии.

# Русский
Двуязычное (рус+англ) средство для разборки и сборки скриптов .bin движка визуальных новелл ACPX. С неполным списком игр на нём вы можете ознакомиться на vndb. С ним вы можете полностью редактирвоать код, а не только строки; по вашему повелению добавлять разрывы между сообщений и даже менять сценарии по своему замыслу!

Определения: "#0>" есть "вольные байты", "#1>" есть команды (и под ними "[...]" аргументы), "*" есть метки, "@" есть комментарии.

# Usage / Использование
# English
![изображение](https://user-images.githubusercontent.com/66121918/214245322-3512616e-17c5-4008-b2d4-a78d4689fc89.png)

1. Choose the mode, file or directory. In first mode you will work with one .bin - .txt pair, in second -- with all files in a pair of directories.
2. Enter a name of the .bin file in the top entry (do see, with extension) or the directory name. Thou can also enter relative or absolute path. You can also click on "..." to choose.
3. Choose the version of script file.
4. Enter a name of the .txt file (do see, with extension) or the directory name. Thou can also enter relative or absolute path. You can also click on "..." to choose.
5. Choose or enter the encodings: for .bin and .txt files. By default, ACPX engine's scripts use cp932 encoding.
6. For dissassemble push the button "Disassemble".
7. For assemble push the button "Assemble".
8. Status will be displayed on the text area below.

# Русский
![изображение](https://user-images.githubusercontent.com/66121918/214245251-cecf372e-2a5d-49d4-ab9d-f2e443d82798.png)

1. Выберите режим: файл или директорию. В первом вы будете работать с парой .bin - .txt, во втором -- со всеми файлами в паре директорий.
2. Введите название файла .bin в верхней форме (заметьте, с расширением) или имя директории. Также можно вводить относительный или абсолютный до него путь. Также вы можете нажать на кнопку "...", чтобы выбрать.
3. Введите название файла .txt в нижней форме (заметьте, с расширением) или имя директории. Также можно вводить относительный или абсолютный до него путь. Также вы можете нажать на кнопку "...", чтобы выбрать.
4. Выберите версию скрипта.
5. Выберите или введите кодировки: .bin и .txt файлов. По умолчанию в скриптах движка ACPX используется cp932.
6. Для разборки нажмите на кнопку "Дизассемблировать".
7. Для сборки нажмите на кнопку "Ассемблировать".
8. Статус сих операций будет отображаться на текстовом поле ниже.

# Breaks / Переносы
# English
Sometimes, there could be a very big problem: text may not fully get in textbox. But with this tool thou don't need to cut some part of text, no. Thou can use line and message breaks. Methods are below.
>>> For line breaks add to lines **\<r\>**.

>>> For message breaks insert this below the current message.

```
#1>MESSAGE 
[]
#1>21 
[0]
```

# Русский
Иногда можно столкнуться с одной большой-пребольшой проблемой: текст может не полностью влезать в текстовое окно. Однако, с сим средством вам не нужно обрезать его, отнюдь. Вы можеет организовывать переносы по строкам и сообщениям. Методы указаны ниже.
>>> Для переносов по строкам добавляйте в них **\<r\>**.

>>>Для переносов по сообщениям добавьте под текущее сообщение следующий код.

```
#1>MESSAGE 
[]
#1>21 
[0]
```

# Tested / Протестировано
# English
- [Yamizome Revenger](https://vndb.org/v22739).

# Русский
- [Павший во тьму мститель](https://vndb.org/v22739).
