# main.py
from CvParser.parser import parse_cv
from Utils.setup import setup
from Utils.LLM import LLM_activation

def main():
    #setup() #setup Data files
    parse_cv()