# coding: utf-8

# In[18]:

# get_ipython().magic(u'matplotlib inline')


# ###Importation des modules

# In[19]:

import networkx as nx
# import matplotlib.pyplot as plt
import PDM
from PDM import *
import pickle
import sys

# In[20]:

PDM.seuilDistribution=0.00


# In[21]:

with open('Regles.pkl', 'rb') as input:
    PDM.analyse = pickle.load(input)
with open('Classes.pkl', 'rb') as input:
    PDM.classification = pickle.load(input)


# In[22]:

prs1=Case("prs.1")
prs1.addForm(FormeCoef("balE",3.0))
#prs1.addForm(FormeCoef("balEj",1.0))
pst1=Case("pst.1")
pst1.addForm(FormeCoef("fini",1.0))
inf=Case("inf")
inf.addForm(FormeCoef("balEjE",1.0))
prspcp=Case("prs.pcp")
prspcp.addForm(FormeCoef("finisâ",1.0))


# In[23]:

lexical=Paradigme()
#lexical.addEntrees(inf,prs1,pst1)
lexical.addEntrees(prs1,inf)
#lexical.addEntrees(prs1,pst1)
#lexical.addEntrees(prs1,prspcp)
lexical.calculerParadigme()


# In[24]:

cliques=list(nx.algorithms.clique.find_cliques(lexical.graphe))
print len(cliques)
for clique in sorted(cliques,key=lambda x: len(x),reverse=True):
    print (len(clique),clique)
    print ()
    total=0
    for node in sorted(clique):
        poids=lexical.graphe.node[node]["weight"]
        total+=poids
        print(node,poids)
    print (total/len(clique))
    print ()

sys.exit()
# In[25]:

nx.write_dot(lexical.graphe,"graphe.dot")
nx.write_dot(lexical.digraphe,"digraphe.dot")


# In[32]:

for n in range(len(cliques)):
    print (n)
    digraphe=lexical.digraphe.subgraph(cliques[n])
    nx.write_dot(digraphe,"clique%d.dot"%n)


# verbe=Paradigme()
# verbe.entrees=lexical.nouveau
# verbe.calculerParadigme()

# In[28]:

lexical.getCoefNewForm("ipf.1","finisE")


# In[29]:

lexical.digraphe.node["ipf.1-finisE"]


# In[30]:

lexical.intermediaires["ipf.1"]


# In[31]:

lexical.nouveau["ipf.1"]


# In[31]:



