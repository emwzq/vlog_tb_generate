
import re
import sys
import chardet

def inText_read(input_file):
    with open(input_file, 'rb') as f:
        f_info = chardet.detect(f.read())
        f_encoding = f_info['encoding']
        #print (f_info)
    with open(input_file, encoding=f_encoding) as inFile:
        inText = inFile.read()

    return inText
def delComment( Text ):
    """ removed comment """
    single_line_comment = re.compile(r"//(.*)$", re.MULTILINE)
    multi_line_comment  = re.compile(r"/\*(.*?)\*/",re.DOTALL)
    Text = multi_line_comment.sub('\n',Text)
    Text = single_line_comment.sub('\n',Text)
    return Text

def delBlock( Text ) :
    """ removed task and function block """
    Text = re.sub(r'\Wtask\W[\W\w]*?\Wendtask\W','\n',Text)
    Text = re.sub(r'\Wfunction\W[\W\w]*?\Wendfunction\W','\n',Text)
    return Text

def delSpace( Text) :
    ''' removed space '''
    Text = re.sub(r'\b', ' ', Text)
    Text = re.sub(r'\n', ' ', Text)
    Text = Text.strip()
    Text = re.sub(r'\s\s+',' ',Text)

    return Text

def inText2List( Text ):
    inText = inText_read(Text)
    inText = delComment(inText)
    inText = delBlock(inText)
    inText = delSpace(inText)
    #print(inText, end='')
    #print()
    inText_list = re.split(' ', inText)
    #print(inText)
    return inText_list

class   Parameter():
    def __init__(self,pName,pValue):
        self.pName = pName
        self.pValue = pValue
        self.pName_len = len(pName)
        self.pValue_len = len(pValue)
    def len_trim(self,name_max_len,value_max_len):
        self.pName += ' '*(name_max_len - self.pName_len)
        self.pValue += ' ' * (value_max_len - self.pValue_len)

class   Port():
    def __init__(self,pName='',pDir='',pWidth_start='',pWidth_end='',pType='wire',ifdef='',endif='',defvalue=''):
        self.pName = pName
        self.pDir = pDir
        self.pWidth_start = pWidth_start
        self.pWidth_end = pWidth_end
        if pWidth_start != '':
            self.pWidth = '['+ pWidth_start + ':' + pWidth_end + ']'
        else:
            self.pWidth = ''
        self.pType = pType

        self.ifdef = ifdef
        self.endif = endif
        self.defvalue = defvalue

        self.pName_len = len(self.pName)
        self.pWidth_len = len(self.pWidth)
        print ('pName=%s,pDir=%s,pWidth_start=%s,pWidth_end=%s,pType=%s,ifdef=%s'%(pName,pDir,pWidth_start,pWidth_end,pType,ifdef))

    def len_trim(self,name_max_len,width_max_len):
        self.pName += ' '*(name_max_len - self.pName_len)
        self.pWidth += ' ' * (name_max_len - self.pWidth_len)

class SourceFileProcess():
    def __init__(self,inText):
        self.moduleName = ''
        self.word_list = inText2List( inText )
        self.param_list = []
        self.port_list = []
        self.param_field_start = 0

        self.pDir = ''
        self.pType = ''
        self.pWidth_start = ''
        self.pWidth_end = ''
        self.pName = ''

        self.ifdef = ''
        self.endif = ''
        self.defvalue = ''

        self.get_port_done = 0

        #pprint (self.word_list)

    def inText_decode(self):
        while len(self.word_list):
            word = self.word_list.pop(0)
            if word == 'module':
                self.moduleName = self.word_list.pop(0)
                print ('moduleName = ',self.moduleName)
                self.param_field_start = 1

            if self.param_field_start and (word=='#('):
                print ('Find Parameter field')
                self.param_field_start = 0
                self.get_parameter()

            elif (word == '(') and (self.get_port_done==0):
                print ('getting port...')
                self.get_port()

    def get_port(self):
        while self.get_port_done == 0:
            word = self.word_list.pop(0)
            print ('>>>',word)
            if (word == ')') or (word == ');'):
                self.get_port_done = 1
                print('debug - 1')
            if (word=='input') or (word=='output') or (word=='inout'):
                self.pDir = word
                print('debug - 2')
            elif (word=='wire') or (word=='reg') or (word=='tri') or (word=='logic'):
                self.pType = word
                print('debug - 3')
            elif (word=='['):
                self.pWidth_start,self.pWidth_end = self.get_width()
                print('debug - 4')
            elif ((word==');') or (word==')') or (word==',')) and (self.pName!='') and (self.pDir!=''):
                self.port_list.append( Port(pName       =self.pName,
                                            pDir        =self.pDir,
                                            pWidth_start=self.pWidth_start,
                                            pWidth_end  =self.pWidth_end,
                                            pType       =self.pType))
                self.pName = ''
                self.pWidth_start = ''
                self.pWidth_end = ''
                print('debug - 5')
            elif (word=='`'):
                word = self.word_list.pop(0)
                print (word)
                self.ifdef = ''
                self.defvalue = ''
                self.endif = ''
                if word == 'ifdef':
                    self.ifdef = '`ifdef '
                    self.defvalue = self.word_list.pop(0)
                elif word == 'endif':
                    self.endif = '`endif'
                print (self.ifdef,self.endif,self.defvalue)

                self.port_list.append( Port(pName       ='',
                                            pDir        ='',
                                            pWidth_start='',
                                            pWidth_end  ='',
                                            pType       ='',
                                            ifdef       =self.ifdef,
                                            endif       =self.endif,
                                            defvalue    =self.defvalue))
            else:
                self.pName = word
                print('debug - 6')
            print('debug - out')

    def get_width(self):
        pWidth_start = ''
        pWidth_end = ''
        while True:
            d = self.word_list.pop(0)
            if d != ':':
                pWidth_start += d
            else:
                break
        while True:
            d = self.word_list.pop(0)
            if d != ']':
                pWidth_end += d
            else:
                break
        return (pWidth_start,pWidth_end)

    def get_parameter(self):
        param_word_find = 0
        while True:
            word = self.word_list.pop(0)
            #print (word)
            if word == 'parameter':
                param_word_find = 1
            if param_word_find:
                if word == ')':
                    break
                else:
                    if self.word_list[1] == '=':
                        pName = self.word_list.pop(0)
                        self.word_list.pop(0)
                        pValue = self.word_list.pop(0)
                        self.param_list.append(Parameter(pName, pValue))
    def find_max(self):
        for i in self.param_list:
            if self.param_name_max_len < i.pName_len:
                self.param_name_max_len = i.pName_len
            if self.param_value_max_len < i.pValue_len:
                self.param_value_max_len = i.pValue_len
        for i in self.port_list:
            if  self.port_name_max_len < i.pName_len:
                self.port_name_max_len = i.pName_len
            if  self.port_width_max_len < i.pWidth_len:
                self.port_width_max_len = i.pWidth_len
        d = self.param_name_max_len % 4
        self.param_name_max_len += 4-d
        d = self.param_value_max_len % 4
        self.param_value_max_len += 4-d
        d = self.port_name_max_len % 4
        self.port_name_max_len += 4-d
        d = self.port_width_max_len % 4
        self.port_width_max_len += 4-d
        for i in self.param_list:
            i.len_trim(self.param_name_max_len,self.param_value_max_len)
        for i in self.port_list:
            i.len_trim(self.port_name_max_len,self.port_width_max_len)