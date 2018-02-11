
# coding: utf-8

# In[258]:

import pandas as pd
import glob,re,pickle,os,yaml,datetime,sys


# In[259]:

debut=datetime.datetime.now()
filePrefix="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/Longitudinales/"
sampleFiles=glob.glob(filePrefix+"Longitudinal*.csv")


# In[260]:

def prefixEchantillon(numero):
    candidats=[]
    for sample in sampleFiles:
        m=re.match(ur"^.*/(Longitudinal-%s-T\d+-F\d+)%s-paradigmes\.csv"%(numero,casesType),sample)
        if m:
            candidats.append(m.group(1))
    if len(candidats)==1:
        return candidats[0]
    else:
        print "PB pas de nom unique correspondant",candidats


# In[261]:

arguments=sys.argv
if len(arguments)>1:
    numeroEchantillon=arguments[1]
    if len(arguments)>2:
        sampleType=arguments[2]
        if len(arguments)>3:
            casesType=arguments[3]
            if len(arguments)>4:
                etapeSwim=arguments[4]
            else:
                etapeSwim="-Swim1"
        else:
            casesType="-Morphomes"
            etapeSwim="-Swim1"
    else:
        sampleType="-X"
        casesType="-Morphomes"
        etapeSwim="-Swim1"
else:
    numeroEchantillon="00"
    sampleType="-X"
    casesType="-Morphomes"
    etapeSwim="-Swim1"

samplePrefix=prefixEchantillon(numeroEchantillon)
initialFile=filePrefix+samplePrefix+"-X-paradigmes.csv"
analysisPrefix=filePrefix+samplePrefix+casesType
predictionsFile=analysisPrefix+"-paradigmes%s.csv"%etapeSwim
print "Nom du fichier prédictions",predictionsFile
referenceFile="/Volumes/gilles/Transfert/Copies-iMac-GB/2015-Data/MGC-171229-Verbes3.pkl"


# ## Réglages de la variante phonologique

# In[262]:

phonologicalMap=sampleType.strip("-")
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


# In[263]:

def recoder(chaine,table=neutralise):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    else:
        result=chaine
    return result


# In[264]:

dierese={"j":"ij", "w":"uw","H":"yH","i":"ij","u":"uw","y":"yH"}


# In[265]:

def checkFrench(prononciation):
    if prononciation:
        result=recoder(prononciation)
        m=re.match(ur"^.*([^ieèEaOouy926êôâ])[jwH]$",result)
        if m:
            print "pb avec un glide final", prononciation
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


# ## Formes de l'échantillon

# In[266]:

initialParadigmes=pd.read_csv(initialFile,sep=";",encoding="utf8")
del initialParadigmes[u"Unnamed: 0"]
initialParadigmes=initialParadigmes.dropna(axis=1,how='all')
initialParadigmesColumns=initialParadigmes.columns.tolist()
listeLexemes=initialParadigmes["lexeme"].tolist()
nbLexemes=len(listeLexemes)

# In[267]:

initialForms=pd.melt(initialParadigmes[initialParadigmes["lexeme"].isin(listeLexemes)],id_vars=["lexeme"]).dropna()
initialForms["lexeme-case"]=initialForms["lexeme"]+"-"+initialForms["variable"]
initialForms.drop(labels=["lexeme","variable"],axis=1,inplace=True)
initialForms.set_index(["lexeme-case"],inplace=True)
initialFormsIndex=initialForms.index.tolist()


# ## Formes de l'échantillon avec les prédictions

# In[268]:

predictedParadigmes=pd.read_csv(predictionsFile,sep=";",encoding="utf8")
del predictedParadigmes[u"Unnamed: 0"]
predictedParadigmes=predictedParadigmes.loc[:,predictedParadigmes.columns.isin(initialParadigmesColumns)].dropna(axis=1,how='all')
if listeLexemes!=predictedParadigmes["lexeme"].tolist():
    print "PB avec la liste des lexèmes prédits"
if set(initialParadigmesColumns)!=set(predictedParadigmes.columns.tolist()):
    print "PB avec la liste des cases prédites"
    print predictedParadigmes.columns.tolist()
    print initialParadigmesColumns


# In[269]:

predictedForms=pd.melt(predictedParadigmes[predictedParadigmes["lexeme"].isin(listeLexemes)],id_vars=["lexeme"]).dropna()
predictedForms["lexeme-case"]=predictedForms["lexeme"]+"-"+predictedForms["variable"]
predictedForms.drop(labels=["lexeme","variable"],axis=1,inplace=True)
predictedForms.set_index(["lexeme-case"],inplace=True)
predictedFormsIndex=predictedForms.index.tolist()


# ## Formes de référence

# In[270]:

with open(referenceFile,"rb") as input:
    lexiqueGold=pickle.load(input)

'''Rectifications phonologiques'''
lexiqueGold["phono"]=lexiqueGold["phono"].apply(lambda x: checkFrench(x))
completeParadigmes=pd.pivot_table(lexiqueGold, values='phono', index=['lexeme'], columns=['case'], aggfunc=lambda x: ",".join(x)).reset_index().reindex()

'''Identification des cases présentes initialement'''
completeParadigmes=completeParadigmes.loc[:,completeParadigmes.columns.isin(initialParadigmesColumns)]

'''Mise en liste des formes de références'''
goldTestForms=pd.melt(completeParadigmes[completeParadigmes["lexeme"].isin(listeLexemes)],id_vars=["lexeme"]).dropna()
goldTestForms["lexeme-case"]=goldTestForms["lexeme"]+"-"+goldTestForms["case"]
goldTestForms.drop(labels=["lexeme","case"],axis=1,inplace=True)
goldTestForms.set_index(["lexeme-case"],inplace=True)

'''Extraction des formes de références pertinentes'''
goldForms=goldTestForms.loc[~goldTestForms.index.isin(initialFormsIndex)]
goldFormsIndex=goldForms.index.tolist()


# In[271]:

def countSplits(dfForms):
    dfForms.loc[:,"split"]=dfForms.loc[:,"value"].str.split(",")
    return dfForms["split"].str.len().sum()


# In[272]:

'''Soustraire les formes initiales des prédictions'''
finalForms=predictedForms.loc[~predictedForms.index.isin(initialFormsIndex)]
finalFormsIndex=finalForms.index.tolist()


# In[273]:

nbInitialForms=countSplits(initialForms)
nbGoldForms=countSplits(goldForms)
print nbGoldForms, "formes à prédire à partir de",nbInitialForms,"formes de",nbLexemes,"lexèmes"


# In[274]:

'''Calculer les sur/sous-générations'''
underGeneration=goldForms.loc[~goldForms.index.isin(finalFormsIndex)]
overGeneration=finalForms.loc[~finalForms.index.isin(goldFormsIndex)]
print "Sous-générations :",countSplits(underGeneration),"Sur-générations :",countSplits(overGeneration)


# In[275]:

'''Réduire les prédictions et la référence aux cases communes'''
compareForms=finalForms.loc[finalForms.index.isin(goldFormsIndex)].copy()
actualForms=goldForms.loc[goldForms.index.isin(finalFormsIndex)]
len(compareForms),len(actualForms)


# In[276]:

'''Créer un tableau pour les comparaisons'''
compareForms.loc[:,"right"]=actualForms.loc[:,"value"]
countSplits(compareForms)


# In[277]:

'''Séparer les cases identiques des cases différentes'''
sameForms=compareForms[compareForms["value"]==compareForms["right"]]
diffForms=compareForms[compareForms["value"]!=compareForms["right"]]


# In[278]:

print "Formes identiques",countSplits(sameForms)
print "Formes potentiellement différentes",countSplits(diffForms)


# In[279]:

'''Sauvegarder les comparatifs'''
overGeneration.to_csv(path_or_buf=analysisPrefix+"-overGeneration%s.csv"%etapeSwim,encoding="utf8")
underGeneration.to_csv(path_or_buf=analysisPrefix+"-underGeneration%s.csv"%etapeSwim,encoding="utf8")
sameForms.to_csv(path_or_buf=analysisPrefix+"-sameForms%s.csv"%etapeSwim,encoding="utf8")
diffForms.to_csv(path_or_buf=analysisPrefix+"-diffForms%s.csv"%etapeSwim,encoding="utf8")



# In[280]:

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


# In[281]:

UG=countSplits(underGeneration)+underBonus
OG=countSplits(overGeneration)
TP=countSplits(sameForms)+nbIdenticalSets+nbIncludedSets
FP=nbWrongForms
resultCharacteristics=(UG,OG,TP,FP)
recall=float(TP)/(UG+TP)
precision=float(TP)/(OG+TP+FP)
fMeasure=2*recall*precision/(recall+precision)
resultMeasures=(precision,recall,fMeasure)
print "UG :",UG ,"OG :",OG,"TP :",TP,"FP :",FP
print "recall :", recall, "precision :", precision
print "fMeasure :",fMeasure


# In[282]:

nomFichierResultats=filePrefix+"Longitudinal-X-Resultats-Recalcul.yaml"
if os.path.isfile(nomFichierResultats):
    with open(nomFichierResultats, 'r') as stream:
        resultats=yaml.load(stream)
        if not resultats:
            resultats={}
else:
    resultats={}

if casesType:
    sampleExt=casesType
else:
    sampleExt=sampleType
sampleId=samplePrefix.strip("Longitudinal").strip("-")+sampleExt
#print resultats


# In[283]:

if not sampleId in resultats:
    resultats[sampleId]={}

etape=etapeSwim.strip("-")
resultats[sampleId][etape]={}
resultats[sampleId][etape]["nbGoldForms"]=nbGoldForms
resultats[sampleId][etape]["nbInitialForms"]=nbInitialForms
resultats[sampleId][etape]["nbLexemes"]=nbLexemes
resultats[sampleId][etape]["UG"]=UG
resultats[sampleId][etape]["OG"]=OG
resultats[sampleId][etape]["TP"]=TP
resultats[sampleId][etape]["FP"]=FP
resultats[sampleId][etape]["Precision"]=precision
resultats[sampleId][etape]["Recall"]=recall
resultats[sampleId][etape]["F-Measure"]=fMeasure

yaml.safe_dump(resultats, file(nomFichierResultats, 'w'), encoding='utf-8', allow_unicode=True)


# In[284]:

fin=datetime.datetime.now()
print debut
print fin
print numeroEchantillon,sampleType,casesType,etapeSwim
