
# coding: utf-8

# # Génération des réseaux de formes à partir des règles
# - Swim1 basé sur l'échantillon initial
#  - Gén-1 : génération des formes d'après les contextes phonologiques
#  - Gén-2 : génération du réseau d'après les contextes phonologiques
#  - Filt-1 : extraction du sous-réseau symétrique
#  - Filt-2 : génération du réseau non-orienté correspondant à Filt-1
#  - Filt-3 : extraction des cliques maximales & fidèles
# - Swim2 basé sur le réseau calculé par Swim1
#  - Exp : génération d'un nouvel échantillon basé sur Swim1
#  - Gén-1 : génération des formes sans contexte phonologique
#  - Gén-2 : génération du réseau sans contexte phonologique
#  - Filt-1 : extraction du sous-réseau symétrique
#  - Filt-2 : génération du réseau non-orienté correspondant à Filt-1
#  - Filt-3 : extraction des cliques maximales & fidèles
# - Évaluation

# ## Importations
# - codecs pour les encodages
# - pandas et numpy pour les calculs sur tableaux
# - matplotlib pour les graphiques
# - itertools pour les itérateurs sophistiqués (paires sur liste, ...)

# In[1]:

from __future__ import print_function

import codecs,operator,datetime,os,glob#,cellbell
import features
import re,sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import pickle
import networkx as nx
#%pylab inline
#pd.options.display.mpl_style = 'default'
debug=False


# In[2]:

#get_ipython().magic(u'matplotlib inline')


# In[3]:

import yaml


# In[4]:

#from ipywidgets import FloatProgress
#from IPython.display import display, HTML


# In[5]:

import datetime
def dateheure():
    return datetime.datetime.utcnow().strftime('%y%m%d%H%M')

def ding():
    print("\007")

# In[6]:
ding()

saut="\n"
details=False


# ### Préparation des matrices de traits

# In[7]:

features.add_config('bdlexique.ini')
fs=features.FeatureSystem('phonemes')


# # Choix de l'échantillon et des règles
# - *sampleFile* est le nom de l'échantillon de départ
# - *analysisPrefix* est une partie du nom des règles

# In[8]:

filePrefix="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/LongitudinalesRnd/Longitudinal"
filePrefix="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/lexique3/Longitudinal-Lexique3"
sampleFiles=glob.glob(filePrefix+"*.pkl")
def prefixEchantillon(numero,sampleType="",casesType=""):
    candidats=[]
#    matchFile=ur"^.*/Longitudinal(-%s-T\d+-F\d+)%s\.pkl"%(numero,sampleType+casesType)
    matchFile=ur"^.*/Longitudinal-Lexique3(-%s-T\d+-F\d+)%s\.pkl"%(numero,sampleType+casesType)
    for sample in sampleFiles:
        m=re.match(matchFile,sample)
        if m:
#            print (sample)
#            print (m.group(1))
            candidats.append(m.group(1))
    if len(candidats)==1:
        return candidats[0]
    else:
        print ("PB pas de nom unique correspondant",len(candidats))


# In[9]:

goldPrefix="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/"
goldFile="MGC-171229-Verbes3.pkl"
arguments=sys.argv
if len(arguments)>1:
    sampleNumero=arguments[1]
    if len(arguments)>2:
        sampleType=arguments[2]
        if len(arguments)>3:
            casesType=arguments[3]
        else:
            casesType=""
    else:
        sampleType="-X"
        casesType=""
else:
    sampleNumero="00"
    sampleType="-X"
    casesType=""

print (sampleNumero,sampleType,casesType)
if casesType:
    sampleNumber=prefixEchantillon(sampleNumero,sampleType,casesType)
else:
    sampleNumber=prefixEchantillon(sampleNumero)
print (sampleNumber)
paperPrefix="-ISMo"
genFormeVotes=True
genCliques=True
listeFormesOutput=["FS","FP"]
genDigraphe=False
genGraphe=False
plotDistributionCliques=False
if casesType:
    samplePrefix=filePrefix+"%s-%s"%(sampleNumber,sampleType.strip("-"))+casesType
    tirageFile=samplePrefix+".pkl"
elif sampleType:
    samplePrefix=filePrefix+"%s-%s"%(sampleNumber,sampleType.strip("-"))
    tirageFile=filePrefix+sampleNumber+".pkl"
else:
    samplePrefix=filePrefix+"%s-X"%(sampleNumber)
    tirageFile=filePrefix+sampleNumber+".pkl"
sampleFile=samplePrefix+"-paradigmes.csv"
initialFile=filePrefix+prefixEchantillon(sampleNumero)+sampleType+"-paradigmes.csv"
print (initialFile)
analysisPrefix=samplePrefix
if debug:
    logfile_name=analysisPrefix+"-network.log"
    logfile = codecs.open(logfile_name,mode='w',encoding="utf8")


# In[10]:

#tirage=filePrefix+'-'+sampleNumber+'-Tirage-'+sampleType+'-170503-1907'+casesType+'.pkl'
#tirage=filePrefix+sampleNumber+casesType+'.pkl'
print (tirageFile)
with open(tirageFile, 'rb') as input:
    sampleTirage = pickle.load(input)


# In[11]:

if not "morphome" in sampleTirage.columns.tolist():
    sampleTirage["morphome"]=sampleTirage["case"]
morphomeCases=sampleTirage[["case","morphome"]].drop_duplicates().to_dict()
casesMC=morphomeCases["case"]
morphomesMC=morphomeCases["morphome"]
dictMorphomeCases={}
for element in casesMC:
    dictMorphomeCases[casesMC[element]]=morphomesMC[element].split("/")
dictMorphomeCases


# # Préparation du calcul des analogies

# ### Calcul de la différence entre deux formes

# In[12]:

def diff(mot1,mot2):
    result=[]
    diff1=""
    diff2=""
    same=""
    vide="."
    lmax=max(len(mot1),len(mot2))
    lmin=min(len(mot1),len(mot2))
    for index in range(lmax):
        if index < lmin:
            if mot1[index]!=mot2[index]:
                diff1+=mot1[index]
                diff2+=mot2[index]
                same+=vide
            else:
                same+=mot1[index]
                diff1+=vide
                diff2+=vide
        elif index < len(mot1):
            diff1+=mot1[index]
        elif index < len(mot2):
            diff2+=mot2[index]
    diff1=diff1.lstrip(".")
    diff2=diff2.lstrip(".")
#    return (same,diff1,diff2,diff1+"_"+diff2)
    return (diff1+"-"+diff2)


# ### Accumulation des paires appartenant à un patron

# In[13]:

def rowDiff(row, patrons):
    result=diff(row[0],row[1])
    if not result in patrons:
        patrons[result]=(formesPatron(),formesPatron())
    patrons[result][0].ajouterFormes(row[0])
    patrons[result][1].ajouterFormes(row[1])
    return (result[0],result[1])


# ### Transformation d'un patron en RegExp

# In[14]:

def patron2regexp(morceaux):
    result="^"
    for morceau in morceaux:
        if morceau=="*":
            result+="(.*)"
        elif len(morceau)>1:
            result+="(["+morceau+"])"
        else:
            result+=morceau
    result+="$"
    result=result.replace(")(","")
    return result


# ### Substitution de sortie
# ???

# In[15]:

def remplacementSortie(sortie):
    n=1
    nsortie=""
    for lettre in sortie:
        if lettre==".":
            nsortie+="\g<%d>"%n
            n+=1
        else:
            nsortie+=lettre
    return nsortie


# # Classe pour la gestion des patrons, des classes et des transformations

# In[16]:

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
            if debug: print ("le numéro de forme n'est pas dans [1,2]",n, file=logfile)

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
        self.classeCF={}
        self.nbClasseCF={}

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
        classeFormeCF=[]
        regleFormeCF=""
        classeForme=[]
        regleForme=""
        for patron in self.patrons:
            filterF1=".*"+patron.split("-")[0]+"$"
            if re.match(filterF1,forme1):
                classeFormeCF.append(patron)
                if forme2==re.sub(self.entree[patron]+"$",self.sortie[patron],forme1):
                    regleFormeCF=patron
            filterF1=self.patrons[patron]
            if re.match(filterF1,forme1):
                classeForme.append(patron)
                '''
                le +"$" permet de forcer l'alignement à droite pour les transformations suffixales
                '''
                if forme2==re.sub(self.entree[patron]+"$",self.sortie[patron],forme1):
                    regleForme=patron
        idClasseFormeCF=", ".join(classeFormeCF)
        if not idClasseFormeCF in self.classeCF:
            self.classeCF[idClasseFormeCF]={}
            self.nbClasseCF[idClasseFormeCF]=0
        if not regleFormeCF in self.classeCF[idClasseFormeCF]:
            self.classeCF[idClasseFormeCF][regleFormeCF]=0
        self.nbClasseCF[idClasseFormeCF]+=1
        self.classeCF[idClasseFormeCF][regleFormeCF]+=1

        idClasseForme=", ".join(classeForme)
        if not idClasseForme in self.classe:
            self.classe[idClasseForme]={}
            self.nbClasse[idClasseForme]=0
        if not regleForme in self.classe[idClasseForme]:
            self.classe[idClasseForme][regleForme]=0
        self.nbClasse[idClasseForme]+=1
        self.classe[idClasseForme][regleForme]+=1

    def sortirForme(self,forme,contextFree=True):
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
                if debug:
                    print (forme, file=logfile)
                    print ("pas de classe",idClasseForme, file=logfile)
                    print ("%.2f par forme de sortie" % (float(1)/len(classeForme)), file=logfile)
                nTotal=len(classeForme)
                for patron in classeForme:
                    sortie=re.sub(self.entree[patron]+"$",self.sortie[patron],forme)
                    sortieForme[sortie]=float(1)/nTotal
        else:
            if debug:
                print (forme, file=logfile)
                print ("pas de patron", file=logfile)
        return sortieForme



# ## Appliquer la formule de calcul des différences entre chaines à chaque ligne
#
# >si il y a au moins une ligne
#
# >>on applique la différence à la ligne
#
# >>on calcule les deux patrons par suppression des points initiaux
#
# >>on renvoie le groupement par patrons (1&2)
#
# >sinon
#
# >>on renvoie le paradigme vide d'origine

# In[17]:

def rapports(paradigme):
    if len(paradigme.columns.values.tolist())==2:
        (case1,lexeme)= paradigme.columns.values.tolist()
        case2=case1
    else:
        (case1,case2,lexeme)= paradigme.columns.values.tolist()
    patrons=pairePatrons(case1,case2)
    classes=paireClasses(case1,case2)
    if len(paradigme)>0:
        paradigme.apply(lambda x: patrons.ajouterFormes(x[case1],x[case2],diff(x[case1],x[case2])), axis=1)
        (regles1,regles2)=patrons.calculerGM()
        for regle in regles1:
            classes.ajouterPatron(1,regle,regles1[regle])
        for regle in regles2:
            classes.ajouterPatron(2,regle,regles2[regle])
        paradigme.apply(lambda x: classes.ajouterPaire(x[case1],x[case2]), axis=1)
    (classes1,classes2)=classes.calculerClasses()
    return (classes1,classes2)


# ### Dédoubler les lignes avec des surabondances dans *colonne*
# >identifier une ligne avec surabondance
#
# >>ajouter les lignes correspondant à chaque valeur
#
# >>ajouter le numéro de la ligne initiale dans les lignes à supprimer
#
# >supprimer les lignes avec surabondance
#
# NB : il faut préparer le tableau pour avoir une indexation qui permette l'ajout des valeurs individuelles et la suppression des lignes de surabondances

# In[18]:

def splitCellMates(df,colonne):
    '''
    Calcul d'une dataframe sans surabondance par dédoublement des valeurs
    '''
    test=df.reset_index()
    del test["index"]
    splitIndexes=[]
    for index,ligne in test.iterrows():
        if "," in ligne[colonne]:
            valeurs=set(ligne[colonne].split(","))
            nouvelleLigne=ligne
            for valeur in valeurs:
                nouvelleLigne[colonne]=valeur
                test=test.append(nouvelleLigne,ignore_index=True)
            splitIndexes.append(index)
    if splitIndexes:
        test=test.drop(test.index[splitIndexes])
    return test


# # Lecture de l'échantillon

# In[19]:

phonologicalMap=sampleType.strip("-")
if debug: print(phonologicalMap)
neutralisationsNORD=(u"6û",u"9ê")
neutralisationsSUD=(u"e2o",u"E9O")
if phonologicalMap=="N":
    neutralisations=neutralisationsNORD
elif phonologicalMap=="S":
    neutralisations=neutralisationsSUD
else:
    neutralisations=(u"",u"")
    phonologicalMap=("X")
bdlexiqueIn = unicode(u"èò"+neutralisations[0])
bdlexiqueNum = [ord(char) for char in bdlexiqueIn]
neutreOut = unicode(u"EO"+neutralisations[1])
neutralise = dict(zip(bdlexiqueNum, neutreOut))


# In[20]:

def recoder(chaine,table=neutralise):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    else:
        result=chaine
    return result


# ### Vérification de la phonotactique des glides du français
# - si *prononciation* est *None* renvoyer *None*
# - ajout de diérèses dans les séquences mal-formées
# - vérification des séquences consonne+glide à la finale

# In[21]:

dierese={"j":"ij", "w":"uw","H":"yH","i":"ij","u":"uw","y":"yH"}


# In[22]:

def checkFrench(prononciation):
    if prononciation:
        result=recoder(prononciation)
        m=re.match(ur"^.*([^ieèEaOouy926êôâ])[jwH]$",result)
        if m:
            print ("pb avec un glide final", prononciation)
        m=re.match(ur"(.*[ptkbdgfsSvzZ][rl])([jwH])(.*)",result)
        if m:
            n=re.search(ur"[ptkbdgfsSvzZ][rl](wa|Hi|wê)",result)
            if not n:
                glide=m.group(2)
                result=m.group(1)+dierese[glide]+m.group(3)
        m=re.match(ur"(.*)([iuy])([ieEaOouy].*)",result)
        if m:
            glide=m.group(2)
            result=m.group(1)+dierese[glide]+m.group(3)
        result=result.replace("Jj","J")
    else:
        result=prononciation
    return result


# In[23]:

paradigmes=pd.read_csv(sampleFile,sep=";",encoding="utf8")
del paradigmes[u"Unnamed: 0"]
paradigmes=paradigmes.dropna(axis=1,how='all')


# In[24]:

goldCases=paradigmes.columns.tolist()
goldCases.remove("lexeme")
#goldCases


# - sampleCases pour la liste des cases effectivement représentées dans le corpus de départ

# In[25]:

sampleCases=paradigmes.columns.values.tolist()
sampleCases.remove(u"lexeme")
#sampleCases


# In[26]:

paradigmes.stack().value_counts(dropna=True).sum()


# In[27]:

len(paradigmes.dropna(thresh=1)["lexeme"])


# ## Préparation des données initiales et de référence

# In[28]:

listeTest=paradigmes.dropna(thresh=1)["lexeme"].values.tolist()
#listeTest=[u"asseoir",u"balayer",u"manger"]
nbVerbes=len(listeTest)
#print (nbVerbes)


# ### Préparation des formes initiales

# In[29]:

initialParadigmes=pd.read_csv(initialFile,sep=";",encoding="utf8")
del initialParadigmes[u"Unnamed: 0"]
initialParadigmes=initialParadigmes.dropna(axis=1,how='all')


# In[30]:

initialForms=pd.melt(initialParadigmes[paradigmes["lexeme"].isin(listeTest)],id_vars=["lexeme"]).dropna()

initialForms["lexeme-case"]=initialForms["lexeme"]+"-"+initialForms["variable"]
initialForms.drop(labels=["lexeme","variable"],axis=1,inplace=True)

initialForms.set_index(["lexeme-case"],inplace=True)

initialFormsIndex=initialForms.index.tolist()


# ### Préparation des formes de référence

# In[31]:

#with open(goldPrefix+"/"+goldFile,"rb") as input:

# with open(goldPrefix+goldFile,"rb") as input:
#     lexiqueGold=pickle.load(input)
lexiqueGold=pd.read_pickle(path=goldPrefix+goldFile)

'''Rectifications phonologiques'''
lexiqueGold["phono"]=lexiqueGold["phono"].apply(lambda x: checkFrench(x))
completeParadigmes=pd.pivot_table(lexiqueGold, values='phono', index=['lexeme'], columns=['case'], aggfunc=lambda x: ",".join(x)).reset_index().reindex()

'''Mise en liste des formes de références'''
goldTestForms=pd.melt(completeParadigmes[completeParadigmes["lexeme"].isin(listeTest)],id_vars=["lexeme"]).dropna()
goldTestForms["lexeme-case"]=goldTestForms["lexeme"]+"-"+goldTestForms["case"]
goldTestForms.drop(labels=["lexeme","case"],axis=1,inplace=True)
goldTestForms.set_index(["lexeme-case"],inplace=True)

'''Extraction des formes de références pertinentes'''
goldForms=goldTestForms.loc[~goldTestForms.index.isin(initialFormsIndex)]
goldFormsIndex=goldForms.index.tolist()

#paradigmes
#analyseCases
#lexeme=u"découper"
#paradigmes[paradigmes["lexeme"]==lexeme].columns[paradigmes[paradigmes["lexeme"]==lexeme].notnull().iloc[0]].tolist()
# # Lecture des règles

# In[32]:

with open(analysisPrefix+'-Regles.pkl', 'rb') as input:
    resultatsLecture = pickle.load(input)


# ### Comparer les cases analysées avec l'ensemble de toutes les cases

# In[33]:

analyseCases=list(set([case for (case,autre) in resultatsLecture.keys()]))
if sorted(analyseCases)!=sorted(goldCases):
    print ("Attention l'analyse ne comprend pas toutes les cases")
    print (sorted(analyseCases))
    print (sorted(goldCases))


# # Préparations pour la génération des formes

# In[34]:

class paradigmeDistribution:
    '''
    Gestion des distributions dans les cases du paradigme
    '''

    def __init__(self,lexeme):
        self.lexeme=lexeme
        self.formes={i:{} for i in analyseCases}

    def ajouterFormes(self,case,formes,coef=1.0):
        for forme in formes:
            if not forme in self.formes[case]:
                self.formes[case][forme]=0
            self.formes[case][forme]+=formes[forme]*coef

    def normaliserDistributions(self,caseListe=analyseCases):
        normalesDistributions={i:{} for i in caseListe}
        for case in caseListe:
            total=0
            for element in self.formes[case]:
                total+=self.formes[case][element]
            for element in self.formes[case]:
                normalesDistributions[case][element]=float(self.formes[case][element])/total
        return normalesDistributions



# In[35]:

def generateForms(lexeme,contextFree=False):
    candidats=paradigmeDistribution(lexeme)
    casesSamples=paradigmes[paradigmes["lexeme"]==lexeme].columns[paradigmes[paradigmes["lexeme"]==lexeme].notnull().iloc[0]].tolist()
    casesSamples.remove("lexeme")
    for caseDepart in casesSamples:
        formeDepart=paradigmes[paradigmes["lexeme"]==lexeme][caseDepart].iloc[0]
        if debug: print (caseDepart,formeDepart, file=logfile)
#        if formeDepart!="nan":
        for case in analyseCases:
            if debug: print (case, file=logfile)
            if not isinstance(resultatsLecture[(caseDepart, case)],str):
                if "," in formeDepart:
                    formesDepart=formeDepart.split(",")
                    coef=1.0/len(formesDepart)
                    for element in formesDepart:
                        candidats.ajouterFormes(case,resultatsLecture[(caseDepart, case)].sortirForme(element,contextFree),coef)
                else:
                    candidats.ajouterFormes(case,resultatsLecture[(caseDepart, case)].sortirForme(formeDepart,contextFree))
            else:
                if debug: print ("str", resultatsLecture[(caseDepart, case)], file=logfile)
    return candidats


# In[36]:

def ajouterPoint(lexeme,forme,case,digraphe,graphe):
    pointName="%s-%s-%s"%(lexeme,forme,case)
#    if not pointName in digraphe.nodes():
    tam=case[:2]
    if tam=="in": tam="inf"
    digraphe.add_node(pointName, tam='"%s"'%tam)
    graphe.add_node(pointName, tam='"%s"'%tam)
    return pointName

def ajouterFleche(pointDepart,pointSortie,coef,digraphe,graphe):
    digraphe.add_edge(pointDepart,pointSortie,weight=float(coef))
    if digraphe.has_edge(pointSortie,pointDepart):
        coefGraphe=float(digraphe.edge[pointSortie][pointDepart]["weight"]+coef)/2
        graphe.add_edge(pointDepart,pointSortie,weight=coefGraphe)


# In[37]:

def generateParadigms(generation1,genDigraphe=True,contextFree=False):
    lexeme=generation1.lexeme
    distributionInitiale=generation1.normaliserDistributions()
    candidats=paradigmeDistribution(lexeme)
    digraphe=nx.DiGraph()
    graphe=nx.Graph()
    for caseDepart in analyseCases:
        for formeDepart in distributionInitiale[caseDepart]:
            if formeDepart:
                pointDepart=ajouterPoint(lexeme,formeDepart,caseDepart,digraphe,graphe)
                coefDepart=distributionInitiale[caseDepart][formeDepart]
                if debug: print (caseDepart,formeDepart, file=logfile)
                for caseSortie in analyseCases:
                    distributionSortieBrute=resultatsLecture[(caseDepart, caseSortie)].sortirForme(formeDepart,contextFree)
                    if distributionSortieBrute:
                        if not genDigraphe:
#                            print ("brute",distributionSortieBrute)
                            distributionSortie={f:distributionSortieBrute[f] for f in distributionSortieBrute if f in distributionInitiale[caseSortie]}
                        else:
                            distributionSortie=distributionSortieBrute
#                        print ("filtre",distributionSortie)
#                        print (distributionInitiale[caseSortie])
                        if debug: print (caseSortie,distributionSortie,distributionInitiale[caseDepart], file=logfile)
                        candidats.ajouterFormes(caseSortie,distributionSortie,distributionInitiale[caseDepart][formeDepart])
                        for formeSortie in distributionSortie:
                            pointSortie=ajouterPoint(lexeme,formeSortie,caseSortie,digraphe,graphe)
                            coefSortie=distributionSortie[formeSortie]
                            ajouterFleche(pointDepart,pointSortie,float(coefDepart*coefSortie),digraphe,graphe)
    return (candidats,digraphe,graphe)


# # Génération d'un jeu de cliques

# In[38]:

def generate(lexeme,genDigraphe=True,contextFree=False):
#    print (lexeme,end=", ")
    generation1=generateForms(lexeme,contextFree)
#    print ("génération 2",end=", ")
    (generation2,lexDigraphe,lexGraphe)=generateParadigms(generation1,genDigraphe,contextFree)
    lexCliques=list(nx.algorithms.clique.find_cliques(lexGraphe))
#    print (lexCliques)
#    print ("génération 3")
    return (generation2,lexDigraphe,lexGraphe,lexCliques)


# In[39]:

paradigmes.dropna(thresh=1).count().sum()-paradigmes.dropna(thresh=1)["lexeme"].count()


# #### Calculer le score de la clique

# In[40]:

def cliqueScore(clique,graph):
    score=0
    if len(clique)>1:
        for (depart,arrivee) in it.combinations_with_replacement(clique,2):
            score+=graph[depart][arrivee]["weight"]
    return score


# In[41]:

def splitArrivee(arrivee):
    arriveeMorceaux=arrivee.split("-")
    if len(arriveeMorceaux)<3:
        print (arrivee,arriveeMorceaux)
    lexeme="-".join(arriveeMorceaux[:-2])
    formeArrivee=arriveeMorceaux[-2]
    caseArrivee=arriveeMorceaux[-1]
    return (lexeme,formeArrivee,caseArrivee)

# trouver tous les liens vers FS-* et FP-*
# regrouper par forme
# calculer les proportions
# renvoyer les proportions par forme
# avec le nombre de forme à l'appui
def formeScore(forme,graph):
    scores={}
    scoresNormes={}
    for depart in graph.edge:
        for arrivee in graph.edge[depart]:
            (lexeme, formeArrivee, caseArrivee)=splitArrivee(arrivee)
            if caseArrivee==forme:
#                print (depart, formeArrivee, graph.edge[depart][arrivee])
                if not formeArrivee in scores:
                    scores[formeArrivee]=0
                scores[formeArrivee]+=graph.edge[depart][arrivee]["weight"]
    totalArrivee=0
    for formeArrivee in scores:
        totalArrivee+=scores[formeArrivee]
    for formeArrivee in scores:
        scoresNormes[formeArrivee]=scores[formeArrivee]/totalArrivee
    return (scores,scoresNormes)



# ## Préparations pour SWIM

# In[42]:

def generateAnalysis(globDigraphe,globGraphe,contextFree=False):
    numClique=0
    #progressBar = FloatProgress(min=0, max=nbVerbes-1,description="Generation (%d verbs)"%nbVerbes)
    #display(progressBar)
    for i,element in enumerate(listeTest):
        cliquesScores[element]={}
        cliquesListes[element]={}
    #    if (i%100)==0: print (i, dateheure()[-4:], int(100*float(i)/nbVerbes), end=", ")
    #    progressBar.value=i
        #print (element)
        result=generate(element,genDigraphe,contextFree)
        (generation,lexDigraphe,lexGraphe,lexCliques)= result
    #    print (generation,lexDigraphe,lexGraphe,lexCliques)
        if genFormeVotes:
            formesScores[element]={}
            formesScoresNormes[element]={}
            for formeOutput in listeFormesOutput:
                (formesScores[element][formeOutput],formesScoresNormes[element][formeOutput])=formeScore(formeOutput,lexDigraphe)
        if genDigraphe:
            globDigraphe=nx.union(globDigraphe,lexDigraphe)
        if genGraphe:
            globGraphe=nx.union(globGraphe,lexGraphe)
        cliques.extend(lexCliques)
        for clique in lexCliques:
            cliquesScores[element][numClique]=cliqueScore(clique,lexGraphe)
            cliquesListes[element][numClique]=clique
            numClique+=1
    return globDigraphe,globGraphe,numClique


# In[43]:

def dictCliqueForms(clique):
    result={}
    for element in clique:
        lexeme,forme,case=splitArrivee(element)
        for c in dictMorphomeCases[case]:
            result[c]=forme
    return result

def dictPdRowForms(row):
    result={}
    for case in sampleCases:
        print (case,row[case].values[0])
    return result

def tableZero(case):
    if case in sampleCases:
        return u"Ø"
    else:
        return u"="

def makeTable(dictForms,title=""):
    tabular=[]
    labelTenseCode={"pi":"Present","ii":"Imperfective","ai":"Simple Past","fi":"Future",
                    "ps":"Subjunctive Pres.","is":"Subjunctive Imp.","pc":"Conditional","pI":"Imperative",
                    "inf":"Infinitive",
                    "ppMS":"Past Part. MS","ppMP":"Past Part. MP",
                    "ppFS":"Past Part. FS","ppMP":"Past Part. FP"
                   }
    def makeLine6(tenseCode):
        line=[]
        line.append(r"<th>%s</th>"%labelTenseCode[tenseCode])
        for person in [per+nb for nb in ["S","P"] for per in ["1","2","3"]]:
            case=tenseCode+person
            if (case in dictForms) and (not (type(dictForms[case]) == float and np.isnan(dictForms[case]))):
                line.append(r"<td>%s</td>"%(dictForms[case]))
            else:
                line.append(r"<td>%s</td>"%(tableZero(case)))
        return r"<tr>"+r"".join(line)+r"</tr>"

    def makeLine3(tenseCode):
        line=[]
        line.append(r"<th>%s</th>"%labelTenseCode[tenseCode])
        for person in [per+nb for nb in ["S","P"] for per in ["1","2","3"]]:
            if person in ["2S","1P","2P"]:
                case=tenseCode+person
                if case in dictForms and (not (type(dictForms[case]) == float and np.isnan(dictForms[case]))):
                    line.append(r"<td>%s</td>"%(dictForms[case]))
                else:
                    line.append(r"<td>%s</td>"%(tableZero(case)))
            else:
                line.append(r"<td>%s</td>"%(u"---"))
        return r"<tr>"+r"".join(line)+r"</tr>"

    def makeLineNF():
        line=[]
        line.append(r"<th>%s</th>"%"NF")
        for case in ["inf","pP","ppMS","ppMP","ppFS","ppFP"]:
            if case in dictForms and (not (type(dictForms[case]) == float and np.isnan(dictForms[case]))):
                line.append(r"<td>%s</td>"%(dictForms[case]))
            else:
                line.append(r"<td>%s</td>"%(tableZero(case)))
        return r"<tr>"+r"".join(line)+r"</tr>"


    top=[
        r"<table>",
        r"<caption style='caption-side:bottom;text-align:center'>",
        "Verbe : %s"%title,
        r"</caption>",
#        r"<tr><th/><th>1S</th><th>2S</th><th>3S</th><th>1P</th><th>2P</th><th>3P</th></tr>"
        r"<tr><th/><th>1SG</th><th>2SG</th><th>3SG</th><th>1PL</th><th>2PL</th><th>3PL</th></tr>"
        ]
    bottom=[
        r"</table>"
        ]
    tabular.append("\n".join(top))
    for tenseCode in ["pi","ii","fi","pc", "ps","ai", "is"]:
        tabular.append(makeLine6(tenseCode))
    tabular.append(makeLine3("pI"))
    tabular.append(makeLineNF())
    tabular.append("\n".join(bottom))
    return "\n".join(tabular)

def diffParadigme(lexeme):
    outLen=lexemeMaxCliques[lexeme][0]
    inLen=paradigmes[paradigmes["lexeme"]==lexeme].notnull().sum(axis=1).values[0]-1
    if outLen>inLen:
        print (lexemeMaxCliques[lexeme][1])
        print (paradigmes[paradigmes["lexeme"]=="grandir"].values)
    return outLen-inLen



# In[44]:

def checkFidelite(fidelite,clique):
    lFidele=False
    for element in clique:
        if fidelite in element:
            lFidele=True
    return lFidele

def generateCliques(contextFree=False):

    def bruteCliques(lexeme,maxCliqueSize=51):
        cliquesBrutes={n+1:0 for n in range(maxCliqueSize)}
        for l in cliquesListes[lexeme].values():
            longueur=len(l)
            if longueur>1:
                if not longueur in cliquesBrutes:
                    cliquesBrutes[longueur]=0
                cliquesBrutes[longueur]+=1
        return cliquesBrutes

    globDigraphe=nx.DiGraph()
    globGraphe=nx.Graph()

    globDigraphe,globGraphe,numClique=generateAnalysis(globDigraphe,globGraphe,contextFree)
    print

    lexemeMaxCliques={}
    lexemeParadigmes={}
    #progressBarCliques = FloatProgress(min=0, max=len(cliquesListes)-1,description="Analysis (%d verbes)"%len(cliquesListes))
    #display(progressBarCliques)
    for lexeme in cliquesListes:
        #progressBarCliques.value+=1
        maxLen=max([len(c) for c in cliquesListes[lexeme].values()])
        lexemeMaxCliques[lexeme]=bruteCliques(lexeme,maxLen)
        if details: print (lexeme,"Nombre de cliques",sum([v for k,v in lexemeMaxCliques[lexeme].iteritems()]))
        maxNbCliques=max([v for k,v in lexemeMaxCliques[lexeme].iteritems()])
        if plotDistributionCliques:
            ax=pd.DataFrame.from_dict(lexemeMaxCliques[lexeme],orient="index").plot(kind="bar",legend=False,grid=True,figsize=(10,3))
            ax.set(xlim=(0,maxLen+.5),ylim=(0,maxNbCliques+10))
            ax.set_xlabel("Clique Size in Cells",fontsize=16)
            ax.set_ylabel("Number of Cliques",fontsize=16)

        dictParadigmes=paradigmes.set_index("lexeme").to_dict(orient="index")

        cliquesFideles={}
        fidelites=[v+"-"+k for k,v in dictParadigmes[lexeme].iteritems() if isinstance(v,unicode)]
        for l in cliquesListes[lexeme].values():
            longueur=len(l)
            if longueur>1:
                fidele=True
                for fidelite in fidelites:
                    if "," in fidelite:
                        fideliteForme,fideliteCase=fidelite.split("-")
                        fideliteFormes=fideliteForme.split(",")
                        fideliteItems=[fideliteF+"-"+fideliteCase for fideliteF in fideliteFormes]
#                        print (fideliteItems)
                        lFidele=True
                        for f in fideliteItems:
                            lFidele=lFidele & checkFidelite(f,l)
                    else:
                        lFidele=checkFidelite(fidelite,l)
                    if not lFidele:
                        fidele=False
                        break
                if fidele:
                    if not longueur in cliquesFideles:
                        cliquesFideles[longueur]=[]
                    cliquesFideles[longueur].append(l)
#                else:
#                    if lexeme==u"bégayer": print ()
#        print ([(k,len(v)) for k,v in cliquesFideles.iteritems()])
        if cliquesFideles:
            maxCliquesCard=max([k for k,v in cliquesFideles.iteritems()])
    #        print (maxCliquesCard)
    #        print (cliquesScores[lexeme])
    #        print (cliquesListes[lexeme])
            lexemeParadigmes[lexeme]=[]
            maxScoreCliques=max([clique for cliqueNumber, clique in cliquesScores[lexeme].items()])
            maxCardScoreNums=[numC for numC, c in cliquesListes[lexeme].items() if c in cliquesFideles[maxCliquesCard]]
            maxCardScore=max([scoreC for numC, scoreC in cliquesScores[lexeme].items() if numC in maxCardScoreNums])
    #        print ("max score among all cliques:",maxScoreCliques)
            if details: print ("max score among faithfull cliques of %d forms:"%maxCliquesCard,maxCardScore)
            for c in cliquesFideles[maxCliquesCard]:
                cNumber=[cliqueNumber for cliqueNumber, clique in cliquesListes[lexeme].items() if clique == c]
                if len(cNumber)!=1:
                    print ("TOO MANY SCORES PROBLEM WITH CLIQUE", cNumber)
    #            print ("Liste n°",cNumber[0],cliquesScores[lexeme][cNumber[0]])
    #            print (sorted(cliquesScores[lexeme].items(), key=operator.itemgetter(1)))
    #            display(HTML(makeTable(dictCliqueForms(c),title=c[0].split("-")[0])))
    #            print (cliquesScores[lexeme][cNumber[0]], maxCardScore)
                if cliquesScores[lexeme][cNumber[0]]==maxCardScore:
                    lexemeParadigmes[lexeme].append(c)
        else:
            lexemeParadigmes[lexeme]=[[lexeme+"-"+f for f in fidelites]]
            if details: print (u"no new faithfull clique, the previous one contained %d forms"%len(lexemeParadigmes[lexeme][0]))
    return lexemeParadigmes


# In[45]:

def cutNodeName(nodeName):
    items=nodeName.split("-")
    nbItems=len(items)
    if nbItems>3:
        items=["-".join(items[0:nbItems-2]),items[-2],items[-1]]
    return items

def filledOutClique(cliques):
    if cliques:
        result=[]
        for clique in cliques:
#            print (clique)
            fullClique=[]
            for element in clique:
                if debug: print ("element",element)
                lexeme,forme,case=splitArrivee(element)
                for c in dictMorphomeCases[case]:
                    fullClique.append("-".join([lexeme,forme,c]))
            result.append(fullClique)
        return result
    else:
        return cliques


# In[46]:

def extendParadigmes(contextParadigmes,extendMorphomes=False):
    lexemesParadigmeListe=[]
    for lexeme in contextParadigmes:
        if extendMorphomes:
            lexParadigmes=filledOutClique(contextParadigmes[lexeme])
        else:
            lexParadigmes=contextParadigmes[lexeme]
        if len(lexParadigmes)!=1:
            if debug:
                print ("LEXEME WITH A NON UNIQUE PARADIGM PB",len(lexParadigmes),lexeme)
                print (lexParadigmes)
        lexParadigme=lexParadigmes[0]
        for lexForme in lexParadigme:
            lexemesParadigmeListe.append(cutNodeName(lexForme))
    newForms=pd.DataFrame(lexemesParadigmeListe)
    newForms.columns=["lexeme","form","case"]
#    newParadigmes=newForms.pivot(index="lexeme", columns="case", values="form")
    newParadigmes=pd.pivot_table(newForms, values='form', index=['lexeme'], columns=['case'], aggfunc=lambda x: ",".join(x)).reset_index().reindex()
    for i in newParadigmes.itertuples():
#        print (i[0],i[1])
        lexeme=i[1]
        lexemeIndexes=paradigmes.lexeme[paradigmes.lexeme==lexeme].index.tolist()
        if lexemeIndexes:
            lexemeIndex=lexemeIndexes[0]
        else:
            print (i,lexeme,lexemeIndexes)
        newParadigmes.loc[newParadigmes.lexeme==lexeme,"index"]=int(lexemeIndex)
    newParadigmes.set_index("index",inplace=True)
    return paradigmes.combine_first(newParadigmes)


# In[47]:

def countSplits(dfForms):
    dfForms.loc[:,"split"]=dfForms.loc[:,"value"].str.split(",")
    return dfForms["split"].str.len().sum()

def calculerResultats(contextParadigmes,extension="-Swim2"):

    '''Préparer le paradigme des prédictions'''
    brutParadigmes=extendParadigmes(contextParadigmes,extendMorphomes=False)
    finalParadigmes=extendParadigmes(contextParadigmes,extendMorphomes=True)
    finalParadigmes.to_csv(path_or_buf=analysisPrefix+"-paradigmes%s.csv"%extension,encoding="utf8",sep=";")
    finalTestForms=pd.melt(finalParadigmes[finalParadigmes["lexeme"].isin(listeTest)],id_vars=["lexeme"]).dropna()
    finalTestForms["lexeme-case"]=finalTestForms["lexeme"]+"-"+finalTestForms["variable"]
    finalTestForms.drop(labels=["lexeme","variable"],axis=1,inplace=True)
    finalTestForms.set_index(["lexeme-case"],inplace=True)

    '''Soustraire les formes initiales'''
    finalForms=finalTestForms.loc[~finalTestForms.index.isin(initialFormsIndex)]
    finalFormsIndex=finalForms.index.tolist()

    '''Calculer les sur/sous-générations'''
    underGeneration=goldForms.loc[~goldForms.index.isin(finalFormsIndex)]
    overGeneration=finalForms.loc[~finalForms.index.isin(goldFormsIndex)]

    '''Réduire les prédictions et la référence aux cases communes'''
    predictedForms=finalForms.loc[finalForms.index.isin(goldFormsIndex)]
    actualForms=goldForms.loc[goldForms.index.isin(finalFormsIndex)]

    '''Créer un tableau pour les comparaisons'''
    compareForms=predictedForms.copy()
    compareForms.loc[:,"right"]=actualForms.loc[:,"value"]

    '''Séparer les cases identiques des cases différentes'''
    sameForms=compareForms[compareForms["value"]==compareForms["right"]]
    diffForms=compareForms[compareForms["value"]!=compareForms["right"]]


    '''Sauvegarder les comparatifs'''
    overGeneration.to_csv(path_or_buf=analysisPrefix+"-overGeneration%s.csv"%extension,encoding="utf8")
    underGeneration.to_csv(path_or_buf=analysisPrefix+"-underGeneration%s.csv"%extension,encoding="utf8")
    sameForms.to_csv(path_or_buf=analysisPrefix+"-sameForms%s.csv"%extension,encoding="utf8")
    diffForms.to_csv(path_or_buf=analysisPrefix+"-diffForms%s.csv"%extension,encoding="utf8")


    '''Transformer les surabondances en liste'''
    diffForms.loc[:,"split-value"]=diffForms.loc[:,"value"].str.split(",")
    diffForms.loc[:,"split-right"]=diffForms.loc[:,"right"].str.split(",")

    '''Transformer les surabondances en set()'''
    diffForms.loc[:,"split-value"]=diffForms.loc[:,"split-value"].apply(set)
    diffForms.loc[:,"split-right"]=diffForms.loc[:,"split-right"].apply(set)

    '''Calculer le nombre de formes (y compris surabondances)'''
    nbValues=diffForms["split-value"].str.len().sum()
    nbRights=diffForms["split-right"].str.len().sum()

    '''Calculer les identités et les inclusions'''
    nbIdenticalSets=diffForms[diffForms["split-value"]==diffForms["split-right"]]["split-value"].str.len().sum()
    nbIncludedSets=diffForms[diffForms["split-value"]<diffForms["split-right"]]["split-value"].str.len().sum()
    nbWrongForms=(nbValues-nbIdenticalSets-nbIncludedSets)
    underBonus=(nbRights-nbIdenticalSets-nbIncludedSets)

    UG=countSplits(underGeneration)+underBonus
    OG=countSplits(overGeneration)
    TP=countSplits(sameForms)+nbIdenticalSets+nbIncludedSets
    FP=nbWrongForms
    resultCharacteristics=(UG,OG,TP,FP)
    recall=float(TP)/(UG+TP+FP)
    precision=float(TP)/(OG+TP+FP)
    fMeasure=2*recall*precision/(recall+precision)
    resultMeasures=(precision,recall,fMeasure)
    print (sampleNumero,sampleType,casesType)
    print ("UG",UG ,"OG",OG,"TP",TP,"FP",FP)
    print ("recall", recall, "precision", precision)
    print (fMeasure)
    return (brutParadigmes,finalParadigmes,resultCharacteristics,resultMeasures)


# # SWIM1

# In[48]:

cliques=[]
cliquesScores={}
cliquesListes={}

formesScores={}
formesScoresNormes={}

print (datetime.datetime.now())
#get_ipython().magic(u'time
swim1ContextParadigmes=generateCliques()
#')


# In[49]:

newParadigmes,paradigmesSwim1,characteristicsSwim1,measuresSwim1=calculerResultats(swim1ContextParadigmes,"-Swim1")
#get_ipython().magic(u'ding')
ding()

# # SWIM2

# ## Préparation des paradigmes

# In[ ]:

paradigmesOriginaux=paradigmes.copy()
paradigmesSample=paradigmesOriginaux[paradigmesOriginaux["lexeme"].isin(listeTest)]


# In[ ]:

paradigmes=newParadigmes.copy()
paradigmesColumns=paradigmes.columns.tolist()
for c in sampleCases:
    if not c in paradigmesColumns:
        print (c)
        paradigmes[c]=np.NaN


# In[ ]:

cliques=[]
cliquesScores={}
cliquesListes={}

formesScores={}
formesScoresNormes={}

print (datetime.datetime.now())
#get_ipython().magic(u'time
swim2ContextParadigmes=generateCliques(contextFree=True)
#')


# In[ ]:

newParadigmes,paradigmesSwim2,characteristicsSwim2,measuresSwim2=calculerResultats(swim2ContextParadigmes,"-Swim2")


# In[ ]:

nomFichierResultats=filePrefix+"-X-Resultats.yaml"
if os.path.isfile(nomFichierResultats):
    with open(nomFichierResultats, 'r') as stream:
            resultats=yaml.load(stream)
else:
    resultats={}

if casesType:
    sampleExt=casesType
else:
    sampleExt=sampleType
sampleId=sampleNumber.strip("-")+sampleExt
resultats[sampleId]={}
resultats[sampleId]["Swim1"]={}
resultats[sampleId]["Swim1"]["UG"]=characteristicsSwim1[0]
resultats[sampleId]["Swim1"]["OG"]=characteristicsSwim1[1]
resultats[sampleId]["Swim1"]["TP"]=characteristicsSwim1[2]
resultats[sampleId]["Swim1"]["FP"]=characteristicsSwim1[3]
resultats[sampleId]["Swim1"]["Precision"]=measuresSwim1[0]
resultats[sampleId]["Swim1"]["Recall"]=measuresSwim1[1]
resultats[sampleId]["Swim1"]["F-Measure"]=measuresSwim1[2]
resultats[sampleId]["Swim2"]={}
resultats[sampleId]["Swim2"]["UG"]=characteristicsSwim2[0]
resultats[sampleId]["Swim2"]["OG"]=characteristicsSwim2[1]
resultats[sampleId]["Swim2"]["TP"]=characteristicsSwim2[2]
resultats[sampleId]["Swim2"]["FP"]=characteristicsSwim2[3]
resultats[sampleId]["Swim2"]["Precision"]=measuresSwim2[0]
resultats[sampleId]["Swim2"]["Recall"]=measuresSwim2[1]
resultats[sampleId]["Swim2"]["F-Measure"]=measuresSwim2[2]

yaml.safe_dump(resultats, file(nomFichierResultats, 'w'), encoding='utf-8', allow_unicode=True)


# In[ ]:

#get_ipython().magic(u'ding')
#get_ipython().magic(u'ding')
ding()
ding()

# In[ ]:

print ("Sample",sampleNumber.strip("-"))
print ("Swim1",characteristicsSwim1,measuresSwim1)
print ("Swim2",characteristicsSwim2,measuresSwim2)


# # Fin du traitement
cliques=[]
