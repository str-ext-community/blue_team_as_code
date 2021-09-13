from elastalert.enhancements import BaseEnhancement

class CreateCorrelationField(BaseEnhancement):
    def process(self, match):
        match['elastalert_correlation_username'] = "%s_%s" % (self.rule['name'], match['host_name'])