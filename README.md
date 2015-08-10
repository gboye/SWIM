#SWIM
A tentative implementation of Small World Inflectional Morphology

##Preparing
- Prepare a bdlexique with phonological transcriptions and frequencies
 - Synchronize frequencies from Lexique.org
 - Remove duplicates
 - Transform frequencies into probabilities
 - Save the lexicon in CSV form
- Prepare the GOLD paradigms
 - Make complete paradigms in CSV form
   - with overabundance
   - with defectiveness
 - Calculate the analogies and the classifications based on the GOLD paradigms
   - with all phonological maps
   - store in pandas form

##Training
- Get a training sample
 - Choose a sample size
 - Make the corresponding paradigm table
  - Beware of orthographical and L23 duplicates
  - Allow for overabundance
- Neutralize symbols according to a map
 - Index training samples with a serial and a map reference
- Calculate the analogies and the classifications based on the training sample

##Testing
- Calculate the complete paradigms for the verbs in the training sample
- Make a test sample for verbs excluded from the training sample
- Calculate the complete paradigms for the verbs in the test sample

##Evaluating
- Identify the patterns that were not obtained in the training sample
- Measure the distance between the patterns obtained from the training sample and the complete paradigms
- Measure the distance between the classification obtained from the training sample and the complete paradigms
