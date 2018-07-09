import logging

import boto3


class Service:
    def __init__(self, config_service):
        self.config_service = config_service

        self.logger = logging.getLogger("zebr0-aws.route53.service")
        self.resource_record_set = None

        try:
            region = self.config_service.lookup("region")
            self.logger.info("creating route53 client")
            self.client = boto3.client(service_name="route53", region_name=region)

            self.domain_name = self.config_service.lookup("domain-name")

            self.logger.info("checking hosted zone")
            hosted_zones = self.client.list_hosted_zones_by_name(DNSName=self.domain_name, MaxItems="1").get("HostedZones")
            if hosted_zones and hosted_zones[0].get("Name") == self.domain_name:
                self.hosted_zone_id = hosted_zones[0].get("Id")
                self.fqdn = ".".join([self.config_service.stage, self.config_service.project, self.domain_name])  # TODO

                self.logger.info("checking resource record set")
                resource_record_sets = self.client.list_resource_record_sets(
                    HostedZoneId=self.hosted_zone_id,
                    StartRecordName=self.fqdn,
                    StartRecordType="A",
                    MaxItems="1"
                ).get("ResourceRecordSets")
                if resource_record_sets and resource_record_sets[0].get("Name") == self.fqdn:
                    self.resource_record_set = resource_record_sets[0]
            else:
                self.logger.warning("no hosted zone was found in route53 for the '%s' domain, it needs to be created manually", self.domain_name)
        except LookupError as error:
            self.logger.warning("%s, skipping dns entry management", error)

    def create_dns_entry_if_needed(self, address):
        if not self.resource_record_set:
            ttl = int(self.config_service.lookup("dns-record-ttl"))

            self.logger.info("creating resource record set")
            self.client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone_id,
                ChangeBatch={"Changes": [{
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": self.fqdn,
                        "Type": "A",
                        "TTL": ttl,
                        "ResourceRecords": [{"Value": address}]
                    }
                }]}
            )

    def destroy_dns_entry_if_needed(self):
        if self.resource_record_set:
            self.logger.info("destroying resource record set")
            self.client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone_id,
                ChangeBatch={"Changes": [{
                    "Action": "DELETE",
                    "ResourceRecordSet": self.resource_record_set
                }]}
            )
