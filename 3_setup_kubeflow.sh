export AWS_PROFILE=kubeflow
export CLUSTER_NAME=kubeflow
export CLUSTER_REGION=us-east-1
export KUBEFLOW_RELEASE_VERSION=v1.7.0
export AWS_RELEASE_VERSION=v1.7.0-aws-b1.0.2
export AWS_ACCOUNT=744774087552

make deploy-kubeflow INSTALLATION_OPTION=kustomize DEPLOYMENT_OPTION=vanilla

cd tests/e2e
python3.8 -m pip install -r requirements.txt
# update tests/e2e/utils/load_balancer/config.yaml
PYTHONPATH=.. python3.8 utils/load_balancer/setup_load_balancer.py

# https://github.com/kubeflow/manifests/blob/master/README.md#port-forward
# https://github.com/kubeflow/manifests/blob/master/README.md#change-default-user-password

DELETE
# Check if there any external IP svc
kubectl get svc --all-namespaces
eksctl delete cluster --name kf-test
