import os
import sys
sys.dont_write_bytecode = True
import json
import argparse

from src.multi_step.score import generate_score
# game
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Main function to load models and process games
def main():

    generate_score()

if __name__ == "__main__":
    main()
