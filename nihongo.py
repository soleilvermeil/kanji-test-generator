import pandas as pd
from math import floor
import random
import os
import argparse

# +-----------------------+
# | Setting up the parser |
# +---------------------- +

parser = argparse.ArgumentParser(
    description="This program gnerates a test in order to evaluate the knowledge of kanjis of students. This program generates a LaTeX file made of grids that the students have to fill. These files are then automatically converted into a PDF if pdflatex is available on the current computer. In order to find out if pdflatex is correcly installed, try running 'pdflatex -v'. If it raises an error, you can install pdflatex (on Ubuntu) using 'sudo apt-get install texlive-latex-base'.",
)

parser.add_argument("-l", "--language", type=str, default="en", help="Language of the test", choices=["fr", "en"])
parser.add_argument("-t", "--title", type=str, default="Kanji test", help="Title of the document")
parser.add_argument("-st", "--subtitle", type=str, default=r"\begin{CJK}{UTF8}{min}漢字検定\end{CJK}", help="Subtitle of the document")
parser.add_argument("-i", "--instructions", type=str, default="Complete the table below.", help="Instructions for the students")
parser.add_argument("-c", "--columns", type=int, help="Number of columns", required=True)
parser.add_argument("-r", "--rows", type=int, help="Number of rows", required=True)
parser.add_argument("-o", "--output", type=str, help="Name of the folder to store output", default="output")
parser.add_argument("-s", "--seed", type=int, help="Seed for the random generator", default=-1)

# TODO
# Add field "kanji2word ratio and word2kanji ratio (default 0.5 and 0.5)"
# Add field "kanji2word score (default 1)"
# Add field "word2kanji score (default 1)"

args = parser.parse_args()

# +--------------------------------------------+
# | Importing files and sorting the valid rows |
# +--------------------------------------------+

df__ = pd.read_csv("words.csv", sep=";")

print(df__.to_markdown())

first_zero_idx = df__.query("fr == '?'").index[0]
last_index = floor((first_zero_idx - 1) / 5) * 5

df_ = df__.iloc[:last_index]

# +------------------------------------------------------------+
# | Defining some variables for the generation of the document |
# +------------------------------------------------------------+

DOCUMENT: str = None
with open("model/document.txt", "r") as f:
    DOCUMENT = f.read()

CONTENT: str = None
with open("model/content.txt", "r") as f:
    CONTENT = f.read()

WORD: str = None
with open("model/word.txt", "r") as f:
    WORD = f.read()
    
if args.seed != -1:
    random.seed(args.seed)

# +------------------------------------------------------------------------+
# | Setting some variables. They will then influence which rows are picked |
# +------------------------------------------------------------------------+

COLS = args.columns
ROWS = args.rows

assert COLS * ROWS % 2 == 0, "The product of the number of rows and columns must be even"

FONTSIZE = int(200 / COLS)
TRUEFALSE = [True] * int(COLS * ROWS / 2) + [False] * int(COLS * ROWS / 2)
random.shuffle(TRUEFALSE)
print(TRUEFALSE)

# +------------------------------------------------------------+
# | Picking rows according to the previously chosen parameters |
# +------------------------------------------------------------+

df = df_.sample(COLS * ROWS)

# +-------------------------+
# | Generating the document |
# +-------------------------+

for version in ["test", "solution"]:

    rows = []

    for i in range(ROWS * COLS):
        jp = df.iloc[i]["jp"]
        fr = df.iloc[i][args.language]
        word = WORD.replace("@JP@", jp).replace("@FR@", fr).replace("@FONTSIZE@", str(FONTSIZE))
        if version == "test":
            if TRUEFALSE[i]:
                word = word.replace("@COLTITLE@", "black").replace("@COLUPPER@", "white")
            else:
                word = word.replace("@COLTITLE@", "white").replace("@COLUPPER@", "black")
        elif version == "solution":
            word = word.replace("@COLTITLE@", "black").replace("@COLUPPER@", "black")
        else:
            raise ValueError("Version must be 'test' or 'solution'")
        rows.append(word)
        
    content = CONTENT.replace("@COLS@", str(COLS)).replace("@WORDS@", "\n".join(rows))

    document = DOCUMENT.replace("@CONTENT@", content)
    
    document = document.replace("@TITLE@", args.title)
    document = document.replace("@SUBTITLE@", args.subtitle)
    document = document.replace("@INSTRUCTIONS@", args.instructions)
    document = document.replace("@POINTS@", str(COLS * ROWS))

    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    with open(f"{args.output}/{version}.tex", "w") as f:
        f.write(document)

# +-----------------------------+
# | Print the last instructions |
# +-----------------------------+

os.system(f"cd {args.output} && pdflatex test.tex && pdflatex solution.tex && cd ..")
os.system(f"cd {args.output} && rm *.tex *.aux *.log && cd ..")

print("Done !")