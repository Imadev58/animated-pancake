import os

def run_python_files():
    current_directory = os.getcwd()
    python_files = [file for file in os.listdir(current_directory) if file.endswith('.py')]

    for py_file in python_files:
        try:
            os.system(f'python {py_file}')
            print(f"Successfully ran {py_file}")
        except Exception as e:
            print(f"Error running {py_file}: {e}")

if __name__ == "__main__":
    run_python_files()
