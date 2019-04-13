import re
import sys
f = sys.argv[0].replace('/vlog_tb_gen.py','')
sys.path.append(f)

from pprint import pprint

from vlib import *
test_file = 'iopad.v'


class WriteTestBench(SourceFileProcess):
    def __init__(self,inText):
        super().__init__(inText)

        self.param_name_max_len = 0
        self.param_value_max_len = 0
        self.port_name_max_len = 0
        self.port_width_max_len = 0

        self.inText_decode()
        self.find_max()

        self.write_tb()



    def write_tb(self):
        '''Write data to TestBench'''

        # Write Header
        tb = '\n'
        tb += "`timescale 1ns/1ns\n"

        tb += 'module ' + self.moduleName + '_tb();\n\n'

        tb += 'parameter Period = 20;\n'

        # Write Parameter
        for p in self.param_list:
            tb += 'parameter ' + p.pName + ' = ' + p.pValue + ';\n'
        tb += '\n'

        # Write Reg Declare
        for p in self.port_list:
            if p.pDir == 'input':
                tb += 'reg     ' + p.pWidth + '    '+p.pName + '= 0;\n'
            elif p.pDir=='output' or p.pDir=='inout':
                tb += 'reg     ' + p.pWidth + '    '+p.pName + '   ;\n'
            elif (p.pDir==''):
                tb += p.ifdef + p.defvalue + p.endif + '\n'

        # Write Instance
        tb +='\n\n'+self.moduleName

        if len(self.param_list) != 0:
            tb += ' #('
            for i in self.param_list:
                tb += '.' + i.pName.strip() + '(' + i.pName.strip() + '), '
            tb = tb[0:-2] + ')'
        tb +='  u_' + self.moduleName +  '(\n'
        for p in self.port_list:
            if p.pDir == '':
                tb += p.ifdef + p.defvalue + p.endif + '\n'
            else:
                tb += '    .'+p.pName + '    ('+p.pName+'    ),\n'
        tb = tb[0:-2] + ');\n\n'

        # Generate clock
        for p in self.port_list:
            m = re.search('clk',p.pName)
            if m:
                tb += 'initial begin\n'
                tb += '    clk = 0;\n    forever #Period clk = ~clk;\n'
                tb += 'end\n'
        tb += '\n\ninitial begin\n'
        tb += '    #1000; $finish;\n'
        tb += 'end\n\n'

        tb += 'initial begin\n'
        tb += "`ifdef DUMP_FSDB\n"
        tb += '   $fsdbDumpfile("wave.fsdb");\n'
        tb += "   $fsdbDumpvars();\n"
        tb += "`elsif DUMP_SHM\n"
        tb += '   $shm_open("wave.shm);\n'
        tb += '   $shm_probe(' + self.moduleName + '_tb,"AS");\n'
        tb += "`elsif DUMP_VCD\n"
        tb += '   $dumpfile("wave.vcd");\n'
        tb += "   $dumpvars()\n"
        tb += '`else\n'
        tb += '    $display("No dump andy waves")\n'
        tb += "`endif\n"
        tb += "end\n\n"

        tb += '`include "testcase.v"\n\n'

        tb += 'endmodule\n'

        fout = open(self.moduleName + '_tb.v', 'wt')
        fout.write(tb)
        fout.close()

if __name__ == '__main__':
    flen = len(sys.argv)
    if flen > 1:
        for i in range(1,flen):
            app = WriteTestBench(sys.argv[1])
            app.inText_decode()
    else:
        app = WriteTestBench(test_file)





