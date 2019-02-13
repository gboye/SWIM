#%% [markdown]
# # Trouver les CF sous-jacentes dans les règles
# Pour trouver les CF sous-jacentes dans les règles, on commence par calculer les contextes de transformation réciproque pour chaque paire de cases, c'est à dire pour chaque famille de règles de transformation
#%% [markdown]
# ## Importations
# - codecs pour les encodages
# - pandas et numpy pour les calculs sur tableaux
# - matplotlib pour les graphiques
# - itertools pour les itérateurs sophistiqués (paires sur liste, ...)

#%%

import codecs,glob
import features
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import networkx as nx
import pickle,yaml
#%pylab inline
#pd.options.display.mpl_style = 'default'
debug=False

#%% [markdown]
# ### Préparation des matrices de traits

#%%
features.add_config('bdlexique.ini')
fs=features.FeatureSystem('phonemes')


#%%
rep="/Users/gilles/ownCloud/Recherche/Boye/HDR/Data/Longitudinales/"
rep="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/Longitudinales/"
fichiers=glob.glob(rep+"*X-Regles.pkl")
samples=[f.rsplit("/",1)[-1].split("Regles")[0] for f in fichiers]
samples={int(s.split("-")[1]):s for s in samples}
samples


#%%
sample=samples[10]
fRulesPMS="Regles.pkl"
fRulesPMO="Morphomes-Regles.pkl"

#%% [markdown]
# # Classe pour la gestion des patrons, des classes et des transformations

#%%
class paireClasses:
    def __init__(self,case1,case2):
        self.case1=case1
        self.case2=case2
        self.nom=case1+"-"+case2
        self.classes1=classesPaire(case1,case2)
        self.classes2=classesPaire(case2,case1)

    def ajouterPatron(self,n,patron,motif):
        if n==1:
            self.classes1.ajouterPatron(patron,motif)
        elif n==2:
            self.classes2.ajouterPatron(patron,motif)
        else:
            print "le numéro de forme n'est pas dans [1,2]",n

    def ajouterPaire(self,forme1,forme2):
        self.classes1.ajouterPaire(forme1,forme2)
        self.classes2.ajouterPaire(forme2,forme1)
        
    def calculerClasses(self):
        return(self.classes1,self.classes2)

    
class classesPaire:
    '''
    Gestion des patrons, des classes et des transformations
    
    ajouterPatron : ajoute un patron et son motif associé (MGL)
    ajouterPaire : ajoute une paire de formes, calcule la classe de la forme1 et la règle sélectionnée
    sortirForme : cacule les formes de sortie correspondant à la forme1 avec leurs coefficients respectifs
    '''
    def __init__(self,case1,case2):
        self.case1=case1
        self.case2=case2
        self.nom=case1+"-"+case2
        self.classe={}
        self.nbClasse={}
        self.patrons={}
        self.entree={}
        self.sortie={}
    
    def ajouterPatron(self,patron,motif):
        self.patrons[patron]=motif
        (entree,sortie)=patron.split("-")
        self.entree[patron]=entree.replace(u".",u"(.)")
        self.sortie[patron]=remplacementSortie(sortie)
    
    def ajouterPaire(self,forme1,forme2):
        '''
        on calcule la classe de la paire idClasseForme et la règle sélectionnée
        on incrémente le compteur de la classe et celui de la règle sélectionnée à l'intérieur de la classe
        '''
        classeForme=[]
        regleForme=""
        for patron in self.patrons:
            if re.match(self.patrons[patron],forme1):
                classeForme.append(patron)
                '''
                le +"$" permet de forcer l'alignement à droite pour les transformations suffixales
                '''
                if forme2==re.sub(self.entree[patron]+"$",self.sortie[patron],forme1):
                    regleForme=patron
        idClasseForme=", ".join(classeForme)
        if not idClasseForme in self.classe:
            self.classe[idClasseForme]={}
            self.nbClasse[idClasseForme]=0
        if not regleForme in self.classe[idClasseForme]:
            self.classe[idClasseForme][regleForme]=0
        self.nbClasse[idClasseForme]+=1
        self.classe[idClasseForme][regleForme]+=1

    def sortirForme(self,forme,contextFree=False):
        classeForme=[]
        sortieForme={}
        for patron in self.patrons:
            if contextFree:
                filterF1=".*"+patron.split("-")[0]+"$"
            else:
                filterF1=self.patrons[patron]
            if re.match(filterF1,forme):
                classeForme.append(patron)
        if classeForme:
            idClasseForme=", ".join(classeForme)
            if contextFree:
                nbClasse=self.nbClasseCF
                classe=self.classeCF
            else:
                nbClasse=self.nbClasse
                classe=self.classe
            if idClasseForme in nbClasse:
                nTotal=nbClasse[idClasseForme]
                for patron in classe[idClasseForme]:
                    sortie=re.sub(self.entree[patron]+"$",self.sortie[patron],forme)
                    sortieForme[sortie]=float(classe[idClasseForme][patron])/nTotal
            else:
#                if debug: 
#                    print (forme, file=logfile)
#                    print ("pas de classe",idClasseForme, file=logfile)
#                    print ("%.2f par forme de sortie" % (float(1)/len(classeForme)), file=logfile)
                nTotal=len(classeForme)
                for patron in classeForme:
                    sortie=re.sub(self.entree[patron]+"$",self.sortie[patron],forme)
                    sortieForme[sortie]=float(1)/nTotal
#        else:
#            if debug:
#                print (forme, file=logfile) 
#                print ("pas de patron", file=logfile)
        return sortieForme
        

#%% [markdown]
# ## Ouvrir les fichiers de règles

#%%
with open(rep+sample+fRulesPMS, 'rb') as input:
    rulesPMS = pickle.load(input)
with open(rep+sample+fRulesPMO, 'rb') as input:
    rulesPMO = pickle.load(input)

rules=rulesPMO

#%% [markdown]
# ## Conversion Positions <=> Regex

#%%
def getRegexPositions(positions):
    return "".join([p if len(p)<2 else "[%s]"%''.join(sorted(p)) for p in positions])


#%%
def getPositionsRegex(regex):
    if regex=="": return []
    result=[]
    regex=re.sub(ur"[()]","",regex.replace(".*","X"))
    chunks=[c for c in re.split(ur"(\[[^\]]+\])",regex) if c!=""]
    if chunks[0].startswith("^"): chunks[0]=chunks[0][1:]
    if chunks[-1].endswith("$"): chunks[-1]=chunks[-1][:-1]
    for chunk in chunks:
        if chunk.startswith("["): 
            result.append(chunk.replace("[","").replace("]",""))
        else:
            result.extend(chunk)
    return result

#%% [markdown]
# ## Calcul des intersections

#%%
def getIntersectionPos(l1,l2):
    l=set()
    if l1=="X" or l1==".":
        l=set(l2)
    elif l2=="X" or l2==".":
        l=set(l1)
    else:
        l=set(l1)&set(l2)
    return l

def getIntersectionRegex(gP1,gP2,debug=False):
    p1=gP1[:]
    p2=gP2[:]
    pMin,pMax=sorted([p1,p2],key=len)
    temp=[]
    pMin.reverse()
    pMax.reverse()
#    print p1,p2
    for i in range(len(pMin)):
        l=getIntersectionPos(pMin[i],pMax[i])
        if l:
            temp.append(l)
        else:
            return []
    if len(pMax)>len(pMin):
        if pMin[-1]=="X":
            for i in range(len(pMin),len(pMax)):
                temp.append(set(pMax[i]))
        elif pMax[len(pMin)]!="X":
            temp.append("")
    temp.reverse()
    result=[]
    for c in temp:
        result.append("".join(c))
    if "" in result:
        result=""
    return result

#%% [markdown]
# ## Calcul des transformations

#%%
def transformeExp(gPositions,patron):
    result=[]
    positions=gPositions[:]
    positions.reverse()
    e0,s0=patron.split("-")
    e1=re.split(ur"(\.)",e0)
    s1=re.split(ur"(\.)",s0)
    e1.reverse()
    s1.reverse()
#    print e1, s1, positions
    lPosition=0
    for nChunk,chunk in enumerate(e1):
#        print "chunk",chunk, nChunk, "pos", lPosition
        if chunk!=".":
            if chunk:
                for nLettre,lettre in enumerate(chunk):
    #                print "lettre",nLettre,lettre,"pos",lPosition
                    if nLettre==0: result.extend(s1[nChunk][::-1])
                    lPosition+=1
            else:
                result.extend(s1[nChunk][::-1])
        else:
#            print "lettre",positions[lPosition],"pos",lPosition
            result.append(positions[lPosition])
            lPosition+=1
#    print result
    if len(positions)>lPosition:
        for i in range(lPosition,len(positions)):
            result.append(positions[i])
    elif positions[-1]==u"X":
        result.append(u"X")
    result.reverse()
    return [r for r in result if r!=""]
        

#%% [markdown]
# ## Calcul des contraintes

#%%
def nouvellesContraintes(contraintes,paire,addEdge=False,gPatrons=[]):
    if not gPatrons:
        patrons=patronsConsideres[paire]
    else:
        patrons=gPatrons[paire]
    result1=[]
#    result2={}
    for r in contraintes:
        for p in patrons:
            regexRegle=getPositionsRegex(patrons[p])
            regex=getIntersectionRegex(r,regexRegle)
            if regex:
                trans=transformeExp(regex,p)
                if trans:
                    result1.append(trans)
#                    result2[p]=(regex,trans)
                    if addEdge:
                        pointA=paire[0]+":"+getRegexPositions(regex)
                        pointB=paire[1]+":"+getRegexPositions(trans)
                        if debug: print pointA+"-"+pointB
                        reseauTrans.add_edge(pointA,pointB,key=p)
                    if debug:
                        print "TRANS",r, p, regex
                        print "=>",trans
    if result1:
        return result1
    else:
        return contraintes

def getContraintes(A,B,gPatrons=[]):
    aller=nouvellesContraintes([[u"X"]],(A,B),gPatrons=gPatrons)
    retour=nouvellesContraintes(aller,(B,A),gPatrons=gPatrons)
    return retour

def getListesContraintes(dictA,A,nodes,gPatrons=[]):
    lDictA=dict(dictA)
    for node in nodes:
        lDictA[node]=getContraintes(A,node,gPatrons=gPatrons)
    return lDictA

def mergeContraintesAB(contraintesA,contraintesB):
    result=set()
    for a in contraintesA:
        for b in contraintesB:
            intersection=getIntersectionRegex(a,b)
            if intersection:
                result.add(getRegexPositions(intersection))
    return [getPositionsRegex(p) for p in list(result)]

def mergeContraintes(dictA):
    cases=dictA.keys()
    contraintes=dictA[cases[0]]
    for case in cases[1:]:
        if dictA[case]:
            contraintes=mergeContraintesAB(contraintes,dictA[case])
    return contraintes

#%% [markdown]
# ## Patrons sans contextes

#%%
patronsAvecContexte={}
patronsSansContexte={}
for paire in rules.keys():
    patronsAvecContexte[paire]=rules[paire].patrons
    for r in patronsAvecContexte[paire]:
        if not paire in patronsSansContexte:
            patronsSansContexte[paire]={}
        transformation=r.split("-")[0]
        patronsSansContexte[paire][r]=u"^(.*)%s$"%transformation

patronsConsideres=patronsSansContexte

#%% [markdown]
# ## Définition des cases à prendre en compte

#%%
paradigmeCases=list(set([p[0] for p in rules.keys()]))
#paradigmeCases=[c for c in paradigmeCases if not "1" in c and not "2" in c and not "ai" in c and not "is" in c]
selectionCases=paradigmeCases
#selectionCases=testCells
selectionCases

#%% [markdown]
# # Contraintes en étoile

#%%
eliminationCases=["is%d%s"%(i,n) for i in range(1,4) for n in "SP"]+["ppFS","ppFP"]
selectionCases=[c for c in selectionCases if not c in eliminationCases]
contraintesCase={c:{} for c in selectionCases}
contraintesConsolidees={}
for a in contraintesCase:
    for b in [c for c in contraintesCase if c!=a]:
        contraintesTemp=nouvellesContraintes([[u"X"]],(b,a))
        contraintesCase[a][b]=contraintesTemp
#print contraintesCase["ps1P"]

#%% [markdown]
# ## Simplifier les contraintesConsolidees

#%%
for c in contraintesCase:
    contraintesConsolidees[c]=mergeContraintes(contraintesCase[c])

for a in contraintesCase:
    for b in [c for c in contraintesCase if c!=a]:
        contraintesTemp=nouvellesContraintes(contraintesConsolidees[b],(b,a))
        contraintesCase[a][b]=contraintesTemp

for c in contraintesCase:
    contraintesConsolidees[c]=mergeContraintes(contraintesCase[c])


#%%
reseauTrans=nx.DiGraph()
for k in contraintesCase:    
    for elt in [c for c in contraintesCase if c!=k]:
#        print k,elt,contraintesConsolidees[k]
        nouvellesContraintes(contraintesConsolidees[k],(k,elt),addEdge=True)


#%%
reseauSimTrans=nx.Graph()
for edge in reseauTrans.edges():
    a,b=sorted(edge)
    if reseauTrans.has_edge(a,b) and reseauTrans.has_edge(b,a) and not reseauSimTrans.has_edge(a,b):
        reseauSimTrans.add_edge(a,b)
cliques=list(nx.find_cliques(reseauSimTrans))
cliquesCompletes=0
print len(cliques)
print len(selectionCases)
for c in cliques:
    if len(c)==len(selectionCases) or len(c)>len(selectionCases)-1:
        cliquesCompletes+=1
#        for e in sorted(c):
#            if e.startswith("inf") and e.endswith("]e"):
#                print sorted(c)
#                print e
#                print
        print sorted(c)
print cliquesCompletes


