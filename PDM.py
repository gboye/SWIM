import re
import sys
import copy
import warnings
import pickle


def strFloat(num):
    return ("%0.2f"%num).rstrip("0").rstrip(".")


def formaterRegle(line):
    m=re.search("^(\S+)\s+-->\s+(\S+)\s+/\s+(\S+)\s+___\s+(\S+)\s+(.*)$",line)
    if m:
        a=m.group(1)
        if a=="[]":
            a=""
        b=m.group(2)
        if b=="[]":
            b=""
        c="".join(m.group(3).split(","))
        if c[0]=="X":
            c="^(.*"+c[1:]+")"
        if c[0]=="#":
            c="^("+c[1:]+")"
        d=m.group(4)
        if d[-1]=="X":
            d="("+d[:-1]+".*)$"
        if d[-1]=="#":
            d="("+d[:-1]+")$"
        reste=m.group(5)
        return (c+a+d,b,reste)
    else:
        print ("NOT A RULE")
        return


class RegleDist:
    '''
    Cette classe permet de stocker une règle de transformation et sa proportion
    '''
    def __init__(self,regle,dist,nom="",etiquette=False):
        self.regle=regle
        self.dist=dist
        self.nom=nom
        self.etiquette=etiquette
        
    def __repr__(self):
        if self.etiquette and self.nom!="":
            name=" "+self.nom
        else:
            name=""
        return '%d (%s%s)'%(self.regle,strFloat(self.dist),name)
    
    def __getitem__(self,index):
        if index==0:
            return self.regle
        elif index==1:
            return self.dist
        else:
            warnings.warn("%d index out of range [0,1]"%index)
            
    def __setitem__(self,index,value):
        if index==0:
            self.regle=value
        elif index==1:
            self.dist=value
        else:
            warnings.warn("%d index out of range [0,1]"%index)
    def val(self):
        return (self.regle,self.dist)        


class FormeClasse:
    '''
    Cette classe permet de stocker une classe distributionnelle de formes
    '''
    
    def __init__(self,nom="",etiquette=True):
        self.nom=str(nom)
        self.etiquette=etiquette
        self.reglesDist=[]
        self.regles=[]
        self.total=0
        
    def __repr__(self):
        temp=[]
        for element in self.numRulesDist():
            temp.append(str(element))
        if self.etiquette and self.nom!="":
            nomClasse=self.nom+" : "
        else:
            nomClasse=""
        return "%s[%s]"%(nomClasse,", ".join(temp))
            
    def __getitem__(self,index):
        return self.reglesDist[index]
          
    def addRule(self,regleDist):
        if not regleDist.regle in self.regles:
            self.reglesDist.append(regleDist)
            self.regles.append(regleDist.regle)
            self.total+=regleDist.dist
        else:
            warnings.warn("La règle %d est déjà dans la distribution"%regleDist.regle)

    def addRules(self,*reglesDist):
        for regleDist in reglesDist:
            self.addRule(regleDist)
        
    def numRulesDist(self):
        normalReglesDist=[]
        for dr in self.reglesDist:
            normalReglesDist.append(RegleDist(dr.regle,float(strFloat(dr.dist/self.total)),dr.nom,dr.etiquette))
        return normalReglesDist
    
    def getRules(self):
        listeNum=[]
        for element in self.regles:
            listeNum.append(str(element))
        return "-".join(sorted(listeNum,key=int))


class PaireClasses:
    '''
    Cette classe permet de stocker les classes distributionnelles d'une paire
     - distribution : un dict qui associe chaque règle à sa proportion dans la distribution
    '''
    
    def __init__(self,nom="Classes",etiquette=True):
        self.nom=nom
        self.etiquette=etiquette
        self.classes=[]
    
    def __repr__(self):
        temp=[]
        for element in self.classes:
            temp.append(str(element))
        classes=",".join(temp)
        if self.etiquette and self.nom!="":
            nomClasse=self.nom+" : "
        else:
            nomClasse=""
        return "%s[%s]"%(nomClasse,classes)

    def name(self):
        return self.nom
    
    def label(self,etiquette):
        self.etiquette=etiquette

    def addFormeClasse(self,FormeClasse):
        self.classes.append(FormeClasse)
    
    def addFormesClasses(self,*FormesClasses):
        for FormeClasse in FormesClasses:
            self.addFormeClasse(FormeClasse)
    
    def content(self,original=False):
        return self.classes


class Classes:
    '''
    Cette classe permet de stocker pour chaque paire, ses classes de distribution
    '''
    
    def __init__(self):
        self.classes={}
    
    def __repr__(self):
        tempPaire=[]
        for paire in self.classes:
            tempPaire.append(str(paire))
            tempClasses=[]
            for classe in self.classes[paire]:
                tempClasses.append(str(classe))
            tempPaire.append("\n".join(tempClasses)+"\n")
        return "\n".join(tempPaire)
    
    def addPaireClasses(self,paire,paireClasses):
        if not paire in self.classes:
            self.classes[paire]=paireClasses.classes
        else:
            warnings.warn("Classes déja définies pour %s"%paire)


class Paire:
    '''
    Cette classe permet de définir une paire (entree,sortie)
    '''
    def __init__(self,entree,sortie):
        self.entree=entree
        self.sortie=sortie

    def __hash__(self):
        return hash(self.entree+self.sortie)
    
    def __eq__(self,other):
        return self.entree==other.entree and self.sortie==other.sortie

    def __repr__(self):
        return ('%s=>%s'%(self.entree,self.sortie))
    
    def __getitem__(self,index):
        if index==0:
            return self.entree
        elif index==1:
            return self.sortie
        else:
            warnings.warn("%d index out of range [0,1]"%index)
            
    def __setitem__(self,index,value):
        if index==0:
            self.entree=value
        elif index==1:
            self.sortie=value
        else:
            warnings.warn("%d index out of range [0,1]"%index)
            
    def val(self):
        return (self.entree,self.sortie)        


class ModifForme:
    '''
    Cette classe permet de stocker une règle de transformation (patron,mod,regleSPE)
    '''
    def __init__(self,inPatron,mod,regleSPE=""):
        self.patron=inPatron
        self.mod=mod
        self.regleSPE=regleSPE
    
    def __eq__(self,other):
        return self.patron==other.patron and self.mod==other.mod
    
    def __repr__(self):
        if self.regleSPE=="":
            return "(%s>%s)" % (self.patron, self.mod)
        else:
            return self.regleSPE

    def __getitem__(self,index):
        if index==0:
            return self.patron
        elif index==1:
            return self.mod
        else:
            warnings.warn("%d index out of range [0,1]"%index)
            
    def __setitem__(self,index,value):
        if index==0:
            self.patron=value
        elif index==1:
            self.mod=value
        else:
            warnings.warn("%d index out of range [0,1]"%index)
            
    def p(self):
        return self.patron        
    def m(self):
        return self.mod     
    def val(self):
        return (self.patron,self.mod)        
    


class Regles:
    '''
    Cette classe permet de stocker les règles de PredSPE dans les variables regles et reglesPaire
     - regles contient toutes les transformations
     - reglesPaire contient les numéros des transformations utiles pour une paire (entree,sortie)
    '''
    def __init__(self):
        self.regles=[]
        self.reglesPaire={}

    def __repr__(self):
        tempRegles=[]
        for i in range(len(self.regles)):
            tempRegles.append(str(i)+" "+str(self.regles[i]))
        tempReglesPaire=[]
        for paire in self.reglesPaire:
            tempPaire=[]
            for element in self.reglesPaire[paire]:
                tempPaire.append(str(element))
            tempReglesPaire.append(str(paire)+" : "+", ".join(tempPaire))
        return "\n".join(tempRegles)+"\n\n"+"\n".join(tempReglesPaire)
            
    def addRegle(self,paire,ligne):
        (inPatron,mod,reste)=formaterRegle(ligne)
        regleSPE=""
        if ligne.endswith(reste):
            regleSPE=ligne[:-len(reste)]
        regle=ModifForme(inPatron,mod,regleSPE)
        if not regle in self.regles:
            self.regles.append(regle)
        if not paire in self.reglesPaire:
            self.reglesPaire[paire]=[]
        if not self.regles.index(regle) in self.reglesPaire[paire]:
            self.reglesPaire[paire].append(self.regles.index(regle))
            
    def getRegleSPE(self,num):
        return self.regles[num].regleSPE

    def getNumRegle(self,patron,mod):
        return self.regles.index(ModifForme(patron,mod))
    


