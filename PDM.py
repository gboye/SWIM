# -*- coding: utf-8 -*-

import re
import warnings
import networkx as nx

seuilDistribution=0.01

verbose=False
verbose1=False
verbose2=False

def strFloat(num):
    '''
    string de l'arrondi d'un float à deux chiffres après le point
    '''
    return ("%0.2f"%num).rstrip("0").rstrip(".")

def parserPaire(line):
    '''
    parse une ligne de la sortie de PredSPE pour une paire comme :
    ipf.1 ==> prs.1
    '''
    m=re.search("^\s*(\S+)\s+==>\s+(\S+)\s*$",line)
    if m:
        inCase=m.group(1)
        outCase=m.group(2)
        return (inCase,outCase)
    else:
        return False

def parserRegle(line):
    '''
    parse une ligne de la sortie de PredSPE pour une règle comme :
    E --> jô / X ___ #
    '''
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

def distributionVecteurs(vecteurs):
    '''
    normalise la distribution sur un ensemble de vecteurs
    '''
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
    '''
    renvoie la transformation de forme par inPatron et mod ou sinon False
    '''
    extrait=re.search(inPatron,forme)
    if extrait:
        sortie=extrait.group(1)+mod+extrait.group(2)
        return sortie
    else:
        return False

def modifierForme(forme,numRegle):
    patron=analyse.regles[numRegle].patron
    mod=analyse.regles[numRegle].mod

    m=re.search(patron,forme)
    if m:
        sortie=m.group(1)+mod+m.group(2)
        return(forme,sortie)
    else:
        return (forme,"")

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
        
    def __eq__(self,other):
        result=True
        result=result and (self.regle==other.regle)
        result=result and (self.dist==other.dist)
        result=result and (self.sortie==other.sortie)
        result=result and (self.nom==other.nom)
        return result
        
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
        return (self.regle,self.dist,self.sortie,self.nom,self.etiquette)        

class FormeClasse:
    '''
    Cette classe permet de stocker une classe de sorties pour une forme
    '''
    
    def __init__(self,nom="",etiquette=True):
        self.nom=str(nom)
        self.etiquette=etiquette
        self.reglesDist={}
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
          
    def addRule(self,regleDist,**kwargs):
        if "force" in kwargs:
            force=kwargs["force"]
        else:
            force=False
        if force or not regleDist.regle in self.reglesDist:
            self.reglesDist[regleDist.regle]=regleDist
        else:
            warnings.warn("La règle %d est déjà dans la distribution %s"%(regleDist.regle,regleDist))

    def addRules(self,*reglesDist,**kwargs):
        if "force" in kwargs:
            force=kwargs["force"]
        else:
            force=False
        for regleDist in reglesDist:
            self.addRule(regleDist,force=force)
    
    def updateTotal(self):
        self.total=0
        for regle in self.reglesDist:
            if self.reglesDist[regle].dist > seuilDistribution:
                self.total+=self.reglesDist[regle].dist
        
    def numRulesDist(self):
        '''
        Renvoie une distribution normalisée
        '''
        self.updateTotal()
        normalReglesDist=[]
        for regle in self.reglesDist:
            dr=self.reglesDist[regle]
            if dr.dist > seuilDistribution:
                normalDist=float(strFloat(dr.dist/self.total))
            else:
                normalDist=0
            normalReglesDist.append(RegleDist(dr.regle,normalDist,dr.sortie,dr.nom,dr.etiquette))
        return normalReglesDist
    
    def getRules(self):
        listeNum=[]
        for element in self.reglesDist:
            listeNum.append(str(element))
        return "-".join(sorted(listeNum,key=int))

class FormesDist(FormeClasse):
    '''
    Classe distributionnelle pour une forme
    '''
    
    def __eq__(self,other):
        '''
        Compare le contenu de deux FormesDist (nom et les RegleDist de la liste)
        '''
        result=(self.nom==other.nom)
        if result:
            for rd in self.reglesDist:
                result=result and (self.reglesDist[rd]==other.reglesDist[rd])
            return result
        else:
            return False

    def __repr__(self):
        temp=[]
        for element in self.numRulesDist():
            temp.append(str(element))
        if self.nom!="":
            nomClasse=self.nom+" : "
        else:
            nomClasse=""
        return "%s[%s]"%(nomClasse,", ".join(temp))

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
    
analyse=Regles()
classification=Classes()

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
        self.total=0
        
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
    
    def addForms(self,FormesCoefs):
        for FormeCoef in FormesCoefs:
            self.addForm(FormeCoef)

    def updateTotal(self):
        self.total=0
        for formeCoef in self.valeurs:
            self.total+=formeCoef.coef
        
    def numValeurs(self):
        '''
        Renvoie une distribution normalisée
        '''
        self.updateTotal()
        formeCoefs={}
        for formeCoef in self.valeurs:
            if verbose2: print ("formeCoef", formeCoef)
            if not formeCoef.forme in formeCoefs:
                formeCoefs[formeCoef.forme]=0
            formeCoefs[formeCoef.forme]+=formeCoef.coef
        normalValeurs=[]
        for forme in formeCoefs:
            normalValeurs.append(FormeCoef(forme,float(strFloat(formeCoefs[forme]/self.total))))
        return normalValeurs

class NewCase:
    '''
    Distribution des formes dans une case
    '''
    
    def __init__(self,nom=""):
        self.nom=nom
        self.coefs={}
        
    def __getitem__(self,index):
        return self.coefs[index]

    def addFormeCoefs(self,*formeCoefs):
        for formeCoef in formeCoefs:
            self.coefs[formeCoef.forme]=formeCoef.coef
        
    def getTotal(self):
        total=0
        for forme in self.coefs:
            total+=self.coefs[forme]
        return total
        
    def rawDistribution(self):
        result=[]
        for forme in self.coefs:
            result.append[FormeCoef(forme,self.coefs[forme])]
        return result
            
    def normDistribution(self):
        result=[]
        total=self.getTotal()
        for forme in self.coefs:
            result.append[FormeCoef(forme,float(strFloat(self.coefs[forme])/total))]
        return result
        
    
class Paradigme:
    '''
    Cet objet contient deux tableaux associatifs entrees et sorties qui contiennent des objets Case
    le tableau supporter est prévu pour noter la contribution des entrées aux sorties
    les cases du paradigme sont fixées par défaut à la création (mutable=False)
    '''
    def __init__(self,Cases=[],mutable=False):
        self.entrees={}
        self.sorties={}
        self.intermediaires={}
        self.nouveau={}
        self.mutable=mutable
        self.digraphe=nx.DiGraph()
        self.graphe=nx.Graph()
        for case in Cases:
            self.entrees[case]=Case(case)
            self.sorties[case]={}

    def __repr__(self):
        entreesTemp=[]
        for case in self.entrees:
            entreesTemp.append(case+" : "+repr(self.entrees[case]))
        sortiesTemp=[]
        for case in self.sorties:
            sortiesTemp.append(repr(case))
            for paire in self.sorties[case]:
                sortiesTemp.append("\t"+repr(paire)+" : "+repr(self.sorties[case][paire]))
        result="entrees : {\n\t%s\n} \nsorties : {\n\t%s\n}"%("\n\t".join(entreesTemp),"\n\t".join(sortiesTemp))
        return result
    
    def __setitem__(self,nomCase,case):
        if self.mutable and not nomCase in self.entrees:
            raise ValueError("%s not in Paradigme"%nomCase)
        else:
            self.entrees[nomCase]=case
        
    def __getitem__(self,nomCase):
        return self.entrees[nomCase]
    
    def strict(self,mutable):
        self.mutable=mutable
    
    def addEntree(self,case):
        '''
        Ajouter la distribution de formes (Case) pour une case d'entrée
        '''
        if not case.nom in self.entrees:
            self.entrees[case.nom]=case
        else:
            warnings.warn("%s déjà dans le paradigme d'entrée %s"%(case,self.entrees[case.nom]))

    def addEntrees(self,*cases):
        for case in cases:
            self.addEntree(case)

    def addEdge(self,paire,formeClasse):
        '''
        Ajouter des arcs dans le graphe pour la paire et la formeClasse
        '''
        nDepart=paire.entree+"-"+formeClasse.nom
        self.graphe.add_node(nDepart,weight=self.getCoefNewForm(paire.entree,formeClasse.nom))
        rulesDist=formeClasse.numRulesDist()
        for rd in rulesDist:
            coef=self.getCoefNewForm(paire.sortie,rd.sortie)
#            if rd.dist>seuilDistribution or True:
            if coef>seuilDistribution:
                nArrivee=paire.sortie+"-"+rd.sortie
                self.digraphe.add_node(nArrivee,weight=coef)
                self.digraphe.add_edge(nDepart,nArrivee,weight=rd.dist)
#                self.digraphe.add_edge(nDepart,nArrivee,weight=coef)
                if self.digraphe.has_edge(nArrivee,nDepart) and "weight" in self.digraphe[nDepart]:
                    poids=(self.digraphe[nDepart][nArrivee]["weight"]+self.digraphe[nArrivee][nDepart]["weight"])/2
                    self.graphe.add_node(nDepart,weight=self.digraphe[nDepart]["weight"])
                    self.graphe.add_node(nArrivee,weight=self.digraphe[nArrivee]["weight"])
                    self.graphe.add_edge(nDepart,nArrivee,weight=poids)
                
    def addSortie(self,paire,formeClasse):
        '''
        Ajouter une distribution de formes à une case de sortie
        '''
        if not paire.sortie in self.sorties:
            self.sorties[paire.sortie]={}

        if not paire in self.sorties[paire.sortie]:
            self.sorties[paire.sortie][paire]=[]
        formesDist=FormesDist(formeClasse.nom)
        formesDist.reglesDist=formeClasse.reglesDist
        if not formesDist in self.sorties[paire.sortie][paire]:
            self.sorties[paire.sortie][paire].append(formesDist)
            self.addEdge(paire,formeClasse)
        else:
            warnings.warn("%s déjà dans le paradigme de sortie %s %s"%(formesDist,paire,self.sorties[paire.sortie][paire]))
            
    def addSorties(self,paire,*formeClasses):
        for formeClasse in formeClasses:
            self.addSortie(paire,formeClasse)    
    
    def getCoefNewForm(self,nomCase,forme):
        '''
        Renvoi le coef d'une forme dans self.nouveau[nomCase]
        '''
        if nomCase in self.nouveau:
            for formeCoef in self.nouveau[nomCase]:
                if formeCoef.forme==forme:
                    return formeCoef.coef
        return 0
    
    def calculNouveau(self):
        '''
        Calculer le nouveau paradigme à partir des sorties
        '''
        for nomCase in self.sorties:
            if verbose: print("nom Case",nomCase)
            case=Case(nomCase)
            for vecteur in self.sorties[nomCase]:
                if verbose: print("\tvecteur",vecteur)
                for fc in self.sorties[nomCase][vecteur]:
                    if verbose: print("\t\tforme classe",fc)
                    for rd in fc.numRulesDist():
                        if verbose: print("\t\t\trègle distribution",rd)
                        if rd.dist!=0:
                            case.addForm(FormeCoef(rd.sortie,rd.dist))
            if verbose: print ("temp case %s : %s" % (nomCase,case.valeurs))
            nouvelleCase=Case(nomCase)
            nouvelleCase.addForms(case.numValeurs())
            if verbose: print ("nouvelle case %s : %s" % (nomCase,nouvelleCase.valeurs))
            self.nouveau[nomCase]=nouvelleCase

    def calculSorties(self,lexical):
        '''
        Calculer les sorties à partir
        '''
        for inCase in lexical:
            if verbose: print("inCase",inCase,lexical[inCase].valeurs)
            for formeCoef in lexical[inCase].numValeurs():
                if verbose: print("\tforme coef",formeCoef)
                forme=formeCoef.forme
                for outCase in analyse.pairesCase[inCase]:
                    if verbose: print("\t\toutCase",outCase)
                    paire=Paire(inCase,outCase)
                    formeSorties=FormeClasse(forme)
                    for numRegle in analyse.reglesPaire[paire]:
                        (entree,sortie)=modifierForme(forme,numRegle)
                        if sortie!="":
                            formeSorties.addRule(RegleDist(numRegle,1,sortie,entree),force=True)
                    if formeSorties in classification.classes[paire]:
                        numClasse=classification.classes[paire].index(formeSorties)
                        for numRegle in formeSorties.reglesDist:
                            formeSorties.reglesDist[numRegle].dist=classification.classes[paire][numClasse].reglesDist[numRegle].dist
                        self.addSortie(paire,formeSorties)
                        if verbose: print("\t\t\tformeSorties",paire,formeSorties)
#                        for rd in formeSorties.numRulesDist():
#                            if rd.dist!=0:
#                                self.addSupporter(paire,rd)
                    else:
                        if verbose: print ("formeSorties",formeSorties.getRules())
                        if verbose: print ("classes", classification.classes[paire])
                        if verbose: print ("pas de classe", paire, formeSorties)

    def calculerParadigme(self):
        self.calculSorties(self.entrees)
        if verbose: print("verbes.sorties")
        self.calculNouveau()
        self.digraphe=nx.DiGraph()
        self.graphe=nx.Graph()
        self.sorties={}
        self.calculSorties(self.nouveau)
        self.calculNouveau()
    

    def supportsEntrees(self):
        for case in self.entrees:
            print (case)
            for formeCoef in self.entrees[case].numValeurs():
                print ("\t",formeCoef.forme)
                if formeCoef.forme in self.supporters[case]:
                    for element in self.supporters[case][formeCoef.forme]:
                        print ("\t\t",element,self.supporters[case][formeCoef.forme][element])
            print ()
    
    def supportsSorties(self):
        for case in self.sorties:
            print (case)
            for paire in self.sorties[case]:
                print ("\t",paire)
                for element in self.sorties[case][paire]:
                    print ("\t\t",element)



