
# coding: utf-8

# ## Importations
# - codecs pour les encodages
# - pandas et numpy pour les calculs sur tableaux
# - matplotlib pour les graphiques
# - itertools pour les itérateurs sophistiqués (paires sur liste, ...)

# In[593]:

from __future__ import print_function

import codecs,glob,sys
# import cellbell
import features
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import pickle
#%pylab inline
#pd.options.display.mpl_style = 'default'
debug=False


# In[594]:

#from ipywidgets import FloatProgress
#from IPython.display import display


# In[595]:

numeroEchantillon="55"
phonologicalMap="-X"
casesType="-X-Morphomes"
#casesType=""
timeStamp=""


# In[596]:

filePrefix="/Users/gilles/Box Sync/2015-Data/MGC-170330"
filePrefix="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/Longitudinales/"
sampleFiles=glob.glob(filePrefix+"Longitudinal*.pkl")

arguments=sys.argv
if len(arguments)>1:
    numeroEchantillon=arguments[1]
    if len(arguments)>2:
        casesType=arguments[2]
        if len(arguments)>3:
            phonologicalMap=arguments[3]
        else:
            phonologicalMap="-X"
    else:
        casesType=""
        phonologicalMap="-X"
else:
    sys.exit()
# In[597]:

def prefixEchantillon(numero):
    candidats=[]
    for sample in sampleFiles:
        m=re.match(ur"^.*/(Longitudinal-%s-T\d+-F\d+)%s\.pkl"%(numero,casesType),sample)
        if m:
            print (sample)
            print (m.group(1))
            candidats.append(m.group(1))
    if len(candidats)==1:
        return candidats[0]
    else:
        print ("PB trop de noms correspondants")


# In[598]:

#echantillonPrefix="-09-20000Ko"
echantillonPrefix=prefixEchantillon(numeroEchantillon)
#echantillonPrefix
if casesType.startswith(phonologicalMap):
    prefixSortie=filePrefix+echantillonPrefix+casesType
else:
    prefixSortie=filePrefix+echantillonPrefix+phonologicalMap+casesType
prefixSortie


# In[599]:

import math
def rAn(r,n):
    f = math.factorial
    return f(n) / f(n-r)
def rCn(r,n):
    f = math.factorial
    return f(n) / f(r) / f(n-r)


# ### Préparation des matrices de traits

# In[600]:

features.add_config('bdlexique.ini')
fs=features.FeatureSystem('phonemes')


# In[601]:

validPhonemes=list(fs.supremum.concept.extent)
#for phoneme in validPhonemes:
#    print (phoneme, [phoneme], ";")


# In[602]:

neutralisationsNORD=(u"6û",u"9ê")
neutralisationsSUD=(u"e2o",u"E9O")
if phonologicalMap=="-N":
    neutralisations=neutralisationsNORD
elif phonologicalMap=="-S":
    neutralisations=neutralisationsSUD
else:
    neutralisations=(u"",u"")
    phonologicalMap=("-X")
bdlexiqueIn = unicode(u"èò"+neutralisations[0])
bdlexiqueNum = [ord(char) for char in bdlexiqueIn]
neutreOut = unicode(u"EO"+neutralisations[1])
neutralise = dict(zip(bdlexiqueNum, neutreOut))


# In[603]:

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

# In[604]:

dierese={"j":"ij", "w":"uw","H":"yH","i":"ij","u":"uw","y":"yH"}


# In[605]:

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
    else:
        result=prononciation
    return result


# In[606]:

checkFrench("trwera")


# # Lecture du tableau de VERBES

# ### Lecture du lexique
# - nomLexique pour le fichier
# - names pour les noms de colonnes
# - élimination des lignes dupliquées éventuelles (p.e. dépendre)

# In[607]:

def lireLexique(nomLexique):
    with open(nomLexique, 'rb') as input:
        lexique=pickle.load(input)
    return lexique


# In[608]:

def pivotLexique(lexique,debug=False):
    paradigmes=pd.pivot_table(lexique[lexique["tir1"]>0], values='phono', index=['lexeme'], columns=['case'], aggfunc=lambda x: ",".join(x)).reset_index().reindex()
    return paradigmes


# In[609]:

nomLexique=filePrefix+echantillonPrefix+"-Tirage"+phonologicalMap+timeStamp+casesType+".pkl"
nomLexique=filePrefix+echantillonPrefix+timeStamp+casesType+".pkl"
lexique=lireLexique(nomLexique)
paradigmes=pivotLexique(lexique)


# In[610]:

if debug:
    logfile_name=filePrefix+echantillonPrefix+phonologicalMap+casesType+".log"
    logfile = codecs.open(logfile_name,mode='w',encoding="utf8")


# In[611]:

casesPrincipales= [
        'inf', 'pi1S', 'pi2S', 'pi3S', 'pi1P', 'pi2P', 'pi3P', 'ii1S',
        'ii2S', 'ii3S', 'ii1P', 'ii2P', 'ii3P',
        'fi1S', 'fi2S', 'fi3S', 'fi1P', 'fi2P',
        'fi3P', 'pI2S', 'pI1P', 'pI2P', 'ps1S', 'ps2S', 'ps3S', 'ps1P',
        'ps2P', 'ps3P',
        'pc1S', 'pc2S', 'pc3S', 'pc1P', 'pc2P', 'pc3P', 'pP',
        'ppMS', 'ppMP', 'ppFS', 'ppFP'
            ]
casesSecondaires= [
       'ai1S', 'ai2S', 'ai3S', 'ai1P', 'ai2P', 'ai3P', 'is1S', 'is2S', 'is3S', 'is1P', 'is2P', 'is3P'
            ]
casesTotales=casesPrincipales+casesSecondaires
listeCases=casesTotales


# ### Suppression de la colonne index inutile

# In[612]:

if u"Unnamed: 0" in paradigmes:
    del paradigmes[u"Unnamed: 0"]


# In[613]:

sampleCases=paradigmes.columns.tolist()
sampleCases.remove(u"lexeme")


# ### Application de la neutralisation phonologique et stockage des paradigmes neutralisés correspondants

# In[614]:

#Neutralize all the forms
for case in sampleCases:
#    print (case)
#    paradigmes[case]=paradigmes[case].apply(lambda x: recoder(x))
    paradigmes[case]=paradigmes[case].apply(lambda x: checkFrench(x))


# In[615]:

#Save neutralized paradigms
paradigmes.to_csv(path_or_buf=prefixSortie+"-paradigmes.csv",encoding="utf8",sep=";")


# # Préparation du calcul des analogies

# ### Calcul de la différence entre deux formes

# In[616]:

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

# In[617]:

def rowDiff(row, patrons):
    result=diff(row[0],row[1])
    if not result in patrons:
        patrons[result]=(formesPatron(),formesPatron())
    patrons[result][0].ajouterFormes(row[0])
    patrons[result][1].ajouterFormes(row[1])
    return (result[0],result[1])


# ### Transformation d'un patron en RegExp

# In[618]:

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

# In[619]:

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


# In[620]:

class formesPatron:
    '''
    Accumulateur de formes correspondant à un patron pour calcul de la Généralisation Minimale (cf. MGL)
    '''
    def __init__(self):
        self.formes=[]

#    def __repr__(self):
#        return ','.join(self.calculerGM())

    def ajouterForme(self,forme):
        self.formes.append(forme)

    def calculerGM(self):
        minLongueur=len(min(self.formes, key=len))
        maxLongueur=len(max(self.formes, key=len))
        if debug: print (minLongueur, maxLongueur, file=logfile)
        positions=[]
        if maxLongueur>minLongueur:
            positions.append("*")
        for i in xrange(minLongueur, 0, -1):
            phonemes=set([x[-i] for x in self.formes])
            if debug: print (phonemes, file=logfile)
            if "." in phonemes:
                positions.append(".")
            else:
                positions.append("".join(fs.lattice[phonemes].extent))
        return patron2regexp(positions)

class pairePatrons:
    '''
    Accumulateur de triplets (f1,f2,patron) correspondant à une paire pour calcul des Généralisations Minimales (cf. MGL)
    '''
    def __init__(self,case1,case2):
        self.patrons1={}
        self.patrons2={}
        self.case1=case1
        self.case2=case2

#    def __repr__(self):
#        return ','.join(self.calculerGM())

    def ajouterFormes(self,forme1,forme2,patron):
#        print (forme1,forme2,patron, file=logfile)
        patron12=patron
        (pat1,pat2)=patron.split("-")
        patron21=pat2+"-"+pat1
#        print (patron12,patron21, file=logfile)
        if not patron12 in self.patrons1:
            self.patrons1[patron12]=formesPatron()
        self.patrons1[patron12].ajouterForme(forme1)
        if not patron21 in self.patrons2:
            self.patrons2[patron21]=formesPatron()
        self.patrons2[patron21].ajouterForme(forme2)


    def calculerGM(self):
        resultat1={}
        for patron in self.patrons1:
            if debug: print ("patron1", patron, file=logfile)
            resultat1[patron]=self.patrons1[patron].calculerGM()
        resultat2={}
        for patron in self.patrons2:
            if debug: print ("patron2", patron, file=logfile)
            resultat2[patron]=self.patrons2[patron].calculerGM()
        return (resultat1,resultat2)


# # Classe pour la gestion des patrons, des classes et des transformations

# In[621]:

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

# In[622]:

def OLDrapports(paradigme):
    (case1,case2,lexeme)= paradigme.columns.values.tolist()
    patrons=pairePatrons(case1,case2)
    if len(paradigme)>0:
#        for index, row in paradigme.iterrows():
#            patrons.ajouterFormes(row[0],row[1],diff(row[0],row[1]))
        paradigme.apply(lambda x: patrons.ajouterFormes(x[case1],x[case2],diff(x[case1],x[case2])), axis=1)
        (regles1,regles2)=patrons.calculerGM()
    return patrons.calculerGM()


# In[623]:

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

# In[624]:

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


# ## Calculer les rapports entre formes pour chaque paire
#
# >on fait la liste des cases de *paradigmes*
#
# >pour chaque paire du tableau principal
#
# >>si la paire fait partie des cases de *paradigmes*
#
# >>>on calcule le rapport
#
# >>sinon
#
# >>>on signale que qu'une des cases n'est pas représentée

# In[625]:

def evaluerEchantillon(paradigmes):
    result={}
    colonnes=paradigmes.columns.values.tolist()
    for n,paire in enumerate(it.combinations_with_replacement(sampleCases,2)):
#        progressBar.value=n
        if n%10==0: print (".",end="")
        if debug: print (paire, file=logfile)
        if debug: print ("-".join(paire),end=", ")
        paireListe=list(paire)
        paireListe.append("lexeme")
        if paire[0] in colonnes and paire[1] in colonnes:
            paradigmePaire=paradigmes[paireListe].dropna(thresh=3, axis=0).reindex()
            if paire[0]==paire[1]:
                paireListe[1]="TEMP"
                paradigmePaire.columns=paireListe
            paradigmePaire=splitCellMates(splitCellMates(paradigmePaire,paireListe[0]),paireListe[1])
            result[paire]=rapports(paradigmePaire)
        else:
            result[paire]=("missing pair", paire)
    return result


# ### Boucle de calcul des analogies pour l'échantillon

# In[626]:

#get_ipython().run_cell_magic(u'time', u'', u'\nprogressBar = FloatProgress(min=0, max=rCn(2,len(sampleCases)), description="Analogies (%d pairs)"%rCn(2,len(sampleCases)))\ndisplay(progressBar)\n
debug=False
debug1=True
resultats=evaluerEchantillon(paradigmes)


# In[627]:

classesFinales={}
for resultat in resultats:
    classesFinales[resultat]=resultats[resultat][0]
    classesFinales[(resultat[1],resultat[0])]=resultats[resultat][1]


# In[628]:

if casesType.startswith(phonologicalMap):
    nomRegles=filePrefix+echantillonPrefix+casesType+'-Regles.pkl'
else:
    nomRegles=filePrefix+echantillonPrefix+phonologicalMap+casesType+'-Regles.pkl'

with open(nomRegles, 'wb') as output:
   pickle.dump(classesFinales, output, pickle.HIGHEST_PROTOCOL)
