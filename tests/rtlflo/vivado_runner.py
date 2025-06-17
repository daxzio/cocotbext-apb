#!/usr/bin/env python
import os
import sys
import time
import datetime
import re
from glob import glob
from parseProject import parseProject


class vivado_runner:
    def __init__(self):
        # cwd = os.getcwd().split(os.sep)[-1]
        self.project = parseProject()
        self.project.parseSetup()
        # self.name = f"{self.project.synth_top}_{cwd}"
        self.name = f"xpr_{self.project.synth_top}_001"
        # self.dir = f"../{self.name}"
        self.dir = f"./{self.name}"
        self.cpujobs = 6
        self.synthname = "synth_1"
        self.implname = "impl_1"
        self.bitstream = (
            f"{self.dir}/{self.name}.runs/{self.implname}/{self.project.synth_top}.bit"
        )
        self.vivado_rev = os.environ["XILINX_REV"]
        self.vivado_rev_short = re.sub(r"\..+", "", self.vivado_rev)

        self.unique_id = None
        if os.path.isfile(self.bitstream):
            self.date_str = time.ctime(os.path.getctime(self.bitstream))
            self.date_str = datetime.datetime.strptime(self.date_str, "%c")
            self.unique_id = self.date_str.strftime("%y%m%d")

    @property
    def xpr(self):
        files = glob(f"{self.dir}/*.xpr")
        if not 1 == len(files):
            raise Exception(f"Only one file should be returned: {files}")
        # return os.path.relpath(files[0])
        # return os.path.abspath(files[0])
        self.xpr_file = os.path.relpath(files[0])
        self.xpr_file = re.sub("\\\\", "\\\\\\\\", self.xpr_file)
        return self.xpr_file

    def create_project(self):
        self.lines.append(
            f"create_project -force {self.name} {self.dir} -part {self.project.part}"
        )
        # self.lines.append(f"set_property target_language VHDL [current_project]")
        self.lines.append("set_property target_language Verilog [current_project]")

    def open_project(self):
        self.lines.append(f'open_project "{self.xpr}"')

    def close_project(self):
        self.lines.append("close_project")

    def add_files(self):
        files = []
        files.extend(self.project.common_files)
        files.extend(self.project.syn_files)
        self.lines.append("set_msg_config -id {Vivado 12-3645} -new_severity {WARNING}")
        for file in self.project.pathfiles(self.project.constraints_files):
            path = f"{{{file.relpath}}}"
            self.lines.append(f"add_files -fileset constrs_1 -norecurse {path}")
            if not file.rtl_style is None:
                self.lines.append(
                    f"set_property SCOPED_TO_REF {file.rtl_style} [get_files {path}]"
                )
        for file in self.project.pathfiles(files):
            library = file.lib
            path = f"{{{file.relpath}}}"
            # path = re.sub('\\', '\\\\', file.relpath)
            self.lines.append(f"add_files -norecurse {path}")
            if not None is library:
                self.lines.append(f"set_property library {library} [get_files {path}]")
            if "global" == file.rtl_style:
                self.lines.append(
                    f"set_property IS_GLOBAL_INCLUDE 1 [get_files {path}]"
                )
            elif file.rtl_style is not None:
                self.lines.append(
                    f"set_property file_type {{{file.rtl_style}}} [get_files {path}]"
                )
        self.lines.append(
            f"set_property top {self.project.synth_top} [current_fileset]"
        )
        for cmd in self.project.custom_vivado:
            self.lines.append(cmd)
        if not 0 == len(self.project.include_dirs):
            dirs = " ".join(self.project.include_dirs)
            self.lines.append(f"set_property include_dirs {{{dirs}}} [current_fileset]")
        for file in self.project.pathfiles(self.project.sim_files):
            path = f"{{{file.relpath}}}"
            self.lines.append(f"add_files -norecurse {path}")
            self.lines.append(
                f"set_property used_in_synthesis false [get_files {path}]"
            )
            self.lines.append(
                f"set_property used_in_implementation false [get_files {path}]"
            )
        self.lines.append(
            f"set_property top {self.project.synth_top} [get_filesets sim_1]"
        )
        for file in self.project.pathfiles(self.project.bd_designs):
            path = f"{{{file.relpath}}}"
            self.lines.append(f"source {path}")
        for k, j in self.project.tcl_files.items():
            path = os.path.relpath(j)
            self.lines.append(f"add_files -fileset utils_1 -norecurse {path}")
            if "pre_synth" == k:
                self.lines.append(
                    f"set_property STEPS.SYNTH_DESIGN.TCL.PRE [ get_files {path} -of [get_fileset utils_1] ] [get_runs synth_1]"
                )
            elif "post_synth" == k:
                self.lines.append(
                    f"set_property STEPS.SYNTH_DESIGN.TCL.POST [ get_files {path} -of [get_fileset utils_1] ] [get_runs synth_1]"
                )
            else:
                raise Exception(f"Unknown {k}")

    def add_generics(self):
        generic = ""
        if self.project.generics is None:
            return
        for k, j in self.project.generics.items():
            if isinstance(j, int):
                pass
            elif g := re.search('x"(.+)"', j):
                j = f"{len(g.group(1))*4}'h{g.group(1)}"

            generic += f"{k}={j} "
        self.lines.append(
            f"set_property generic {{{generic.rstrip()}}} [current_fileset]"
        )

    def add_elfs(self):
        for k, j in self.project.elf_files.items():
            # print(k, j)
            path = os.path.relpath(j)
            self.lines.append(f"add_files -norecurse {path}")
            self.lines.append(
                f"set_property SCOPED_TO_REF {k} [get_files -all -of_objects [get_fileset sources_1] {{{path}}}]"
            )
            self.lines.append(
                f"set_property SCOPED_TO_CELLS {{ processor/ublaze }} [get_files -all -of_objects [get_fileset sources_1] {{{path}}}]"
            )

    def add_runs(self):
        for k, j in self.project.design_runs.items():
            self.lines.append(
                f"create_run {k} -parent_run synth_1 -flow {{Vivado Implementation {self.vivado_rev_short}}} -strategy {j}"
            )
            self.lines.append(f"current_run [get_runs {k}]")
            self.implname = k

    def run_synth(self):
        self.lines.append(f"launch_runs {self.synthname} -jobs {self.cpujobs}")
        self.lines.append(f"wait_on_run {self.synthname}")

    def run_impl(self):
        self.lines.append(
            f"launch_runs {self.implname} -to_step write_bitstream -jobs {self.cpujobs}"
        )
        self.lines.append(f"wait_on_run {self.implname}")

    def collectInitCmds(self):
        self.create_project()
        self.add_files()
        self.add_elfs()
        self.add_generics()
        self.add_runs()
        self.close_project()

    def collectImplCmds(self):
        self.open_project()
        self.run_synth()
        self.run_impl()
        self.close_project()

    def writeBuildTcl(self):
        self.lines = []
        self.collectInitCmds()
        f = open("build_design.tcl", "w")
        f.write("\n".join(self.lines))
        f.close()

    def writeSynthTcl(self):
        self.lines = []
        self.open_project()
        self.run_synth()
        self.close_project()
        f = open("synth_design.tcl", "w")
        f.write("\n".join(self.lines))
        f.close()

    def writeRunTcl(self):
        self.lines = []
        self.collectImplCmds()
        f = open("run_design.tcl", "w")
        f.write("\n".join(self.lines))
        f.close()

    def reportBitfileName(self):
        print(f"{self.bitstream}")

    def reportProductId(self):
        return f"{self.product_id:04x}"

    def reportVersionId(self):
        return f"{self.version_id:08x}"

    def reportDate(self):
        #         self.date_str = time.ctime(os.path.getctime(self.bitstream))
        #         self.date_str = datetime.datetime.strptime(self.date_str, "%c")
        #         self.unique_id = self.date_str.strftime('%y%m%d')
        #         #xx = time.strftime("%y", self.date_str)
        print(f"{self.unique_id}")
        # print(f"{self.product_id}")


def main(stage="all"):
    v = vivado_runner()
    if "bitfile" == stage:
        v.reportBitfileName()
        return
    if "date" == stage:
        v.reportDate()
        return
    if "date_fpga" == stage:
        print(f"{v.project.synth_top}_{v.reportVersionId()}_{v.unique_id}.bit")
        return
    if "all" == stage or "build" == stage:
        v.writeBuildTcl()
    if "synth" == stage:
        v.writeSynthTcl()
    if "all" == stage or "run" == stage:
        v.writeRunTcl()
    # print("\n".join(v.lines))


if __name__ == "__main__":

    stage = "all"
    if 2 == len(sys.argv):
        stage = sys.argv[1]
    if not stage in ["all", "build", "synth", "run", "bitfile", "date", "date_fpga"]:
        raise Exception(f"Unknown stage: {stage}")
    main(stage)
