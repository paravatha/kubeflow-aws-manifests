export AWS_PROFILE=kubeflow
export CLUSTER_NAME=kubeflow
export CLUSTER_REGION=us-east-1
export KUBEFLOW_RELEASE_VERSION=v1.7.0
export AWS_RELEASE_VERSION=v1.7.0-aws-b1.0.2
export AWS_ACCOUNT=744774087552

git clone https://github.com/awslabs/kubeflow-manifests.git && cd kubeflow-manifests
git checkout ${AWS_RELEASE_VERSION}
git clone --branch ${KUBEFLOW_RELEASE_VERSION} https://github.com/kubeflow/manifests.git upstream
make install-tools

eksctl create cluster --name ${CLUSTER_NAME} --version 1.25 \
  --region ${CLUSTER_REGION} --nodegroup-name linux-nodes \
  --node-type t3.medium --nodes 0 --nodes-min 0 --nodes-max 5 \
  --managed --with-oidc
