import os, subprocess, shutil

def main():
    script = "main.py" #name of script to compile
    name = "particle-life" #name of compiled executable

    command = [
        "pyinstaller",
        script,
        "--onefile",  #create a single executable file
        "--noconfirm",  #skip confirmation prompts
        "--clean",  #clean up previous build files
        "--noconsole",  #no terminal window appears when program is run
        f"--name={name}",  #new name of executable
        "--distpath=.",  #where the executable is saved - '.' means current directory
    ]

    if os.path.exists("requirements.txt"):  #reads from the requirements.txt file for necessary modules
        with open("requirements.txt", "r") as f:
            imports = [line.strip() for line in f if line.strip()]

    numba = [  #necessary as compiling a project with numba is a nightmare
        "numba.core.types.old_scalars",
        "numba.core.datamodel.old_models",
        "numba.cpython.old_builtins",
        "numba.core.typing.old_builtins",
        "numba.core.typing.old_cmathdecl",
        "numba.core.typing.old_mathdecl",
        "numba.cpython.old_hashing",
        "numba.cpython.old_numbers",
        "numba.cpython.old_tupleobj",
        "numba.np.old_arraymath",
        "numba.np.random.old_distributions",
        "numba.np.random.old_random_methods",
        "numba.cpython.old_mathimpl",
        "numba.core.old_boxing",
    ]

    for module in imports + numba:
        command += [f"--hidden-import={module}"] #compile modules too
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
    finally:
        if os.path.exists(f"{name.split('.')[0]}.spec"): os.remove(f"{name.split('.')[0]}.spec") #deletes .spec file
        if os.path.exists("build"): shutil.rmtree("build") #deletes temporary build directory
    
if __name__ == "__main__":
    main()