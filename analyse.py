# -*- coding:utf-8 -*-
'''
This script analyses an input file and write analysis in a file named analysed_<INPUT_FILE_NAME>.txt 

Usage:
    python3 analyse.py <PATH_INPUT_FILE> <FILE_TYPE> <PATH_FST>

where <FILE_TYPE> = "log" or "xml"

Ex:
    python3 analyse.py data/user_input_2019_su.txt log ~/all-gut/giellalt/lang-sme/src/analyser-dict-gt-desc.xfst

    python3 analyse.py data/smenob-all.lexc xml ~/all-gut/giellalt/lang-sme/src/analyser-dict-gt-desc.xfst
'''
import sys
from subprocess import Popen, PIPE


file_name = sys.argv[1]
file_type = sys.argv[2]
fst_file = sys.argv[3]
cmd = " | lookup -q -flags mbTT " + fst_file

analysed_file = "analysed_" + file_name.split("/")[1].split(".")[0] + ".txt"
af_txt = open(analysed_file, "w+")

with open(file_name) as f:
    lines = f.readlines()
f.close()

cnt_error = 0
word = ""

for line in lines:
    if file_type == "log":
        try:
            word = line.split("\t")[0]
            in_dict = line.split("\t")[1]
        except IndexError:
            print("error in line", line)
            cnt_error += 1
    else:
        if ":" in line:
            word = line.split(":")[0].replace("_", " ")
    p = Popen('echo "'+ word + '"' + cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    analyses = out.decode()
    if file_type == "log":
        af_txt.write(word + "\t" + in_dict + analyses + ":\n")
    else:
        af_txt.write(word + "\n" + analyses + ":\n")

af_txt.close()
