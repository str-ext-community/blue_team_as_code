import logging
import sys
import os
import pathlib
import yaml
import argparse

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        style="{",
        fmt="[{name}] {levelname} - {message}"
    )
)

log = logging.getLogger("cab2elastalert")
log.setLevel(logging.INFO)
log.addHandler(handler)

class Cab2ElastAlertError(Exception):
    pass

def searchByUUID(uuid, a2bdir):
    result = None
    for r, d, f in os.walk(a2bdir):
        for file in f:
            if file.endswith(".yml"):
                try:
                    with open(os.path.join(r, file), 'r') as stream:
                        detection = yaml.safe_load(stream)                                
                    if detection.get("uuid") == uuid or detection.get("id") == uuid:
                        result = os.path.join(r, file)                    
                except Exception as e:
                    log.debug(e)
                    raise Cab2ElastAlertError(e)
            if result:
                return result
    return False 

def createCorrelation(cab_obj, stages, outputdir):
    tmp = []
    for s in stages:
        tmp.append(f"detection_name:\"{s}\"")
    stages_query = " OR ".join(tmp)
    

    detection = {
        "name": cab_obj["title"],
        "match_enhancements":  ["elastalert_modules.fixmapping.FixMappingEnhancement"],
        "type": "cardinality",
        "cardinality_field": "match_body.elastalert_correlation_username",
        "max_cardinality": len(stages) - 1,
        "index": "elastalert_status",
        "timeframe": {cab_obj['stages'][-1]["stageTimeUnit"] : cab_obj['stages'][-1]["stagetimediff"] },
        "filter": [
            {
                "query": {
                    "query_string": {
                        "query": f"(({stages_query}) AND alert_sent:true)"
                    }
                }
            }
        ],
        "alert" : [
            "email"
        ],
        "email": "demo@elastalert.local"

    }

    with open(pathlib.Path.joinpath(outputdir, cab_obj['uuid'] + ".yml"), 'w') as outfile:
        yaml.dump(detection, outfile, default_flow_style=False, width=10000, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(
        description="CAB2ElastAlertconverter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--sigmadir", "-s", required=True, help="sigma directory")
    parser.add_argument("--a2bdir", "-a", required=True, help="a2b directory")
    parser.add_argument("--mapping", "-m", required=True, help="sigma mapping")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--outputdir", default="./output/", type=str, help="default output directory for elastalert detection")

    parser.add_argument("cabs", nargs="*", help="CAB input file")

    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    if len(args.cabs) == 0:
        log.info("Nothing to do!")
        parser.print_usage()
        sys.exit(0)

    if not pathlib.Path(args.mapping).is_file():
        log.info("mapping not found: [%s]" % args.mapping)
        sys.exit(0)

    if not pathlib.Path(args.a2bdir).is_dir():
        log.info("a2bdir not found: [%s]" % args.a2bdir)
        sys.exit(0)
    
    if not pathlib.Path(args.sigmadir).is_dir():
        log.info("sigmadir not found: [%s]" % args.sigmadir)
        sys.exit(0)
    
    if not pathlib.Path(args.outputdir).is_dir():
        log.info("outputdir not found: [%s]" % args.outputdir)
        sys.exit(0)
    
    #add sigma dir to path
    sys.path.insert(0, args.sigmadir+'tools/')
    from elastalert import ElastAlertBackend

    for cab in args.cabs:
        if not pathlib.Path(cab).is_file():
            log.info("CAB not found: [%s]" % args.cab)
            sys.exit(0)
    
        cab_file = pathlib.Path(cab)
        with open(cab_file, 'r') as stream:
            try:
                cab_obj = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                log.debug(e)
                raise Cab2ElastAlertError(e)

        stages = []
        for stage in cab_obj['stages']:
            a2b_uuid = stage['policy_uuid']
            a2b_file = searchByUUID(a2b_uuid, args.a2bdir)
            
            if not a2b_file:
                log.error("A2B with uuid: %s not found in %s" % (a2b_uuid, args.a2bdir))
                sys.exit(0)

            backend = ElastAlertBackend(args.mapping, outputdir = pathlib.Path(args.outputdir))
            stages.append(backend.convert(a2b_file))

        createCorrelation(cab_obj, stages, pathlib.Path(args.outputdir))
  
    # time = datetime.now().strftime("%Y_%m_%d_%H%M%S")
if __name__ == '__main__':
    main()
