# -*- coding:utf-8 -*-
'''
This script checks:
1. how many compunds in NDS log file are covered covered by NDS
2. how many compunds in NDS are covered by fst (lemmas taken from smenob-all.lexc that can be generated in ~/main/words/dicts/smenob/bin)

The script will create results_nds.txt with results for 1. and 2.

Usage:
    python3 cmp_coverage_nds.py <PATH_ANALYSED_LOG_FILE> <PATH_ANALYSED_LEXC_FILE>

Ex.:
    python3 cmp_coverage_nds.py analysed_user_input_2019_su.txt analysed_smenob-all.txt
'''

import sys
import csv
import lxml.etree
from lxml.etree import ElementTree as ET
from lxml.etree import Element, SubElement, XMLParser
from subprocess import Popen, PIPE
from xml.dom import minidom


def check_in_dict(pos_key, pos_dict):
    if pos_key in pos_dict:
        pos_dict[pos_key] += 1
    else:
        pos_dict[pos_key] = 1
    return

def check_pos(parts):
    bad_pos = ["G3", "G7", "IV", "TV", "Cmp", "Comp", "Sg", "Nom", "Acc"]
    for idx, part in enumerate(parts):
        if part:
            if part not in bad_pos and not "/" in part and not part.startswith("v"):
                if part == "N":
                    if idx < len(parts)-1:
                        next_part = parts[(idx + 1)]
                        if next_part == "Prop":
                            return "NProp"
                        else: return part
                    else: return part
                else: return part
        else:
            return ""

def write_results(file_name, file_type):
    cnt_error = 0
    cmp_parts_tot = {}
    cmp_pos_lex, cmp_pos2_f, cmp_pos3_f, cmp_pos4_f, cmp_pos5_f = {}, {}, {}, {}, {}
    words = []
    cnt_in_dict = 0
    cnt_is_cmp, cnt_is_cmp_lex, cnt_is_cmp2, cnt_is_cmp3, cnt_is_cmp4, cnt_is_cmp5 = 0, 0, 0, 0, 0, 0
    cnt_is_lex = 0
    cnt_not_an = 0
    tot_analyses = []
    analyses = []
    in_dict = []

    with open(file_name) as f:
        lines = f.readlines()
    f.close()

    for line in lines:
        word = ""
        pos_lex, pos2_f, pos3_f, pos4_f, pos5_f = "", "", "", "", ""
        if not line.startswith(":\n"):
            if file_type == "log":
                if len(line.split("\t")) == 2 and not "+" in line.split("\t")[1]:
                    word = line.split("\t")[0]
                    words.append(word)
                    if "True" in line.split("\t")[1]:
                        cnt_in_dict += 1
                        in_dict.append("True")
                    else:
                        in_dict.append("False")
                else:
                    analyses.append(line)
            else:
                if len(line.split("\t")) == 1:
                    word = line.split("\t")[0]
                    words.append(word)
                else:
                    analyses.append(line)
        else:
            tot_analyses.append(analyses)
            analyses = []

    cnt_cmp_in_dict = 0

    for idx, analysis_array in enumerate(tot_analyses):
        is_cmp = False
        is_lex = False
        is_cmp_lex = False
        cmp_parts = 0
        for analysis in analysis_array:
            analysis = analysis.split("\n")
            for single_an in analysis:
                if "?" in single_an:
                    single_an = "+?"
                    cnt_not_an += 1
                elif single_an:
                    if "¨" in single_an:
                        cnt_error += 1
                    else:
                        single_an = single_an.split("\t")[1]
                        if "Cmp#" in single_an:
                            is_cmp = True
                            cmp_parts = len(single_an.split("Cmp#"))
                            if cmp_parts == 2:
                                pos2_f = check_pos(single_an.split("Cmp#")[-1].split("+")[1:])
                            if cmp_parts == 3:
                                pos3_f = check_pos(single_an.split("Cmp#")[-1].split("+")[1:])
                            if cmp_parts == 4:
                                pos4_f = check_pos(single_an.split("Cmp#")[-1].split("+")[1:])
                            if cmp_parts == 5:
                                pos5_f = check_pos(single_an.split("Cmp#")[-1].split("+")[1:])
                        else:
                            is_lex = True
                            pos_lex = check_pos(single_an.split("+")[1:])
        if is_cmp:
            cnt_is_cmp += 1
            if in_dict and in_dict[idx] == "True":
                cnt_cmp_in_dict += 1
        if is_lex:
            cnt_is_lex += 1
        if is_cmp and is_lex:
            is_cmp_lex = True
            cnt_is_cmp_lex += 1
            check_in_dict(pos_lex, cmp_pos_lex)
        if not is_cmp_lex:
            if cmp_parts == 2:
                cnt_is_cmp2 += 1
                check_in_dict(pos2_f, cmp_pos2_f)
            if cmp_parts == 3:
                cnt_is_cmp3 += 1
                check_in_dict(pos3_f, cmp_pos3_f)
            if cmp_parts == 4:
                cnt_is_cmp4 += 1
                check_in_dict(pos4_f, cmp_pos4_f)
            if cmp_parts == 5:
                cnt_is_cmp5 += 1
                check_in_dict(pos5_f, cmp_pos5_f)
            check_in_dict(cmp_parts, cmp_parts_tot)

    if file_type == "log":
        rf_txt.write("Results for log file" + "\n")
        rf_txt.write("Number of unique user searches: " + str(len(words)) + "\n")
        rf_txt.write("Number of user searches that are in dictionary: " + str(cnt_in_dict) + "\n")
        rf_txt.write("Percentage of user searches that are in dictionary: " + str(round(cnt_in_dict/len(words)*100, 2)) + "%"+ "\n")
        rf_txt.write("Number of user searches that do not get an analysis: " + str(cnt_not_an) + "\n")
        rf_txt.write("Percentage of user searches that do not get an analysis: " + str(round(cnt_not_an/len(words)*100, 2)) + "%" + "\n")
        rf_txt.write("Number of user searches that are compounds: " + str(cnt_is_cmp) + "\n")
        rf_txt.write("Percentage of user searches that are compounds: " + str(round(cnt_is_cmp/len(words)*100, 2)) + "%" + "\n")
        rf_txt.write("Number of user searches that are compounds that get a translation: " + str(cnt_cmp_in_dict) + "\n")
        rf_txt.write("Percentage of user searches that are compounds that get a translation: " + str(round(cnt_cmp_in_dict/cnt_is_cmp*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        rf_txt.write("Number of user searches that are compounds that are lexicalised: " + str(cnt_is_cmp_lex) + "\n")
        rf_txt.write("Percentage of user searches that are compounds that are lexicalised: " + str(round(cnt_is_cmp_lex/cnt_is_cmp*100, 2)) + "%" + "\n")
        for key, value in cmp_pos_lex.items():
            rf_txt.write("Number of compounds that are lexicalised, with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp_lex*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_parts_tot.items():
            if not key == 0:
                rf_txt.write("Number of compounds with '" + str(key) + "' elements: " + str(value) + "\n")
                rf_txt.write("Percentage of compounds with '" + str(key) + "' elements: " + str(round(value/(cnt_is_cmp-cnt_is_cmp_lex)*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos2_f.items():
            rf_txt.write("Number of compounds with 2 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 2 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp2*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos3_f.items():
            rf_txt.write("Number of compounds with 3 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 3 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp3*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos4_f.items():
            rf_txt.write("Number of compounds with 4 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 4 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp4*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos5_f.items():
            rf_txt.write("Number of compounds with 5 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 5 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp5*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        rf_txt.write("Number of skipped lines because of errors: " + str(cnt_error) + "\n")
        rf_txt.write("Number of skipped lines because of errors: " + str(cnt_error) + "\n")
        rf_txt.write("\n=====================================================================\n" + "\n")
    else:
        rf_txt.write("Results for xml file" + "\n")
        rf_txt.write("Number of entries in dictionary: " + str(len(words)) + "\n")
        rf_txt.write("Number of entries that do not get an analysis: " + str(cnt_not_an) + "\n")
        rf_txt.write("Percentage of entries that do not get an analysis: " + str(round(cnt_not_an/len(words)*100, 2)) + "%" + "\n")
        rf_txt.write("Number of entries that are compounds: " + str(cnt_is_cmp) + "\n")
        rf_txt.write("Percentage of entries that are compounds: " + str(round(cnt_is_cmp/len(words)*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        rf_txt.write("Number of entries that are compounds that are lexicalised: " + str(cnt_is_cmp_lex) + "\n")
        rf_txt.write("Percentage of entries that are compounds that are lexicalised: " + str(round(cnt_is_cmp_lex/cnt_is_cmp*100, 2)) + "%" + "\n")
        for key, value in cmp_pos_lex.items():
            rf_txt.write("Number of compounds that are lexicalised, with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp_lex*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_parts_tot.items():
            if not key == 0:
                rf_txt.write("Number of compounds with '" + str(key) + "' elements: " + str(value) + "\n")
                rf_txt.write("Percentage of compounds with '" + str(key) + "' elements: " + str(round(value/(cnt_is_cmp-cnt_is_cmp_lex)*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos2_f.items():
            rf_txt.write("Number of compounds with 2 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 2 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp2*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos3_f.items():
            rf_txt.write("Number of compounds with 3 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 3 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp3*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")
        for key, value in cmp_pos4_f.items():
            rf_txt.write("Number of compounds with 4 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 4 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp4*100, 2)) + "%" + "\n")
        for key, value in cmp_pos5_f.items():
            rf_txt.write("Number of compounds with 5 elements with f with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with 5 elements with f with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp5*100, 2)) + "%" + "\n")
        rf_txt.write("==========================" + "\n")

    return


analysed_log_file = sys.argv[1]
analysed_lexc_file = sys.argv[2]

results_file = "results_nds.txt"
rf_txt = open(results_file, "w+")

'''
Check how many cmp in NDS log file are in NDS lexicon
'''
write_results(analysed_log_file, "log")
print("*** Done log file")

'''
Check how many cmp in NDS are covered by fst
'''
write_results(analysed_lexc_file, "xml")
print("*** Done xml file")

rf_txt.close()
