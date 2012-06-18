#!/usr/bin/env python
import logging
import os
import sys
from optparse import OptionParser

import yaml

from batchbuilderror import BatchBuildError
from module import Module
from runner import Runner

USAGE="%prog <project.yaml> [module1 [module2...]]"


def main():
    parser = OptionParser(usage=USAGE)

    # Add an invert boolean option stored in options.verbose.
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Print command output to stdout")

    (options, args) = parser.parse_args()
    logging.basicConfig(format="devo-batchbuild: %(asctime)s %(message)s", level=logging.DEBUG)

    # Check devo name
    devo_name = os.environ.get("DEVO_NAME", None)
    if devo_name is None:
        logging.error("No devo set up")
        return 1
    logging.info("Using devo '%s'", devo_name)

    # Load config
    if len(args) == 0:
        parser.error("Missing args")
    config = yaml.load(open(args[0]))
    base_dir = os.path.expanduser(config["global"]["base-dir"])

    # Select modules to build
    if len(args) > 1:
        module_names = set(args[1:])
        module_configs = []
        for module_config in config["modules"]:
            name = module_config["name"]
            if name in module_names:
                module_configs.append(module_config)
                module_names.remove(name)
        if len(module_names) > 0:
            logging.error("Unknown modules: %s", ", ".join(module_names))
            return 1
    else:
        module_configs = config["modules"]

    # Setup logging
    log_dir = os.path.join(base_dir, "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    fails = []
    for module_config in module_configs:
        log_file_name = os.path.join(log_dir, module_config["name"] + ".log")
        log_file = open(log_file_name, "w")
        runner = Runner(log_file, options.verbose)
        module = Module(config["global"], module_config, runner)
        try:
            if module.has_checkout():
                module.update()
            else:
                module.checkout()
            module.configure()
            module.build()
            module.install()
        except BatchBuildError, exc:
            logging.error("%s failed to build: %s", module_config["name"], exc)
            fails.append([module_config["name"], str(exc), log_file_name])

    if len(fails) > 0:
        logging.info("%d modules failed to build:", len(fails))
        for name, msg, log_file_name in fails:
            logging.info("- %s: %s, see %s", name, msg, log_file_name)
    else:
        logging.info("All modules built successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
