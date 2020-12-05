import os
import sys
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from ClassRecord import ClassRecord

def create_output_file(filename):
        currentFileName = filename.partition(".")[0]
        outputFileName = currentFileName + ".vm"
        print("OUTPUT: ", outputFileName)
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
        jack_files_full_path = map(lambda f: input_name + "/" + f, jack_files)
        return jack_files_full_path
    else:
        return [input_name]

def strip_file_name(name):
    if "/" in name:
        name = name.split("/")[-1]
    return name.partition(".")[0]

def main():
    file_names = get_list_of_files()
    class_record = ClassRecord()
    for file in file_names:
        print("INPUT: ", file)
        output_file = create_output_file(file)
        class_record.add_name(strip_file_name(file))
        tokenizer = JackTokenizer(file, class_record)
        CompilationEngine(tokenizer, output_file)
    print("Compiler finished.")

if __name__ == "__main__":
    main()