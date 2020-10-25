import os
import sys
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer

def create_output_file(filename):
        currentFileName = filename.partition(".")[0]
        outputFileName = currentFileName + ".xml"
        outputFile = open(outputFileName, 'a+')
        return outputFile

def is_jack_file(fileName):
    return os.path.basename(fileName).partition(".")[2] == "jack"

def get_list_of_files():
    try:
        input_name = sys.argv[1]
    except IndexError:
        raise SystemExit("Usage: {} <input filename/directory>".format(sys.argv[0]))

    is_directory = os.path.isdir(input_name)
    if is_directory:
        list_of_all_files = os.listdir(input_name)
        jack_files = filter(is_jack_file, list_of_all_files)
        return jack_files
    else:
        return [input_name]

def main():
    file_or_directory = get_list_of_files()
    for file in file_or_directory:
       tokenizer = JackTokenizer(file)
       output_file = create_output_file(file)
       CompilationEngine(tokenizer, output_file)
    print("Compiler finished.")

if __name__ == "__main__":
    main()