#SWIM
===
A tentative implementation of Small World Inflectional Morphology

===
##Training
- Prepare a lexicon with phonological transcriptions and frequencies
 - Synchronize frequencies from Lexique.org
 - Remove duplicates
- Get a training sample
 - Choose a sample size
 - Make the corresponding paradigm table
  - Beware of orthographical and L23 duplicates
  - Allow for overabundance
- Neutralize symbols according to a map
 - Index training samples with a serial and a map reference
- Calculate the analogies and the classifications based on the training sample
- Calculate the complete paradigms for the verbs in the training sample

===
##Testing
- Make a test sample for verbs excluded from the training sample
- Calculate the complete paradigms for the verbs in the test sample
