import argparse

import config
import ec2


def init_environment(args):
    vpc_id = ec2.create_vpc_if_needed(args.project, args.stage)
    subnet_id = ec2.create_subnet_if_needed(args.project, args.stage, vpc_id)
    instance_id = ec2.create_instance_if_needed(args.project, args.stage, subnet_id)
    ec2.create_internet_gateway_if_needed(args.project, args.stage, vpc_id)
    ec2.create_address_if_needed(args.project, args.stage, instance_id)


def destroy_environment(args):
    ec2.destroy_address_if_needed(args.project, args.stage)
    ec2.destroy_internet_gateway_if_needed(args.project, args.stage)
    ec2.destroy_instance_if_needed(args.project, args.stage)
    ec2.destroy_subnet_if_needed(args.project, args.stage)
    ec2.destroy_vpc_if_needed(args.project, args.stage)


def edit_config(args):
    config.edit_config(args.filename)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="")
    subparsers = argparser.add_subparsers()

    parser_init = subparsers.add_parser("init", help="")
    parser_init.add_argument("project", help="")
    parser_init.add_argument("stage", help="")
    parser_init.set_defaults(func=init_environment)

    parser_destroy = subparsers.add_parser("destroy", help="")
    parser_destroy.add_argument("project", help="")
    parser_destroy.add_argument("stage", help="")
    parser_destroy.set_defaults(func=destroy_environment)

    parser_config = subparsers.add_parser("config", help="")
    parser_config.add_argument("filename", nargs="?", default="/etc/zebr0.conf", help="")
    parser_config.set_defaults(func=edit_config)

    args = argparser.parse_args()
    args.func(args)
