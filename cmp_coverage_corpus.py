# -*- coding:utf-8 -*-
'''
This script checks:
1. how many compunds in corpus
2. how many compunds are lexicalised
3. PoS for top element of compound

The script will create results_corpus.txt with results for 1., 2. and 3.

Usage:
    python3 cmp_coverage_corpus.py
'''

import sys, os
import csv
import re
from subprocess import Popen, PIPE


def check_in_dict(pos_key, pos_value, pos_dict):
    if pos_key in pos_dict:
        pos_dict[pos_key] += pos_value
    else:
        pos_dict[pos_key] = pos_value
    return

def check_pos(parts):
    bad_pos = ["G3", "G7", "IV", "TV", "Cmp", "Comp", "Sg", "Nom"]
    for idx, part in enumerate(parts):
        if part:
            if part not in bad_pos and not "/" in part and not part.startswith("v") and not part.startswith("#"):
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

def write_results(dict, num_elem, cnt, tot_dict, f):
    for key, value in dict.items():
        rf_txt.write("Number of compounds with " + str(num_elem) + " elements with " + f + " with pos '" + str(key) + "': " + str(value) + "\n")
        rf_txt.write("Percentage of compounds with " + str(num_elem) + " elements with " + f + " with pos '" + str(key) + "': " + str(round(value/cnt*100, 2)) + "%" + "\n")
        check_in_dict(key, value, tot_dict)
    return

def write_tot_results(dict, num_elem, cnt, f):
    for key, value in dict.items():
        rf_txt.write("Total number of compounds with " + str(num_elem) + " elements with " + f + " with pos '" + str(key) + "': " + str(value) + "\n")
        rf_txt.write("Total percentage of compounds with " + str(num_elem) + " elements with " + f + " with pos '" + str(key) + "': " + str(round(value/cnt*100, 2)) + "%" + "\n")
    return

lemma = []
analysis = []
count_tabs = []
pos = []
is_cmp = False
tot_tokens = 0
tot_cnt_cmp = 0
tot_cmp_parts = {}
tot_cmp_pos = {}
tot_cmp_lex = {}
tot_cnt_is_cmp2, tot_cnt_is_cmp3, tot_cnt_is_cmp4, tot_cnt_is_cmp5, tot_cnt_is_cmp6, tot_cnt_is_cmp7 = 0, 0, 0, 0, 0, 0
tot_cmp_pos2_f, tot_cmp_pos3_f, tot_cmp_pos4_f, tot_cmp_pos5_f, tot_cmp_pos6_f, tot_cmp_pos7_f = {}, {}, {}, {}, {}, {}

results_file = "results_corpus.txt"
rf_txt = open(results_file, "w+")

for file in os.listdir("data"):
    if file.endswith(".dep"):
        print(os.path.join("data", file))
        dep_file = os.path.join("data", file)
        with open(dep_file) as f:
            lines = f.readlines()
        f.close()

        cnt_token = 0
        cnt_cmp = 0
        cmp_percent = 0
        cmp_parts = {}
        cmp_pos = {}
        cmp_pos_lex = {}
        cnt_is_cmp2, cnt_is_cmp3, cnt_is_cmp4, cnt_is_cmp5, cnt_is_cmp6, cnt_is_cmp7 = 0, 0, 0, 0, 0, 0
        cnt_is_cmp_lex = 0
        cmp_pos_lex = {}
        cmp_pos2_f, cmp_pos3_f, cmp_pos4_f, cmp_pos5_f, cmp_pos6_f, cmp_pos7_f = {}, {}, {}, {}, {}, {}
        rf_txt.write("Results for file: " + dep_file.split("/")[1].split(".")[0] + "\n")

        for line in lines:
            if '"<' in line:
                token = line.split('"<')[1].split('>"')[0]
                cnt_token += 1
            regex=re.compile('\s*:')
            if not ('"<' in line or re.match(regex, line) or line.startswith('\n')):
                try:
                    if not line.split('"')[1] in lemma:
                        count_tabs.append(line.count('\t'))
                        current_tabs = line.count('\t')
                        max_tabs = max(count_tabs)
                        more_tabs = [x for x in count_tabs if x>1]
                        # If there are >1 analyses, take only the first one
                        if not current_tabs<max_tabs and count_tabs.count(current_tabs)<2:
                            if not '"""' in line:
                                lemma.append(line.split('"')[1])
                                analysis.append(line.split('"')[2])
                                parts = line.split('"')[2].split(" ")[1:]
                                #print("parts=", parts)
                                real_pos = check_pos(parts)
                                pos.append(real_pos)
                            else:
                                lemma.append(line.split('"')[1])
                                analysis.append(line.split('"')[3])
                                parts = line.split('"')[3].split(" ")[1:]
                                #print("parts=", parts)
                                real_pos = check_pos(parts)
                                pos.append(real_pos)
                except IndexError:
                    pass

            if line.startswith(":"):
                cmp_matches = [x for x in analysis if "cohort-with-dynamic-compound" in x]
                if cmp_matches:
                    is_cmp = True
                    cnt_cmp += 1
                    if len(lemma) == 1:
                        cnt_is_cmp_lex += 1
                        check_in_dict(pos[0], 1, cmp_pos_lex)
                    if len(lemma) == 2:
                        cnt_is_cmp2 += 1
                        check_in_dict(pos[0], 1, cmp_pos2_f)
                    if len(lemma) == 3:
                        cnt_is_cmp3 += 1
                        check_in_dict(pos[0], 1, cmp_pos3_f)
                    if len(lemma) == 4:
                        cnt_is_cmp4 += 1
                        check_in_dict(pos[0], 1, cmp_pos4_f)
                    if len(lemma) == 5:
                        cnt_is_cmp5 += 1
                        check_in_dict(pos[0], 1, cmp_pos5_f)
                    if len(lemma) == 6:
                        cnt_is_cmp6 += 1
                        check_in_dict(pos[0], 1, cmp_pos6_f)
                    if len(lemma) == 7:
                        cnt_is_cmp7 += 1
                        check_in_dict(pos[0], 1, cmp_pos7_f)
                    check_in_dict(len(lemma), 1, cmp_parts)
                lemma = []
                analysis = []
                count_tabs = []
                pos = []
                is_cmp = False
                real_pos = ""

        tot_tokens += cnt_token
        tot_cnt_cmp += cnt_cmp
        tot_cnt_is_cmp2 += cnt_is_cmp2
        tot_cnt_is_cmp3 += cnt_is_cmp3
        tot_cnt_is_cmp4 += cnt_is_cmp4
        tot_cnt_is_cmp5 += cnt_is_cmp5
        tot_cnt_is_cmp6 += cnt_is_cmp6
        tot_cnt_is_cmp7 += cnt_is_cmp7

        rf_txt.write("Number of tokens: " + str(cnt_token) + "\n")
        rf_txt.write("Number of compounds: " + str(cnt_cmp) + "\n")
        rf_txt.write("Percentage of compounds: " + str(round(cnt_cmp/cnt_token*100, 2)) + "%" + "\n")
        for key, value in cmp_parts.items():
            rf_txt.write("Number of compounds with " + str(key) + " elements: " + str(value) + "\n")
            rf_txt.write("Percentage of compounds with " + str(key) + " elements: " + str(round(value/cnt_cmp*100, 2)) + "%" + "\n")
            if key in tot_cmp_parts:
                tot_cmp_parts[key] += value
            else:
                tot_cmp_parts[key] = value
        rf_txt.write("==========================" + "\n")
        rf_txt.write("Number of compounds that are lexicalised: " + str(cmp_parts[1]) + "\n")
        rf_txt.write("Percentage of compounds that are lexicalised: " + str(round(cmp_parts[1]/cnt_cmp*100, 2)) + "%" + "\n")
        for key, value in cmp_pos_lex.items():
            rf_txt.write("Number of compounds that are lexicalised with pos '" + str(key) + "': " + str(value) + "\n")
            rf_txt.write("Percentage of compounds that are lexicalised with pos '" + str(key) + "': " + str(round(value/cnt_is_cmp_lex*100, 2)) + "%" + "\n")
            check_in_dict(key, value, tot_cmp_lex)
        rf_txt.write("==========================" + "\n")
        write_results(cmp_pos2_f, 2, cnt_is_cmp2, tot_cmp_pos2_f, "f")
        rf_txt.write("==========================" + "\n")
        write_results(cmp_pos3_f, 3, cnt_is_cmp3, tot_cmp_pos3_f, "f")
        rf_txt.write("==========================" + "\n")
        write_results(cmp_pos4_f, 4, cnt_is_cmp4, tot_cmp_pos4_f, "f")
        rf_txt.write("==========================" + "\n")
        write_results(cmp_pos5_f, 5, cnt_is_cmp5, tot_cmp_pos5_f, "f")
        rf_txt.write("==========================" + "\n")
        write_results(cmp_pos6_f, 6, cnt_is_cmp6, tot_cmp_pos6_f, "f")
        rf_txt.write("==========================" + "\n")
        write_results(cmp_pos7_f, 7, cnt_is_cmp7, tot_cmp_pos7_f, "f")
        rf_txt.write("=====================================================================" + "\n")

# Total
rf_txt.write("Total number of tokens: " + str(tot_tokens) + "\n")
rf_txt.write("Total number of compounds: " + str(tot_cnt_cmp) + "\n")
rf_txt.write("Total percentage of compounds: " + str(round(tot_cnt_cmp/tot_tokens*100, 2)) + "%" + "\n")
for key, value in tot_cmp_parts.items():
    rf_txt.write("Total number of compounds with " + str(key) + " elements: " + str(value) + "\n")
    rf_txt.write("Total percentage of compounds with " + str(key) + " elements: " + str(round(value/tot_cnt_cmp*100, 2)) + "%" + "\n")
rf_txt.write("==========================" + "\n")
write_tot_results(tot_cmp_pos2_f, 2, tot_cnt_is_cmp2, "f")
rf_txt.write("==========================" + "\n")
write_tot_results(tot_cmp_pos3_f, 3, tot_cnt_is_cmp3, "f")
rf_txt.write("==========================" + "\n")
write_tot_results(tot_cmp_pos4_f, 4, tot_cnt_is_cmp4, "f")
rf_txt.write("==========================" + "\n")
write_tot_results(tot_cmp_pos5_f, 5, tot_cnt_is_cmp5, "f")
rf_txt.write("==========================" + "\n")
write_tot_results(tot_cmp_pos6_f, 6, tot_cnt_is_cmp6, "f")
rf_txt.write("==========================" + "\n")
write_tot_results(tot_cmp_pos7_f, 7, tot_cnt_is_cmp7, "f")
rf_txt.write("=====================================================================" + "\n")

rf_txt.close()
