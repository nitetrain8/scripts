Intro:
    Merge.exe is a command-line based utility for intelligently updating PBS config files during customer software updates. It incorporates logic from scripts that I have been using since the original v3.0 release to visualize the differences between customers' config files and the new default files that were released with 3.0. 
    
    The comparison logic works on the assumption that PBS provides reasonable defaults and customers accept that PBS selects reasonable defaults when leaving the factory, but that customers who make changes to defaults do so for intelligent reasons. The logic therefore works (generally) as follows:
    
        For each variable in the new default config file:
            check the user's value and old default value
            if the user's value differs from the old default:
                update the new file with the user's value


Requirements to build merge.exe:

    - Python 3 or higher
    - PyInstaller (run pip install pyinstaller)

    Instructions:
    1. Install python of the desired type (32 bit or 64 bit). The bitness MUST match what's on the bioreactor, or else the EXE will fail.
    2. Install pyinstaller: pip install pyinstaller
    3. (Option) install lxml: pip install lxml
    4. Run build.bat. 

The output file will appear magically in the builds folder. 

Requirements to run Unittests:

    - pytest: (run pip install pytest)

    Instructions: 
    1. Navigate to the test/unittests folder
    2. Run test.bat. Optionally, run test.bat --exe to test using the EXE file instead of the python files. This will automatically attempt to build the EXE if any source files have been modified since the EXE was last built, and I don't know what happens if it fails. 
    
    
To add Unittests:

    Most tests are discovered manually at runtime using the following rules:
        Test cases are dynamically loaded from the contents of the unittests/data_files folder. Changing these folder names will prevent the test framework from automatically finding them. All folder names must have the format "[type]_case_files". 

        Each individual test case in the directory is a folder containing files. The folder must start with "case", or it will not be automatically added to the list. Note this can be useful if the case should be specially handled - give it a special name, and load it manually in the corresponding python unittest file. 
        
        Within each folder, the following files must exist with the indicated name patterns:
            - File beginning with "expected_[type]"  -- expected raw file output 
            - File beginning with "new_[type]"       -- new default settings file
            - File beginning with "old_[type]"       -- old default settings file
            - File beginning with "user_[type]"      -- user's settings file
            - File ending with ".patch"              -- patch file
            

    Instructions:
    1. Navigate to unittests/data_files
    2. Find the type of test you want to run, e.g. sysvars. 
    3. Add the corresponding files (see rules above)
    4. Run the unittest suite as normal - you should see the test appear in the list. 