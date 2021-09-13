# CAB2ElastAlert | A STR CAB converter for Securonix CABs#

This is PoC of CAB to ElastAlert converter.

## Use ##
### Install ###
Prerequisites:
~~~~
python3 -m pip install -r requirements.txt
~~~~

### Run ###
~~~~
usage: CAB2ElastAlert [-h] --sigmadir SIGMADIR --a2bdir A2BDIR --mapping MAPPING [--verbose] [--outputdir OUTPUTDIR] [cabs [cabs ...]]
~~~~
Example:
~~~~
python3 CAB2ElastAlert --sigmadir ~/sigma/ --a2bdir ../input  --outputdir ../output  --mapping ../../../str-omega/config/mapping.yml  ../input/model-CAB-L12.yml
~~~~
