import os
import re
from vunit import VUnit
from glob import glob
from parseProject import parseProject

class baseTest:
    def __init__(self, dir):
        self.dir = os.path.relpath(dir)
        self.valid = False
        self.generics = {
        }
        self.testname = self.dir.split('/')[-1]

    def __str__(self):
        return self.testname

    def __repr__(self):
        return f"{self.testname} - self.generics"

class dkTest(baseTest):
    def __init__(self, dir):
        super().__init__(dir)

        self.generics = {
            'G_AXIFILE0': None, 
            'G_AXIFILE1': None, 
            'G_AXIFILE2': None, 
            'G_AXIFILE3': None, 
            'G_INFRAME0': None, 
            'G_INFRAME1': None, 
            'G_INFRAME2': None, 
            'G_INFRAME3': None, 
            'G_OUTFRAME0': None, 
            'G_OUTFRAME1': None, 
            'G_OUTFRAME2': None, 
            'G_OUTFRAME3': None, 
            'G_JTAG_DEBUG': 'false', 
        }
        files = glob(f"{self.dir}/axi*.cmds")
        
        short_version = False
        long_version = False
        for file in files:
            if file.endswith("axi.cmds"):
                short_version = True
            if file.endswith("axi_0.cmds"):
                long_version = True
        if short_version and long_version:
            raise Exception(f"Short version and long version of axi file names used, pick one!")
        
        for i, file in enumerate(files):
            filename = os.path.abspath(file)
            filename = re.sub('\\\\', "/", filename)
            self.generics[f"G_AXIFILE{i}"] = filename
            self.valid = True
        
        files = glob(f"{self.dir}/inframe*.cmds")
        for i, file in enumerate(files):
            filename = os.path.abspath(file)
            filename = re.sub('\\\\', "/", filename)
            self.generics[f"G_INFRAME{i}"] = filename
            self.valid = True

        files = glob(f"{self.dir}/outframe*.cmds")
        for i, file in enumerate(files):
            filename = os.path.abspath(file)
            filename = re.sub('\\\\', "/", filename)
            self.generics[f"G_OUTFRAME{i}"] = filename
            self.valid = True

class collectTestsDirs:
    def __init__(self):
        self.tests = []
        dirs = glob("./test*")
        for dir in dirs:
            self.tests.append(dkTest(dir))
    
    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        try:
            while True:
                x = self.tests[self.a]
                self.a += 1
                if x.valid:
                    break
        except IndexError:
            raise StopIteration
        
        return x

class tb_runner:
    
    def __init__(self):
        self.project = parseProject()
        self.ui = VUnit.from_argv()
        self.defaultlib = 'worklib'
        self.libs  = []
        self.project.parseSetup()
        
        self.tests = collectTestsDirs()

    def getlib(self, x):
        if x is None:
            x = self.defaultlib
        try:
            lib = self.ui.add_library(x)
            self.libs.append(lib)
            return lib
        except ValueError:
            for lib in self.libs:
                if x == lib.name:
                    return lib
    
    @property
    def worklib(self):
        return self.libs[0]


    def startproject(self):
        for library, path in self.project.external_libraries.items():
            self.ui.add_external_library(library, path)

        # Add default compile directory first
        for library in self.project.libraries:
            self.defaultlib = library
        
        lib = self.ui.add_library(self.defaultlib)
        self.libs.append(lib)
        
        files = []
        files.extend(self.project.common_files)
        files.extend(self.project.sim_files)
        for file in self.project.pathfiles(files):
            library = file.lib
            path = file.simfile
            lib = self.getlib(library)
            lib.add_source_files(path)

        self.top = self.worklib.entity(self.project.test_top)
        
        for t in self.tests:
            generics = t.generics | self.project.generics
            #print(t.testname, generics)
            self.top.add_config(name=t.testname, generics=generics)

    def runproject(self):
        self.ui.main()
