savefile = "savefile.csv"


import csv


export_table = []


with open(savefile, "w") as f:
    csv.writer(f, lineterminator="\n").writerows(export_table)