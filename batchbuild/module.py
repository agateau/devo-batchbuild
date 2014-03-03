import logging
import os
import shutil

import vcs

class Module(object):
    def __init__(self, config):
        self.config = config
        self.name = self.config.flat_get("name")
        assert self.name is not None

        self.base_dir = os.environ["DEVO_SOURCE_BASE_DIR"]
        self.src_dir = os.path.join(self.base_dir, self.name)
        self.build_dir = os.path.join(os.environ["DEVO_BUILD_BASE_DIR"], self.name)

        # Init repository stuff
        repo_type = self.config.get("repo-type")
        assert repo_type is not None

        self.branch = self.config.get("branch", "")

        # Expanding vars is useful for tests
        self.url = os.path.expandvars(self.config.get("repo-url", ""))
        if repo_type == "svn":
            self.vcs = vcs.Svn(self)
        elif repo_type == "partialsvn":
            self.vcs = vcs.PartialSvn(self, self.config.get("repo-dirs"))
        elif repo_type == "git":
            self.vcs = vcs.Git(self)
        elif repo_type == "kdegit":
            self.vcs = vcs.KdeGit(self)
        elif repo_type == "bzr":
            self.vcs = vcs.Bzr(self)
        elif repo_type == "hg":
            self.vcs = vcs.Hg(self)
        else:
            raise Exception("Unknown repo-type: %s" % repo_type)

    def has_checkout(self):
        return os.path.exists(self.src_dir)

    def checkout(self, runner):
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.vcs.checkout(runner)

    def switch_branch(self, runner):
        self.vcs.switch_branch(runner)

    def update(self, runner):
        self.vcs.update(runner)

    def refresh_build(self):
        if os.path.exists(self.build_dir):
            logging.info("Removing dir '%s'" % self.build_dir)
            shutil.rmtree(self.build_dir)

    def configure(self, runner):
        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)
        configure = self.config.get("configure", "devo_cmake " + self.src_dir)
        opts = self.config.get("configure-options", "")
        extra_opts = self.config.get("configure-extra-options", "")
        runner.run(self.build_dir, configure + " " + opts + " " + extra_opts, env=self._getenv())

    def build(self, runner):
        if not os.path.exists(self.build_dir):
            self.configure()
        build = self.config.get("build", "make")
        if not build:
            return
        opts = self.config.get("build-options", "")
        extra_opts = self.config.get("build-extra-options", "")
        runner.run(self.build_dir, build + " " + opts + " " + extra_opts, env=self._getenv(), report_progress=True)

    def install(self, runner):
        install = self.config.get("install", "make install")
        if not install:
            return
        opts = self.config.get("install-options", "")
        extra_opts = self.config.get("install-extra-options", "")
        runner.run(self.build_dir, install + " " + opts + " " + extra_opts, env=self._getenv())

    def _getenv(self):
        env = dict(os.environ)
        env["DEVO_SOURCE_DIR"] = os.path.join(env["DEVO_SOURCE_BASE_DIR"], self.name)
        env["DEVO_BUILD_DIR"] = os.path.join(env["DEVO_BUILD_BASE_DIR"], self.name)
        return env
