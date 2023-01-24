# Made by Tester Testerov.

from acpx_bin_script_gui import ACPXBinScriptGUI

debug = False


def chk_files(chk_file, true_file):
    with open(chk_file, 'rb') as chkf, open(true_file, 'rb') as tf:
        i = 0
        while True:
            cb, tb = chkf.read(1), tf.read(1)
            i += 1
            if (cb == b'') or (tb == b''):
                break
            if cb != tb:
                print("NOT IDENTICAL:", i - 1)
                break
        print("IDENTICAL!")


def test(bin_script, txt_file):
    from acpx_script import ACPXBinScript
    test_script = ACPXBinScript(bin_script, txt_file, debug=False, version="ESCR1_00",
                                bin_encoding="cp932", txt_encoding="cp932")
    #test_script.disassemble()
    test_script.assemble()


def start_gui():
    gui = ACPXBinScriptGUI()
    return True


if __name__ == '__main__':
    if debug:
        bin_script = "a01_prol.bin"
        bak_bin_script = "a01_prol.bin.bak"
        txt_file = "a01_prol.txt"

        test(bin_script, txt_file)
        #chk_files(bin_script, bak_bin_script)
    else:
        start_gui()
