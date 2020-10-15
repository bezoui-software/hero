digits = "0123456789"
alpha = "azertyuiopqsdfghjklmwxcvbn"
math_syntaxs = "+-()*^/"
syntaxs = {
  "print": "PRINT",
 ";": "ENDLINE",
   "'": "Q_MARK",
  "input": "INPUT",
  "str": "CONVERT_STRING",
  "int": "CONVERT_INT",
  "f,": "AND",
  "=": "EQUAL",
  "$": "VAR",
  "float": "CONVERT_FLOAT",
  "expr": "CONVERT_EXPR",
  "(": "START_PARENTHESE",
  ")": "END_PARENTHESE"
}

class Hero:
    def __init__(self, filedata):
         self.filedata = filedata
         self.vars = {}
         self.errors = []
         self.run()
          
    def run(self):
         self.lex()
         #print (self.tokens)
         self.parse()
         #print (self.tokens)
         self.printError()
        
    def lex(self):
         tokens = []
         tok = ""
         str_state = False
         int_state = False
         float_state = False
         expr_state = False
         var_state = False
         for char in self.filedata:
             tok += char
             if (tok == " " or tok == "\n") and str_state == False:
                 tok = ""
             if tok in syntaxs or char in syntaxs:
                 if syntaxs.get(char)=="Q_MARK":
                     if str_state == True:
                         str_state = False               
                          #Remove ' from tok
                         tok = tok[:-1]
                         tok = "STRING:" + tok
                         tokens.append(tok)
                         tok = ""
                     else:
                         str_state = True
                         tok = ""
                 #Detect var
                 elif syntaxs.get(char)=="VAR":
                     if var_state == False:
                         var_state = True
                         int_state = False
                         float_state = False
                 #Detect equal
                 elif syntaxs.get(char)=="EQUAL":
                     tok = tok.replace("=","")
                     #Add var
                     if var_state:
                         var_state = False
                         tok = tok.replace("$","VAR:")
                         tok = tok.replace(" ","")
                         tokens.append(tok)
                         tok = ""
                     tokens.append(syntaxs.get(char))
                 elif syntaxs.get(char)=="ENDLINE" or syntaxs.get(char)=="AND" or syntaxs.get(char)== "END_PARENTHESE":
                     tok = tok.replace(";","") 
                     tok = tok.replace(",","")
                     tok = tok.replace(")","")
                     #Add int
                     if int_state:
                         int_state = False
                         tok = "INT:"+tok
                         tokens.append(tok)
                         tok = ""
                     #Add float
                     if float_state:
                         float_state = False
                         tok = "FLOAT:"+tok
                         tokens.append(tok)
                         tok = ""
                     #Add expr
                     if expr_state:
                         expr_state = False
                         tok = "EXPR:"+tok
                         tokens.append(tok)
                     #Add var
                     if var_state:
                         var_state = False
                         tok = tok.replace("$","VAR:")
                         tok = tok.replace(" ","")
                         tokens.append(tok)
                         tok = ""
                     else:
                         tok = ""
                     tokens.append(syntaxs.get(char))
                 else:
                     tokens.append(syntaxs.get(tok))
                     tok = ""
             if char in digits:
                 if int_state==False and float_state==False and expr_state==False and str_state == False and var_state==False:
                     int_state = True
             #Detect float
             if char==".":
                 if int_state:
                     int_state = False
                     float_state = True
             #Detect expr
             if char in math_syntaxs:
                 if int_state or float_state:
                     int_state = False
                     float_state = False
                     expr_state = True
         self.tokens = tokens
        
    def parse(self): 
         tokens = self.tokens
         state = {"PRINT":False,"INPUT":False,"VAR":False,"CONVERT":False}
         for i in range(len(tokens)):
             if tokens[i]=="PRINT":
                 state["PRINT"] = True
             elif tokens[i]=="INPUT":
             	state["INPUT"] = True
             elif tokens[i].split("_")[0]=="CONVERT":
                 state["CONVERT"] = True
             elif tokens[i]=="ENDLINE":
                 state["PRINT"] = False
                 state["INPUT"] = False
                 state["VAR"] = False
                 state["CONVERT"] = False
             elif tokens[i] == "END_PARENTHESE":
                  state["CONVERT"] = False
                  state["VAR"] = False
             elif self.checkType(tokens[i],"VAR"):
                  tok = tokens[i].split(":")
                  tokType = tok[0]
                  if len(tok)>2:
                      tokText = tok.pop(0)
                      tokText = "".join(tokText)
                  else:
                       tokText = tok[1]
                       state["VAR"] = True
             if state["CONVERT"]:
                 to_type = tokens[i].replace("CONVERT_","")
                 self.convertNode(tokens[i+2], to_type)
                 state["CONVERT"] = False
             if state["PRINT"]:
                 if tokens[i+1] == "AND":
                     self.printNode(tokens[i], "")
                 else:
                     self.printNode(tokens[i])
             elif state["INPUT"]:
             	if self.checkType(tokens[i+1], "STRING"):
             	    if self.checkType(tokens[i+2], "VAR"): 
             	        self.inputNode(tokens[i+1], tokens[i+2])
             	    else:
             	        self.inputNode(tokens[i+1],None)
             elif state["VAR"]:
                 if i+1 < len(tokens) and tokens[i+1] == "EQUAL":
                     self.varNode(tokText,tokens[i+2])
                    
    def printNode(self,tok,end="\n"):
        if tok != None:
             if ":" in tok and len(tok)>2:
                 tok = tok.split(":")
                 tokType = tok[0]
                 tokText = tok[1]
                 if tokType == "EXPR":
                     print (eval(tokText),end=end)
                 elif tokType == "VAR":
                     tokText = self.varNode(tokText,action="get")
                     self.printNode(tokText, end=end)
                 else:
                     print (tokText,end=end)
        else:
             error="There is an error in your print !"
             self.errors.append(error)
             
    def inputNode(self, string, var):
        if self.checkType(string, "STRING"):
            string = self.getData(string)
            string = string[1]
            if var == None:
                input (string)
            else:
                var = self.getData(var)
                varName = var[1]
                value = input (string)
                value = self.make(value, "STRING")
                self.vars[varName] = value
                
    def convertNode(self, data, to_type):
        temp = data
        data = self.getData(data)
        data_type = data[0]
        data_value = data[1]
        #print (data)
        if data_type == "VAR":
            var_name = data_value
            var = self.varNode(var_name, action="get")
            var = self.getData(var)
            var_type = var[0]
            var_value = var[1]
            if (to_type == "STRING"):
                var_value = self.make(var_value, to_type)
                self.vars[var_name] = var_value
            else:
                if alpha in var_value:
                    error = "You can't convert a string variable to a number <"+var_name+">"
                    self.errors.append(error)
                    return ''
                else:
                    var_value = self.make(var_value, to_type)
                    self.vars[var_name] = var_value  
        else:
            if to_type=="STRING":
                data_value = self.make(data_value, to_type)
                self.tokens[self.tokens.index(temp)] = data_value
            elif alpha in data_type:
                error = "You can't convert a string to a number <"+data_value+">"
                self.errors.append(error)
            else:
                data_value = self.make(data_value, to_type)
                self.tokens[self.tokens.index(temp)] = data_value

    def varNode( self,varName, varValue="", action="set"):
        #print (varName, varValue, action)
        varValue = varValue.replace("$", "VAR:")
        varValue = varValue.replace("CONVERT_INT","")
        varValue = varValue.replace("CONVERT_FLOAT","")
        varValue = varValue.replace("CONVERT_EXPR","")
        if action=="set":
            varValue = varValue.replace("CONVERT_INT","")
            #print (varValue,self.containType(varValue, "VAR"))
            if self.containType(varValue, "VAR"):
                    var = varValue
                    temp = varValue
                    #print (varValue,self.containSyntaxs(temp, math_syntaxs))
                    if self.containSyntaxs(temp, math_syntaxs):
                        temp = self.remove(temp, math_syntaxs)
                        temp = temp.split(" ")
                        temp = " ".join(temp).split() 
                        #print (temp)
                        for item in temp:
                            value = None
                            #print (item)
                            if self.checkType(item, "VAR"):
                                tempVarName = self.getData(item)[1]
                                if tempVarName in self.vars:
                                    value = self.varNode(tempVarName, action="get")
                                    #print (value)
                                    if self.checkType(value, "STRING"):
                                        error = "YOU CAN'T ASSIGN A STRING AS A NUMBER <"+value+">"
                                        self.errors.append(error)
                                        return '';
                                    else:
                                        var = var.replace(item, self.getData(value)[1])
                                else:
                                    error = "There is no variable called <"+tempVarName+">"
                                    self.errors.append(error)
                                    break
                        var = var.replace("INT:","")
                        var = var.replace("FLOAT:","") 
                        var = var.replace("EXPR:","")
                        
                        if 'STRING:' in var:
            	            error =  "You can't use String as a Number in <"+var+">"
            	            self.errors.append(error)
                        else:
                            finalValue = eval(var)
                            #print (">",var, finalValue)
                            finalValue = self.make(finalValue, "INT")
                            self.vars[varName] = str(finalValue)
                    else:
                        var = varValue.split(":")
                        if len(var) == 2:
                            type = var[0]
                            varValue = var[1]
                            if type == "VAR":
                                value = self.varNode(varValue,action="get")
                                self.vars[varName]=value
                            elif type in syntaxs.values():
                                self.vars[varName]=value
                            else:
                        	    error = "Invalide variable value <",varValue,"> !"
                        	    self.errors.append(error)
                        elif len(var) > 2:
                            tempVar = self.remove(varValue, math_syntaxs)
                            tempVarList = list(tempVar)
                            for i in range(len(tempVarList)):
                                if (tempVarList[i] in digits) and (tempVarList[i-1] not in alpha):
                                    tempVarList.pop(i)
                            
                        		
                            tempVar = "".join(tempVarList)
                            tempVar = tempVar.split(" ")
                            value = None
                            for i in range(len(tempVar)):
                                if tempVar[i] != "":
                                    value = self.varNode(tempVar[i], action="get")
                                    if self.checkType(value,"STRING"):
                                	    error = "You can't use STRING as NUMBER !"
                                	    self.errors.append(error)
                                	    break
                                    else:
                                        value = self.getData(value)[1]
                                        varValue =varValue.replace(tempVar[i], value)
                            if value != None:
                                varValue = self.make(varValue, "EXPR")
                                self.vars[varName]=varValue
                   
            else:
                self.vars[varName] = varValue
                #print (self.vars)    
        elif action == "get":
            #print (self.vars)
            #print (">>",varName)
            varName = varName.replace("$", "VAR:")
            if self.checkType(varName,"VAR"):
            	varName = varName.replace("VAR:","")
            if varName in self.vars:
                #print (self.vars.get(varName))
                if self.checkType(self.vars.get(varName),"VAR"):
                    varName = self.vars.get(varName)
                    varName = varName.split(":")
                    varName = varName[1]                  
                    #print (self.varNode(varName, action="get"))
                    return self.varNode(varName,action="get")
                else:
                    return self.vars.get(varName)
            else:
                error = "The var <"+varName+"> doesn't exist"
                self.errors.append(error)
                            
    def checkType(self, tok, type):
      tok = str(tok)
      if tok != " " and tok != None:
        if ":" in list(tok):
             tok = tok.split(":")
             tokType = tok[0]
             if tokType == type:
                 return True
             else:
                 return False
        else:
            return False
      else:
        return False
        
    def VAREXPR(self, varName, varvalue):
        tempVar = self.remove(varValue, math_syntaxs)
        tempVarList = list(tempVar)
        for i in range(len(tempVarList)):
            if (tempVarList[i] in digits) and (tempVarList[i-1] not in alpha):
                tempVarList.pop(i)
        tempVar = "".join(tempVarList)
        tempVar = tempVar.split(" ")
        value = None
        for i in range(len(tempVar)):
            if tempVar[i] != "":
                value = self.varNode(tempVar[i], action="get")
                if self.checkType(value,"STRING"):
                    error = "You can't use STRING as NUMBER !"
                    self.errors.append(error)
                    break
                else:
                    value = self.getData(value)[1]
                    varValue =varValue.replace(tempVar[i], value)
        if value != None:
            varValue = self.make(varValue, "EXPR")
            self.vars[varName]=varValue
            
    def containType(self, tok, target):
        if self.containSyntaxs(tok, math_syntaxs):
            tok = self.remove(tok, math_syntaxs)
            tok = tok.split(" ")
            for item in tok:
                if (self.containType(item, target)):
            	    return True
            	
            return False
        else:
            tok=tok.split(":")
        for i in range(len(tok)):
            if tok[i] == target:
                return True
        return False
    def containSyntaxs(self, tok, arr):
        for item in arr:
    	    if item in tok:
    	        return True
        return False
    
    def getData(self, tok):
        if ":" in str(tok):
            tok = tok.split(":")
        return tok
        
    def make(self,tok,type):
        tok = str(tok)
        return type+":"+tok
    def remove(self, tok, syntaxs_arr):
        for i in range(len(syntaxs_arr)):
            tok = tok.replace(syntaxs_arr[i], " ")
        return tok
    def printError(self):
        errors = self.errors
        errorSize = len(errors)
        if errorSize > 0:
            print ("\n ERRORS : \n")
            for i in errors:
                print (i)
txt = """
input 'Birthyear > ' $year;
input 'Tape a math expression > ' $expr;
int($year);
expr($expr);
print 'Result of expression ',$expr;
$age = 2020-$year;
print 'You have ',$age,' years old';
input 'Tape your first name > ' $fname;
input 'Tape your last name > ' $lname;
print '---------------------------';
print 'Your full name is ',$fname,' ',$lname,' and you have ',$age,' years old !';
"""
engine = Hero(txt)
engine
