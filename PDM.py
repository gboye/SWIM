import re
import warnings

seuilDistribution=0.01

def strFloat(num):
    return ("%0.2f"%num).rstrip("0").rstrip(".")


def parserPaire(line):
    m=re.search("^\s*(\S+)\s+==>\s+(\S+)\s*$",line)
    if m:
        inCase=m.group(1)
        outCase=m.group(2)
        return (inCase,outCase)
    else:
        return False


def parserRegle(line):
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
    def __init__(self,regle,dist,sortie="",nom="",etiquette=False):
        self.regle=regle
        self.dist=dist
        self.sortie=sortie
        self.nom=nom
        self.etiquette=etiquette
        
    def __repr__(self):
        if self.etiquette and self.nom!="":
            name=" "+self.nom
        else:
            name=""
        if self.sortie!="":
            name=" "+self.sortie+name
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
        self.reglesDist={}
#        self.regles=[]
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

    def __eq__(self,other):
        return self.getRules()==other.getRules()

            
    def __getitem__(self,index):
        if index in self.reglesDist:
            return self.reglesDist[index]
        else:
            raise KeyError("pas de %s" % index)
          
    def addRule(self,regleDist):
        if not regleDist.regle in self.reglesDist:
            self.reglesDist[regleDist.regle]=regleDist
#            self.regles.append(regleDist.regle)
#            self.total+=regleDist.dist
        else:
            warnings.warn("La règle %d est déjà dans la distribution"%regleDist.regle)

    def addRules(self,*reglesDist):
        for regleDist in reglesDist:
            self.addRule(regleDist)
    
    def updateTotal(self):
        self.total=0
        for regle in self.reglesDist:
            self.total+=self.reglesDist[regle].dist
        
    def numRulesDist(self):
        self.updateTotal()
        normalReglesDist=[]
        for regle in self.reglesDist:
            dr=self.reglesDist[regle]
            normalReglesDist.append(RegleDist(dr.regle,float(strFloat(dr.dist/self.total)),dr.sortie,dr.nom,dr.etiquette))
        return normalReglesDist
    
    def getRules(self):
        listeNum=[]
        for element in self.reglesDist:
            listeNum.append(str(element))
        return "-".join(sorted(listeNum,key=int))


class PaireClasses:
    '''
    Cette classe permet de stocker les classes distributionnelles d'une paire
     - classes : une liste de FormeClasse
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
        self.pairesCase={}

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
        (inPatron,mod,reste)=parserRegle(ligne)
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
        if not paire.sortie in self.pairesCase:
            self.pairesCase[paire.sortie]=[]
        if not paire.entree in self.pairesCase[paire.sortie]:
            self.pairesCase[paire.sortie].append(paire.entree)

    def getRegleSPE(self,num):
        return self.regles[num].regleSPE

    def getNumRegle(self,patron,mod):
        return self.regles.index(ModifForme(patron,mod))
    
def distributionVecteurs(vecteurs):
    formes={}
    total=0
    for vecteur in vecteurs:
        for fc in vecteur:
            forme=fc.forme
            coef=fc.coef
            if not forme in formes:
                formes[forme]=0
            formes[forme]+=coef
            total+=coef
    distribution=[]
    supprime=False
    for forme in formes:
        coef=float(strFloat(formes[forme]/total))
        if coef>seuilDistribution:
            distribution.append(FormeCoef(forme,coef))
        else:
            supprime=True
    if supprime==True:
        distribution=distributionVecteurs([distribution])
    return sorted(distribution,key=lambda couple: couple[1],reverse=True)
    
def transformerForme(inPatron,mod,forme):
    extrait=re.search(inPatron,forme)
    if extrait:
        sortie=extrait.group(1)+mod+extrait.group(2)
        return sortie
    else:
        return False

def outputFormes(paireCase,FormeCoef):
    lines=[]
    numsClasse={}
    (forme,part)=FormeCoef
    for numero in pairesCasesRegles[paireCase]:
        (inPatron,mod)=reglesPDM[numero]
        sortie=transformerForme(inPatron,mod,forme)
        if sortie:
            numsClasse[numero]=sortie
    alphaKeys=[]
    for num in sorted(numsClasse.keys()):
        alphaKeys.append(str(num))
    classe="-".join(alphaKeys)
    if not classe in Classes[paireCase]:
        print ("FORME SANS SORTIE",forme)
    else:
        for numero in numsClasse:
            if Classes[paireCase][classe][numero]>0:
                lines.append((numsClasse[numero],Classes[paireCase][classe][numero]*part))
    return distributionVecteurs([lines]) 

class FormeCoef:
    '''
    Cet classe contient deux variables : forme et coef
    '''
    def __init__(self,forme,coef):
        self.forme=forme
        self.coef=coef
        
    def __repr__(self):
        return ('("%s",%s)'%(self.forme,strFloat(self.coef)))
    
    def __getitem__(self,index):
        if index==0:
            return self.forme
        elif index==1:
            return self.coef
        else:
            raise ValueError("out of range [0,1]")
            
    def __setitem__(self,index,value):
        if index==0:
            self.forme=value
        elif index==1:
            self.coef=value
        else:
            raise ValueError("out of range [0,1]")
            
    def val(self):
        return (self.forme,self.coef)

class FormeSorties:
    '''
    Cet classe contient deux variables : forme et sorties
    '''
    def __init__(self,forme):
        '''
        FormeSorties
        '''
        self.forme=forme
        self.sorties={}
        
    def __repr__(self):
        '''
        FormeSorties
        '''
        result=self.forme+" : "
        for element in self.sorties:
            result+=str(element)+"=>"+self.sorties[element]
        return result

    def __eq__(self,other):
        '''
        FormeSorties
        '''
        result=(self.forme==other.forme)
        if result:
            for sortie in self.sorties:
                result=result and (self.sorties[sortie]==other.sorties[sortie])
        return result
                
    def __setitem__(self,index,value):
        '''
        FormeSorties
        '''
        self.sorties[index]=value
            
    def val(self):
        '''
        FormeSorties
        '''
        return (self.forme,self.sorties)
        
class FormeEntrees:
    '''
    Cet classe contient deux variables : forme et sorties
    '''
    def __init__(self,forme):
        '''
        FormeEntrees
        '''
        self.forme=forme
        self.entrees={}
        
    def __repr__(self):
        '''
        FormeEntrees
        '''
        result=self.forme+" : "
        for element in self.entrees:
            result+=str(element)+"=>"+self.entrees[element]
        return result

    def __eq__(self,other):
        '''
        FormeEntrees
        '''
        result=(self.forme==other.forme)
        if result:
            for entree in self.entrees:
                result=result and (self.entrees[entree]==other.entrees[entree])
        return result
                
    def __setitem__(self,index,value):
        '''
        FormeEntrees
        '''
        self.entrees[index]=value
            
    def val(self):
        '''
        FormeEntrees
        '''
        return (self.forme,self.entrees)


class Case:
    '''
    Cette classe contient 4 variables :
     - valeurs : une liste de FormeCoef
     - coefficient : un dict qui associe chaque forme à son coefficient
     - normalValeurs : une liste de FormeCoef avec des coefficients normés (somme=1)
     - normalCoefficient : un dict qui associe chaque forme à son coefficient normé (somme=1)
    '''
    
    def __init__(self,nom="",etiquette=False):
        self.nom=nom
        self.etiquette=etiquette
        self.valeurs=[]
        self.coefficient={}
        self.normalValeurs=[]
        self.normalCoefficient={}
    
    def __str__(self):
        temp=[]
        for fc in distributionVecteurs([self.valeurs]):
            temp.append(repr(fc))
        contenuCase=",".join(temp)
        if self.nom!="":
            nomCase=self.nom+" : "
        else:
            nomCase=""
        return "%s[%s]"%(nomCase,contenuCase)

    
    def __repr__(self):
        temp=[]
        for fc in distributionVecteurs([self.valeurs]):
            temp.append(repr(fc))
        contenuCase=",".join(temp)
        if self.etiquette and self.nom!="":
            nomCase=self.nom+" : "
        else:
            nomCase=""
        return "%s[%s]"%(nomCase,contenuCase)

    def __getitem__(self,index):
        return self.valeurs[index]
        

    def label(self,etiquette):
        self.etiquette=etiquette

    def addForm(self,FormeCoef):
        self.valeurs.append(FormeCoef)
        if not FormeCoef.forme in self.coefficient:
            self.coefficient[FormeCoef.forme]=0
        self.coefficient[FormeCoef.forme]+=FormeCoef.coef
    
    def addForms(self,FormesCoefs):
        for FormeCoef in FormesCoefs:
            self.addForm(self,FormeCoef)
    
    def content(self,original=False):
        if original:
            return self.valeurs
        else:
            self.normalValeurs=distributionVecteurs([self.valeurs])
            return self.normalValeurs
        
    def coef(self,forme,original=False):
        if forme in self.coefficient:
            if original:
                return self.coefficient[forme]
            else:
                self.normalValeurs=distributionVecteurs([self.valeurs])
                for fc in self.normalValeurs:
                    self.normalCoefficient[fc.forme]=fc.coef
                return self.normalCoefficient[forme]
        else:
            return 0
        
    def coefs(self,original=False):
        if original:
            return self.coefficient
        else:
            self.normalValeurs=distributionVecteurs([self.valeurs])
            for fc in self.normalValeurs:
                self.normalCoefficient[fc.forme]=fc.coef
            return self.normalCoefficient


class Paradigme:
    '''
    Cet objet contient deux tableaux associatifs entrees et sorties qui contiennent des objets Case
    le tableau supporter est prévu pour noter la contribution des entrées aux sorties
    les cases du paradigme sont fixées par défaut à la création (mutable=False)
    '''
    def __init__(self,Cases=[],mutable=False):
        self.entrees={}
        self.sorties={}
        self.supporters={}
        self.mutable=mutable
        for case in Cases:
            self.entrees[case]=Case(case)
            self.sorties[case]=Case(case)

    def __repr__(self):
        entreesTemp=[]
        for case in self.entrees:
            entreesTemp.append(case+" : "+repr(self.entrees[case]))
        sortiesTemp=[]
        for case in self.sorties:
            sortiesTemp.append(case+" : "+repr(self.sorties[case]))
        result="entrees : {%s} \nsorties : {%s}"%(", ".join(entreesTemp),", ".join(sortiesTemp))
        return result
    
    def __setitem__(self,nomCase,case):
        if self.mutable and not nomCase in self.entrees:
            raise ValueError("%s not in Paradigme"%nomCase)
        else:
            self.entrees[nomCase]=case
            if not nomCase in self.sorties:
                self.sorties[nomCase]=Case(nomCase)
        
    def __getitem__(self,nomCase):
        return self.entrees[nomCase]
    
    def strict(self,mutable):
        self.mutable=mutable
    
    def addEntree(self,case):
        if not case.nom in self.entrees:
            self.entrees[case.nom]=case
        else:
            warnings.warn("%s déjà dans le paradigme d'entrée"%case)

    def addEntrees(self,*cases):
        for case in cases:
            self.addEntree(case)

    
    def addSortie(self,case):
        if not case.nom in self.sorties:
            self.sorties[case.nom]=case
        else:
            warnings.warn("%s déjà dans le paradigme de sortie"%case)
            
    def addSorties(self,*cases):
        for case in cases:
            self.addSortie(case)    

    def addSupporter(self,paire,ruleDist):
        '''
        Ajouter la forme d'entrée de la paire supporte la forme de sortie
        '''
        inCase=paire.entree
        outCase=paire.sortie
        if not outCase in self.supporters:
            self.supporters[outCase]={}
        if not ruleDist.sortie in self.supporters[outCase]:
            self.supporters[outCase][ruleDist.sortie]=FormeClasse()
        self.supporters[outCase][ruleDist.sortie].addRule(RegleDist(ruleDist.regle,ruleDist.dist,ruleDist.nom+":"+inCase,ruleDist.sortie))
