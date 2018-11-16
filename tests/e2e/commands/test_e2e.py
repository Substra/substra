import json
import os
from subprocess import PIPE, Popen as popen
from unittest import TestCase, mock

from substra.commands import Config

url = 'http://owkin.substrabac:8000'


class TestFixtures(TestCase):
    def setUp(self):
        Config({
            '<url>': url,
            '<version>': '0.0',
            '<user>': os.environ.get('BACK_AUTH_USER', ''),
            '<password>': os.environ.get('BACK_AUTH_PASSWORD', ''),
            '--config': '/tmp/.substra_e2e'
        }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra_e2e')
        except:
            pass

    def test_add_fixtures(self):
        # register dataset
        data = json.dumps({
            "name": "ISIC 2018",
            "data_opener": "./tests/assets/fixtures/chunantes/datasets/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener.py",
            "type": "Images",
            "description": "./tests/assets/fixtures/chunantes/datasets/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description.md",
            "permissions": "all",
            "challenge_keys": []
        })

        output = popen(['substra', 'add', 'dataset', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {
                "pkhash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                "name": "ISIC 2018",
                "data_opener": "%s/media/datasets/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener.py" % url,
                "description": "%s/media/datasets/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description.md" % url,
                "validated": True
            })

        # readd it
        output = popen(['substra', 'add', 'dataset', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        self.assertTrue(json.loads(res) == {"message": "A dataset with this opener file already exists."})

        # register train data
        data = json.dumps({
            "file": "./tests/assets/fixtures/chunantes/data/62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a/0024700.zip",
            "dataset_key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
            "test_only": False,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        print(res)

        self.assertTrue(
            json.loads(res) == {"pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                "validated": True,
                                "file": "%s/media/data/62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a/0024700.zip" % url})

        # register train data
        data = json.dumps({
            "file": "./tests/assets/fixtures/chunantes/data/42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9/0024899.zip",
            "dataset_key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
            "test_only": False,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9",
                                "validated": True,
                                "file": "%s/media/data/42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9/0024899.zip" % url})

        ###############################

        # register second dataset
        data = json.dumps({
            "name": "Simplified ISIC 2018",
            "data_opener": "./tests/assets/fixtures/owkin/datasets/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/opener.py",
            "type": "Images",
            "description": "./tests/assets/fixtures/owkin/datasets/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/description.md",
            "permissions": "all",
            "challenge_keys": []
        })

        output = popen(['substra', 'add', 'dataset', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {
                "pkhash": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
                "name": "Simplified ISIC 2018",
                "data_opener": "%s/media/datasets/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/opener.py" % url,
                "description": "%s/media/datasets/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/description.md" % url,
                "validated": True
            })

        #########################

        # register test data
        data = json.dumps({
            "file": "./tests/assets/fixtures/owkin/data/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024900.zip",
            "dataset_key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "test_only": True,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1",
                                "validated": True,
                                "file": "%s/media/data/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024900.zip" % url})

        # register test data
        data = json.dumps({
            "file": "./tests/assets/fixtures/owkin/data/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip",
            "dataset_key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "test_only": True,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010",
                                "validated": True,
                                "file": "%s/media/data/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip" % url})

        #########################

        # register test data
        data = json.dumps({
            "file": "./tests/assets/fixtures/owkin/data/93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060/0024317.zip",
            "dataset_key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "test_only": True,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060",
                                "validated": True,
                                "file": "%s/media/data/93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060/0024317.zip" % url})

        # register test data
        data = json.dumps({
            "file": "./tests/assets/fixtures/owkin/data/eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb/0024316.zip",
            "dataset_key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "test_only": True,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb",
                                "validated": True,
                                "file": "%s/media/data/eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb/0024316.zip" % url})

        #########################

        # register test data
        data = json.dumps({
            "file": "./tests/assets/fixtures/owkin/data/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip",
            "dataset_key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "test_only": True,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                                "validated": True,
                                "file": "%s/media/data/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip" % url})

        # register test data
        data = json.dumps({
            "file": "./tests/assets/fixtures/owkin/data/533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1/0024318.zip",
            "dataset_key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "test_only": True,
        })

        output = popen(['substra', 'add', 'data', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(
            json.loads(res) == {"pkhash": "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1",
                                "validated": True,
                                "file": "%s/media/data/533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1/0024318.zip" % url})

        # #########################

        # register challenge
        data = json.dumps({
            "name": "Simplified skin lesion classification",
            "description": "./tests/assets/fixtures/owkin/challenges/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description.md",
            "metrics_name": "macro-average recall",
            "metrics": "./tests/assets/fixtures/owkin/challenges/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics.py",
            "permissions": "all",
            "test_data_keys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                               "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"]
        })

        output = popen(['substra', 'add', 'challenge', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['pkhash'] == '6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c')
        self.assertTrue(res['validated'] == True)
        self.assertTrue(res['description'] == '%s/media/challenges/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description.md' % url)
        self.assertTrue(res['metrics'] == '%s/media/challenges/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics.py' % url)


        # register challenge
        data = json.dumps({
            "name": "Skin Lesion Classification Challenge",
            "description": "./tests/assets/fixtures/chunantes/challenges/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description.md",
            "metrics_name": "macro-average recall",
            "metrics": "./tests/assets/fixtures/chunantes/challenges/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics.py",
            "permissions": "all",
            "test_data_keys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]
        })

        output = popen(['substra', 'add', 'challenge', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['pkhash'] == 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f')
        self.assertTrue(res['validated'] == True)
        self.assertTrue(res['description'] == '%s/media/challenges/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description.md' % url)
        self.assertTrue(res['metrics'] == '%s/media/challenges/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics.py' % url)

        ############################

        # register algo
        data = json.dumps({
            "name": "Logistic regression",
            "file": "./tests/assets/fixtures/chunantes/algos/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/algo.tar.gz",
            "description": "./tests/assets/fixtures/chunantes/algos/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/description.md",
            "challenge_key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
            "permissions": "all",
        })

        output = popen(['substra', 'add', 'algo', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['pkhash'] == '6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f')
        self.assertTrue(res['validated'] == True)
        self.assertTrue(res['description'] == '%s/media/algos/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/description.md' % url)
        self.assertTrue(res['file'] == '%s/media/algos/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/algo.tar.gz' % url)

        # register second algo on challenge Simplified skin lesion classification
        data = json.dumps({
            "name": "Logistic regression for balanced problem",
            "file": "./tests/assets/fixtures/chunantes/algos/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/algo.tar.gz",
            "description": "./tests/assets/fixtures/chunantes/algos/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description.md",
            "challenge_key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
            "permissions": "all",
        })

        output = popen(['substra', 'add', 'algo', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['pkhash'] == '7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0')
        self.assertTrue(res['validated'] == True)
        self.assertTrue(res['description'] == '%s/media/algos/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description.md' % url)
        self.assertTrue(res['file'] == '%s/media/algos/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/algo.tar.gz' % url)

        # register third algo
        data = json.dumps({
            "name": "Neural Network",
            "file": "./tests/assets/fixtures/chunantes/algos/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/algo.tar.gz",
            "description": "./tests/assets/fixtures/chunantes/algos/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/description.md",
            "challenge_key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
            "permissions": "all",
        })

        output = popen(['substra', 'add', 'algo', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['pkhash'] == '0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f')
        self.assertTrue(res['validated'] == True)
        self.assertTrue(res['description'] == '%s/media/algos/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/description.md' % url)
        self.assertTrue(res['file'] == '%s/media/algos/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/algo.tar.gz' % url)

        # register fourth algo
        data = json.dumps({
            "name": "Random Forest",
            "file": "./tests/assets/fixtures/chunantes/algos/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/algo.tar.gz",
            "description": "./tests/assets/fixtures/chunantes/algos/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/description.md",
            "challenge_key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
            "permissions": "all",
        })

        output = popen(['substra', 'add', 'algo', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['pkhash'] == 'f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284')
        self.assertTrue(res['validated'] == True)
        self.assertTrue(res['description'] == '%s/media/algos/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/description.md' % url)
        self.assertTrue(res['file'] == '%s/media/algos/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/algo.tar.gz' % url)

        ####################################

        # create traintuple
        data = json.dumps({
            "algo_key": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
            "model_key": "",
            "train_data_keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a","42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"]
        })

        output = popen(['substra', 'add', 'traintuple', data, '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        res = json.loads(res)

        self.assertTrue('pkhash' in res)
