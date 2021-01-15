#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test case for merging tables
"""
import os
import unittest

# relative imports, from CLI and from parent project
if __name__ != "__main__":
    from .tools import TmpDirTestCase, run_cwl, write_table
    from .settings import CWL_DIR

if __name__ == "__main__":
    from tools import TmpDirTestCase, run_cwl, write_table
    from settings import CWL_DIR

cwl_file = os.path.join(CWL_DIR, 'merge-tables.cwl')

class TestMergeTables(TmpDirTestCase):
    def test_merge_tables1(self):
        lines1 = [
        ['#SAMPLE_ID', 'PATIENT_ID', 'SAMPLE_COVERAGE'],
        ['#SAMPLE_ID', 'PATIENT_ID', 'SAMPLE_COVERAGE'],
        ['#STRING', 'STRING', 'NUMBER',],
        ['#1', '1', '1'],
        ['SAMPLE_ID', 'PATIENT_ID', 'SAMPLE_COVERAGE'],
        ['Sample1-T', 'Patient1', '108'],
        ['Sample1-N', 'Patient2', '58'],
        ['Sample2-T', 'Patient3', '502'],
        ['Sample2-N', 'Patient4', '56'],
        ]

        lines2 = [
        ['SampleID', 'TMB'],
        ['Sample1-T', '100'],
        ['Sample2-T', '200'],
        ]
        data_clinical_file = write_table(self.tmpdir, filename = "data_clinical_sample.txt", lines = lines1)
        tmb_file = write_table(self.tmpdir, filename = "tmb.tsv", lines = lines2)
        input_json = {
            'table1': {
                "class": "File",
                "path": data_clinical_file
            },
            'table2': {
                "class": "File",
                "path": tmb_file
            },
            'key1': 'SAMPLE_ID',
            'key2': 'SampleID',
            'output_filename': 'output.tsv'
        }
        output_json, output_dir = run_cwl(
            testcase = self,
            tmpdir = self.tmpdir,
            input_json = input_json,
            cwl_file = cwl_file,
            print_command = False,
            )

        expected_output = {
            'output_file': {
                'location': 'file://' + os.path.join(output_dir,'output.tsv'),
                'basename': 'output.tsv',
                'class': 'File',
                'checksum': 'sha1$9480f53914b2eba6839f5837e8629e028b132fe4',
                'size': 251,
                'path':  os.path.join(output_dir,'output.tsv')
                }
            }
        self.assertDictEqual(output_json, expected_output)

        output_file = expected_output['output_file']['path']
        with open(output_file) as fin:
            lines = [ l.strip().split() for l in fin ]
        expected_lines = [
            ['#SAMPLE_ID', 'PATIENT_ID', 'SAMPLE_COVERAGE'],
            ['#SAMPLE_ID', 'PATIENT_ID', 'SAMPLE_COVERAGE'],
            ['#STRING', 'STRING', 'NUMBER'],
            ['#1', '1', '1'],
            ['SAMPLE_ID', 'PATIENT_ID', 'SAMPLE_COVERAGE', 'TMB'],
            ['Sample1-T', 'Patient1', '108', '100'],
            ['Sample1-N', 'Patient2', '58'], # tailing empty value gets stripped off
            ['Sample2-T', 'Patient3', '502', '200'],
            ['Sample2-N', 'Patient4', '56'] # tailing empty value gets stripped off
            ]
        self.assertEqual(lines, expected_lines)

if __name__ == "__main__":
    unittest.main()
