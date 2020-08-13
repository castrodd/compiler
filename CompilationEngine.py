def main():
    file_or_directory = get_list_of_files()
    for file in file_or_directory:
       tokenized_file = JackTokenizer(file)
       output_file = OutputFile(file)
       compiled_file = CompilationEngine(tokenized_file, output_file)
       write_file(compiled_file)
    print("Compiler finished.")

if __name__ == "__main__":
    main()