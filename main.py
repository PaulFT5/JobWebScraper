# main.py
from CvParser.parser import parse_cv
from Utils.LLM import LLM_activation

text = parse_cv()
LLM_activation(text)