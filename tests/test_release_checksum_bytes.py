import hashlib,importlib.util,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checksum_writer',ROOT/'scripts/write-release-checksums.py');writer=importlib.util.module_from_spec(spec);spec.loader.exec_module(writer)

class ReleaseChecksumBytes(unittest.TestCase):
 def test_binary_output_is_lf_only_and_matches_exact_assets(self):
  with tempfile.TemporaryDirectory()as d:
   root=pathlib.Path(d);(root/'host.zip').write_bytes(b'fixture\r\narchive');(root/'install.sh').write_bytes(b'#!/bin/sh\n')
   self.assertEqual(writer.write_checksums(root),2)
   raw=(root/'SHA256SUMS').read_bytes();self.assertNotIn(b'\r',raw);self.assertTrue(raw.endswith(b'\n'))
   self.assertEqual(raw.decode().splitlines()[0],hashlib.sha256(b'fixture\r\narchive').hexdigest()+'  host.zip')
 def test_signed_release_is_never_rewritten(self):
  with tempfile.TemporaryDirectory()as d:
   root=pathlib.Path(d);(root/'install.sh').write_bytes(b'fixture');(root/'SHA256SUMS').write_bytes(b'preserve');(root/'release-manifest.sig').write_bytes(b'signed')
   with self.assertRaises(ValueError):writer.write_checksums(root)
   self.assertEqual((root/'SHA256SUMS').read_bytes(),b'preserve')
