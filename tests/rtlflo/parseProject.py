import os
import sys
import re
from glob import glob
import yaml
import json

def replaceEnvironVar(x):
    h = re.findall(r"\${(\w+)}", x)
    for g in h:
        if not g in os.environ.keys():
            raise Exception(f"Environments variable: ${g} not set")
        y = os.environ[g]
        y = re.sub('\\\\', "/", y)
        x = re.sub(f"\\${{{g}}}", y, x)
    return x

class rtlFile:
    def __init__(self, input):
        self.path = None
        self.lib = None
        self._rtl_style = None
        if isinstance(input, dict):
            for library in input:
                self.lib = library
                self.path = input[library]
        else:
            self.lib = None
            self.path = input
        
        self.path = replaceEnvironVar(self.path)
        x = self.path.split(',')
        self.path = x[0]
        try:
          self._rtl_style = x[1]
        except IndexError:
            pass
        if not os.path.isfile(self.path):
            raise Exception(f"Unknown file: {self.path}")
        
    @property
    def relpath(self):
        return os.path.relpath(self.path)
    
    @property
    def ext(self):
        return os.path.splitext(self.path)[1]
    
    @property
    def rtl_style(self):
        if not self._rtl_style is None:
            return self._rtl_style
        if ".vhd" == self.ext or ".vhdl" == self.ext:
            return 'VHDL 2008'
        else:
            return None
    
    def __str__(self):
        return f"path: {self.relpath} lib: {self.lib}"

    @property
    def simfile(self):
        if ".xci" == self.ext:
            workdir =  os.path.dirname(self.path)
            files = glob(f"{workdir}/*_sim_netlist*.vhd*")
            if not 1 == len(files):
                raise Exception(f"Cannot find sim file in {workdir}")
            else:
                return os.path.relpath(files[0])
        else:
            return os.path.relpath(self.path)
 
class parseProject:

    attr_list = [
        "lib_files",
        "sim_files",
        "syn_files",
        "common_files",
        "libraries",
        "generics",
        "external_libraries",
    ]
    
    def __init__(self):
        self.config_head = "project_list"
        
        self.test_top = None
        self.synth_top = None
        self.part = None
        #self.lib_files = []
        self.sim_files = []
        self.syn_files = []
        self.bd_designs = []
        self.tcl_files = {}
        self.elf_files = {}
        self.design_runs = {}
        self.common_files = []
        self.constraints_files = []
        self.ip_files = []
        self.libraries = []
        self.generics = {}
        self.custom_vivado = []
        self.external_libraries = {}
        self.include_dirs = []
        self.platform = sys.platform
            
    @property
    def config(self):
        e = {}
        for attr in self.attr_list:
            e[attr] = getattr(self, attr)
        return e
    
    @property
    def config_yml(self):
        return f"{self.config_head}.yml"
    
    @property
    def config_json(self):
        return f"{self.config_head}.json"
    
    def parseSetup(self):
        self.readYaml()
        
        if self.sim_files is None:
            self.sim_files = []
        if self.syn_files is None:
            self.syn_files = []
        if self.common_files is None:
            self.common_files = []
        
        if not 'XILINX_PART' in os.environ.keys():
            os.environ['XILINX_PART'] = self.part
        if not 'XILINX_REV' in os.environ.keys():
            os.environ['XILINX_REV'] = '2018.2'
#         if not 'XILINX_LIB' in os.environ.keys():
#             os.environ['XILINX_LIB'] = 'C:\\\\storage\\\\projects\\\\modelsim_lib'

        if not 'VIVADO_PATH' in os.environ.keys():

            if self.platform.startswith("win"):
                os.environ['VIVADO_PATH'] = f"C:\\\\Xilinx\\\\Vivado\\\\{os.environ['XILINX_REV']}"
            elif self.platform.startswith("linux"):
                os.environ['VIVADO_PATH'] = f"/opt/Xilinx/Vivado/{os.environ['XILINX_REV']}/bin/vivado"
            else:
                os.environ['VIVADO_PATH'] = f"/cygdrive/c/Xilinx/Vivado/{os.environ['XILINX_REV']}"
        if not self.external_libraries is None:
            for library, path in self.external_libraries.items():
                self.external_libraries[library] = replaceEnvironVar(path)
        
        if not self.generics is None:
            for key, val in self.generics.items():
                if os.path.isfile(val):
                    val = os.path.abspath(val)
                    if g := re.search("/cygdrive/(.)", val):
                        val = re.sub(g.group(0), f"{g.group(1).upper()}:", val) 
                    val = re.sub('\\\\', "/", val)
                    self.generics[key] = val
        
        if not self.custom_vivado is None:
            cmds = []
            for cmd in self.custom_vivado:
                cmd = replaceEnvironVar(cmd)
                cmds.append(cmd)
            self.custom_vivado = cmds
        if not self.include_dirs is None:
            cmds = []
            for cmd in self.include_dirs:
                cmd = replaceEnvironVar(cmd)
                cmds.append(cmd)
            self.include_dirs = cmds
    
    def pathfiles(self, infiles):
        files = []
        if not infiles is None:
            newfiles = []
            for x in infiles:
                incfiles = []
                if os.path.isdir(x):
                    incfiles = glob(f"{x}/*")
                    newfiles.extend(incfiles)
                else:
                    newfiles.append(x)
            for x in newfiles:
                y = rtlFile(x)
                files.append(y)
        return files

    def readYaml(self):
        with open(self.config_yml) as f:
            config = yaml.safe_load(f)
        for attr, value in config.items():
            if not hasattr(self, attr):
                raise Exception(f"Missing Attribute: {attr}\n{config.items()}")
            setattr(self, attr, value)
            
    def readJson(self):
        with open(self.config_json) as f:
            config = json.load(f)
        for attr, value in config.items():
            if not hasattr(self, attr):
                raise Exception()
            setattr(self, attr, value)
            
    def writeYaml(self):
        with open(self.config_yml, 'w') as f:
            yaml.dump(self.config, f)
            
    def writeJson(self):
        with open(self.config_json, 'w') as f:
            json.dump(self.config, f)
