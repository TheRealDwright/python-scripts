import subprocess
import re
import datetime
import time
import argparse


class Action:
    START = 1
    UPDATE = 2
    CREATE = 3


class Options:
    region = None
    action = None
    confirm = True
    template_url = None
    region = None
    parameters = None
    stack_name = None
    wait = False


def usage(message=None):
    if message:
        print("\nERROR: %s" % message)
    exit(2)


def abort(code, message=None):
    if message:
        print("\nERROR: %s" % message)
    print("\nERROR: exit code %d" % code)
    exit(code)


def run_command(cmd):
    print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out, err


def find_json_value(key, text):
    match = re.search(r"\"%s\": +\"(.*)\"" % key, text, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return None


def check_status(options):
    cmd = ['aws', 'cloudformation', 'describe-stacks',
           '--region', options.region, '--stack-name', options.stack_name]
    err, json, stderr = run_command(cmd)
    if err == 0:
        status = find_json_value('StackStatus', json)
    else:
        status = stderr
    return err, status


def log(message):
    timestamp = datetime.datetime.strftime(datetime.datetime.now(),
                                           '%Y-%m-%d %H:%M:%S')
    print("%s: %s" % (timestamp, message))


def cfn_wait(options):
    print("Waiting for %s to complete." % options.stack_name)
    complete_statuses = ['CREATE_COMPLETE',
                         'DELETE_COMPLETE',
                         'UPDATE_COMPLETE']
    failure_statuses = ['UPDATE_ROLLBACK_COMPLETE', 'ROLLBACK_COMPLETE']
    period = 10.
    while True:
        time0 = datetime.datetime.now()
        err, status = check_status(options)
        log(status)
        if err != 0 or status in complete_statuses:
            return err, status
        if status in failure_statuses:
            return 1, status
        time1 = datetime.datetime.now()
        delay = period - (time1-time0).total_seconds()
        if delay > 0:
            time.sleep(delay)


def cfn_status(options):
    print("Checking status of %s." % options.stack_name)
    err, status = check_status(options)
    if err == 0:
        log(status)
    else:
        abort(err, status)


def cfn_start(options):
    print("Looking for existing stack %s." % options.stack_name)
    err, status = check_status(options)
    if err == 0:
        cfn_update(options)
    elif err == 255:
        cfn_create(options)
    else:
        abort(err, status)


def construct_aws_command(options, action):
    if options.template_url is None:
        usage("Missing template-url")
    if options.stack_name is None:
        usage("Missing stack-name")
    cmd = [
        'aws',
        'cloudformation',
        '--region', options.region,
        'update-stack' if action == Action.UPDATE else 'create-stack',
        '--stack-name',    options.stack_name,
        '--template-url',  options.template_url,
        '--capabilities',  'CAPABILITY_IAM'
    ]

    if options.parameters:
        cmd += ['--parameters']
        cmd.extend(options.parameters)

    print(cmd)
    return cmd


def cfn_update(options):
    print("Updating stack %s." % options.stack_name)
    cmd = construct_aws_command(options, Action.UPDATE)
    err, json, stderr = run_command(cmd)
    if err != 0:
        abort(err, stderr)
    print json


def cfn_create(options):
    print("Creating stack %s." % options.stack_name)
    cmd = construct_aws_command(options, Action.CREATE)
    err, json, stderr = run_command(cmd)
    if err != 0:
        abort(err, stderr)
    print json


def main():
    options = Options()
    options.region = 'us-west-1'

    parser = argparse.ArgumentParser(description='Run cloudformation')
    parser.add_argument("-y", "--yes", dest="confirm", action="store_true",
                        help="Answer yes to any confirmation prompts."
                        )
    parser.add_argument("-r", "--region", dest="region", type=str,
                        default="us-west-2",
                        help="The AWS region to deploy to."
                        )
    parser.add_argument("-t", "--template-url", dest="template_url",
                        type=str, help="The template url to run."
                        )
    parser.add_argument("-p", "--parameters", dest="parameters",
                        type=str, nargs="*",
                        help="The parameters to pass on."
                        )
    parser.add_argument("-n", "--stack-name", dest="stack_name", type=str,
                        help="The stack name to run."
                        )
    parser.add_argument("-w", "--wait", dest="wait", action="store_true",
                        help="Wait for the status to a *_COMPLETE statuses"
                        )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--start", dest="action", action="store_const",
                       const=Action.START
                       )
    group.add_argument("-u", "--update", dest="action", action="store_const",
                       const=Action.UPDATE
                       )
    group.add_argument("-c", "--create", dest="action", action="store_const",
                       const=Action.CREATE
                       )
    args = parser.parse_args()

    for arg in vars(args):
        setattr(options, arg, getattr(args, arg))
    print(options.__dict__)

    if options.action == Action.START:
        cfn_start(options)
    elif options.action == Action.UPDATE:
        cfn_update(options)
    elif options.action == Action.CREATE:
        cfn_create(options)
    elif not options.wait:
        cfn_status(options)

    if options.wait:
        err, status = cfn_wait(options)
        if err != 0:
            abort(err, status)

if __name__ == "__main__":
    main()
