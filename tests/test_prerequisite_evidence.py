"""The operator evidence collector must remain read-only and cannot grant approval."""
import importlib.util,json,pathlib,subprocess,unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prerequisite_evidence',ROOT/'scripts/collect-prerequisite-evidence.py')
collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)

class PrerequisiteEvidence(unittest.TestCase):
    def test_only_narrow_read_commands_and_no_implicit_approval(self):
        observed=[]
        def run(argv,**options):
            observed.append(argv)
            self.assertEqual(options['timeout'],12)
            self.assertNotIn('shell',options)
            return subprocess.CompletedProcess(argv,0,'rootless fixture','not shared')
        with patch.object(collector.shutil,'which',return_value=None),patch.object(collector.subprocess,'run',side_effect=run):
            result=collector.collect()
        self.assertTrue(result['readOnly']);self.assertFalse(result['securityApproval'])
        self.assertTrue(result['vulnerabilityReviewRequired'])
        self.assertEqual(observed,[['docker','--version'],['docker','version','--format','{{.Server.Version}}'],['docker','compose','version','--short'],['docker','info','--format','{{json .SecurityOptions}}']])
        self.assertNotIn('not shared',json.dumps(result))

    def test_unavailable_or_timed_out_tools_are_not_clearance(self):
        for error in (FileNotFoundError(),subprocess.TimeoutExpired('docker',12)):
            with patch.object(collector.shutil,'which',return_value=None),patch.object(collector.subprocess,'run',side_effect=error):
                result=collector.collect()
            self.assertFalse(result['securityApproval'])
            for key in ('dockerClient','dockerServer','compose','securityOptions'):
                self.assertEqual(result[key],{'available':False,'value':None})
