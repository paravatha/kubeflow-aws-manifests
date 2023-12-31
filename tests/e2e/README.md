
## Usage

Install dependencies
```
python3
kustomize 
eksctl
kubectl

awscli # configure your default credentials

# install python dependencies
pip install -r requirements.txt
```

Run a specific test.
Region is a required parameter for all tests. Each test suite/test class may require additional set of parameters. e.g. test_sanity needs only `--region` but cognito test needs `--root-domain-name` and `--root-domain-hosted-zone-id` and rds-s3 tests need `--accesskey` and `--secretkey` in addition to region. 

`--installation_option`(default=kustomize) and `--deployment_option`(default=vanilla) need to be specified depending on test to run. 
```
pytest <tests/test_file.py> -k <test_name(s)> --region <REGION_NAME> --installation_option <helm/kustomize> --deployment_option <vanilla/cognito/rds-s3>
```

Tests do not delete eks cluster by default. If you wish to delete cluster after test is finished:
```
pytest --deletecluster ...<other arguments>...
```

Run without deleting successfully created resources. Useful for re-running failed tests.
```
pytest --keepsuccess ...<other arguments>...
```

Resume from a previous run using the resources that were previous created
```
pytest --metadata .metadata/metadata-1638939746471968000.json --keepsuccess ...<other arguments>...
```

## Test specific commands

### Terraform

Vanilla
```
pytest tests/terraform/test_vanilla.py -s -q --region <aws region>
```

RDS-S3
```
pytest tests/terraform/test_rds_s3.py -s -q --region <aws region> --accesskey <accesskey> --secretkey <secretkey>
```

Cognito
```
pytest tests/terraform/test_cognito.py -s -q --region <aws region> --root-domain-name <root domain, e.g. example.com>
```

Cognito-RDS-S3
```
pytest tests/terraform/test_cognito_rds_s3.py -s -q --region <aws region> --root-domain-name <root domain, e.g. example.com> --accesskey <accesskey> --secretkey <secretkey>
```


### About metadata
When using the helper method `configure_resource_fixture` a metadata file is generated with the following output:
```
# Using cluster as an example

Saved key: cluster_name value: e2e-test-cluster-507uvuyhca in metadata file /Users/rkharse/kf-e2e-tests/e2e/.metadata/metadata-1639087995874492000
```

Metadata can also be manually be output to a file by calling `Metadata#to_file` on a metadata object
