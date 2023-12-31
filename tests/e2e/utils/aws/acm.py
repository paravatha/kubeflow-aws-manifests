# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import boto3
import logging
import time

from botocore.exceptions import ClientError, WaiterError
from .route53 import Route53HostedZone
from typing import Any

logger = logging.getLogger(__name__)


class AcmCertificate:
    """
    Encapsulates ACM functions.
    """

    def __init__(
        self,
        domain: str = None,
        subject_alternative_names: list = None,
        hosted_zone: Route53HostedZone = None,
        region: str = "us-east-1",
        acm_client: Any = None,
        arn: str = None,
    ):
        self.domain = domain
        self.subject_alternative_names = subject_alternative_names
        self.hosted_zone = hosted_zone
        self.region = region
        self.acm_client = acm_client or boto3.client("acm", region_name=region)
        self.arn = arn
        if not domain and not arn:
            raise ValueError("Either domain or arn should be defined")

    def request_validation(self, validation_method="DNS") -> str:
        """
        Starts a validation request that results in a new certificate being issued
        by ACM. DNS validation requires that you add CNAME records to your DNS
        provider. Email validation sends email to a list of email addresses that
        are associated with the domain.

        For more information, see _Issuing and managing certificates_ in the ACM
        user guide.
            https://docs.aws.amazon.com/acm/latest/userguide/gs.html

        :param validation_method: The validation method, either DNS or EMAIL.

        :return: The ARN of the requested certificate.
        """
        try:
            args = {
                'DomainName': self.domain,
                'ValidationMethod': validation_method,
            }
            if self.subject_alternative_names is not None:
                args['SubjectAlternativeNames'] = self.subject_alternative_names

            response = self.acm_client.request_certificate(**args)
       
            
        except ClientError:
            logger.exception(
                f"failed to request validation of certificate for {self.domain} in {self.region}"
            )
            raise
        else:
            self.arn = response["CertificateArn"]
            logger.info(
                f"requested {validation_method} validation for domain {self.domain}. \
                certificate ARN is {self.arn}."
            )
            return self.arn

    def describe(self) -> dict:
        """
        Gets certificate metadata

        :return: Metadata about the certificate.
        """
        try:
            response = self.acm_client.describe_certificate(CertificateArn=self.arn)
        except ClientError:
            logger.exception(f"failed to describe certificate {self.arn}")
            raise
        else:
            certificate = response["Certificate"]
            return certificate

    def wait_for_certificate_validation(
        self, wait_periods: int = 20, period_length: int = 30
    ):
        waiter = self.acm_client.get_waiter("certificate_validated")
        logger.info(f"{self.arn}: waiting for validation ...")
        try:
            waiter.wait(
                CertificateArn=self.arn,
                WaiterConfig={"Delay": period_length, "MaxAttempts": wait_periods},
            )
        except WaiterError:
            logger.exception(f"timed out waiting for validation: {self.arn}")

    def get_domain_validation_record_detail(self, wait_periods: int = 6, period_length: int = 15) -> list:
        validation_options = self.describe().get("DomainValidationOptions")
        for _ in range(wait_periods):
            if validation_options is not None:
                resource_record = validation_options[0].get("ResourceRecord", None)
                if resource_record is not None:
                    break
            time.sleep(period_length)
            validation_options = self.describe().get("DomainValidationOptions")
        else:
            raise Exception(
                f"timed out waiting for resource record for: {self.arn}"
            )

        resource_records = []
        for option in validation_options:
            resource_records.append(option.get("ResourceRecord"))
        return resource_records
    

    def generate_domain_validation_record(self) -> list:
        logger.info(f"{self.arn}: waiting for domain validation record ...")
        record_detail = self.get_domain_validation_record_detail()
       
        domain_validation_records = []
        for record in record_detail:
            domain_validation_records.append(self.hosted_zone.generate_change_record(
            record.get("Name"),
            record.get("Type"),
            [record.get("Value")]
                )
            )
        
        return domain_validation_records


    def create_domain_validation_records(self, validation_records):

        for record in validation_records:
            self.hosted_zone.change_record_set([record])

    def wait_for_cert_not_in_use(
        self, wait_periods: int = 20, period_length: int = 30
    ) -> bool:
        associated_resources = self.describe()["InUseBy"]
        for _ in range(wait_periods):
            if not associated_resources:
                return True
            time.sleep(period_length)
            logger.info(
                f"{self.arn}: waiting for certificate to be not have any associated resources ..."
            )
            associated_resources = self.describe()["InUseBy"]
        else:
            logger.exception(
                f"timed out waiting for ceritificate to not have any associated resources. {self.arn}: in use by: {associated_resources}"
            )
            return False

    def delete(self):
        try:
            if self.wait_for_cert_not_in_use():
                self.acm_client.delete_certificate(CertificateArn=self.arn)
                logger.info(f"deleted certificate {self.arn}")
            else:
                logger.info(
                    f"skipped deleting certificate {self.arn} since it is in use"
                )
        except ClientError:
            logger.exception(f"failed to delete certificate {self.arn}")
            raise