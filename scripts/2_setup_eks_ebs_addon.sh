export AWS_PROFILE=kubeflow
export CLUSTER_NAME=kubeflow
export CLUSTER_REGION=us-east-1
export KUBEFLOW_RELEASE_VERSION=v1.7.0
export AWS_RELEASE_VERSION=v1.7.0-aws-b1.0.2
export AWS_ACCOUNT=744774087552

eksctl create iamserviceaccount \
    --name ebs-csi-controller-sa \
    --namespace kube-system \
    --cluster ${CLUSTER_NAME} \
    --role-name AmazonEKS_EBS_CSI_DriverRole \
    --role-only \
    --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
    --approve
eksctl create addon --name aws-ebs-csi-driver --cluster ${CLUSTER_NAME} --service-account-role-arn arn:aws:iam::${AWS_ACCOUNT}:role/AmazonEKS_EBS_CSI_DriverRole --force
eksctl scale nodegroup --cluster=${CLUSTER_NAME} --nodes=4 linux-nodes --wait
