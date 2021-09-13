import yaml
from sigma.config.collection import SigmaConfigurationManager
from sigma.configuration import SigmaConfiguration, SigmaConfigurationChain
from sigma.parser.collection import SigmaCollectionParser
from sigma.backends.elasticsearch import ElastalertBackendQs
import pathlib 

class ElastAlertBackend(ElastalertBackendQs):
    def __init__(self, *args, **kwargs):
        mapping, = args
        self.timestamp_field = kwargs.get("timestamp_field", "etl_processed_time")
        self.outputdir = kwargs['outputdir']
        with open(mapping, 'r') as stream:
          self.sigmaconfigs = SigmaConfiguration(configyaml=stream)
        super().__init__(self.sigmaconfigs, {})

    def convert(self, a2b_file):
        with open(a2b_file, 'r') as stream:
            parser = SigmaCollectionParser(stream, self.sigmaconfigs, None)

        with open(a2b_file, 'r') as stream:   
            a2b_obj = yaml.safe_load(stream)

        if "uuid" in a2b_obj:
            a2b_obj['id'] =  a2b_obj['uuid']

        uuid = a2b_obj.get('uuid', a2b_obj.get('id'))

        parser.generate(self)
        result = self.finalize()
        #upate fields

        result['description'] = a2b_obj['tldr']
        result['timestamp_field'] = self.timestamp_field
        result['index'] = "logs-endpoint-winevent-sysmon-*"
        result['match_enhancements'] = ["elastalert_modules.correlation_field.CreateCorrelationField"]

        with open(pathlib.Path.joinpath(self.outputdir, uuid + ".yml"), 'w') as outfile:
            yaml.dump(result, outfile, default_flow_style=False, width=10000)
        return result['name']

    def finalize(self):
        # yaml.dump(detection, default_flow_style=False, width=10000)
        for detection_name, detection in self.elastalert_alerts.items():
            return detection