# in Cloud 9
aws configure --profile=kubeflow
# us-east-1
# json
aws sts get-caller-identity

export AWS_PROFILE=kubeflow
export CLUSTER_NAME=kube-test
export CLUSTER_REGION=us-east-1
eksctl create cluster --name ${CLUSTER_NAME} --version 1.25 --region ${CLUSTER_REGION} --nodegroup-name linux-nodes --node-type t3.medium --nodes 5 --nodes-min 5 --nodes-max 3 --managed --with-oidc

#eksctl get addon --name aws-ebs-csi-driver --cluster ${CLUSTER_NAME}
#kubectl describe daemonset aws-node --namespace kube-system | grep amazon-k8s-cni: | cut -d : -f 3
## add EBS and VPC add-ons
## grant EBS permissions to nodegroups

export KUBEFLOW_RELEASE_VERSION=v1.7.0
export AWS_RELEASE_VERSION=v1.7.0-aws-b1.0.2
#git clone https://github.com/awslabs/kubeflow-manifests.git && cd kubeflow-manifests
#git checkout ${AWS_RELEASE_VERSION}
#git clone --branch ${KUBEFLOW_RELEASE_VERSION} https://github.com/kubeflow/manifests.git upstream
git clone https://github.com/paravatha/kubeflow-test-manifests
cd kubeflow-test-manifests
make install-tools
make deploy-kubeflow INSTALLATION_OPTION=kustomize DEPLOYMENT_OPTION=vanilla

cd tests/e2e
python3.8 -m pip install -r requirements.txt
# update tests/e2e/utils/load_balancer/config.yaml
PYTHONPATH=.. python3.8 utils/load_balancer/setup_load_balancer.py

DELETE
# Check if there any external IP svc
kubectl get svc --all-namespaces
eksctl delete cluster --name kf-test
