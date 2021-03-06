import os
import subprocess


class BaseVcs(object):
    def __init__(self, module):
        self.module = module

    def switch_branch(self, runner):
        pass

    def checkout(self, runner):
        raise NotImplementedError

    def update(self, runner):
        raise NotImplementedError


class Svn(BaseVcs):
    def checkout(self, runner):
        cmd = "svn checkout %s %s" % (self.module.url, self.module.name)
        runner.run(self.module.base_dir, cmd)

    def update(self, runner):
        runner.run(self.module.src_dir, "svn up --non-interactive")


class Git(BaseVcs):
    def __init__(self, module):
        BaseVcs.__init__(self, module)
        self.url = self.module.url
        self.branch = module.branch
        if self.branch == "":
            self.branch = "master"

    def checkout(self, runner):
        cmd = "git clone --recursive"
        if self.branch != "master":
            cmd += " --branch " + self.branch
        cmd += " %s %s" % (self.url, self.module.name)
        runner.run(self.module.base_dir, cmd)

    def switch_branch(self, runner):
        runner.run(self.module.src_dir, "git fetch")
        if self.branch in self._list_local_branches():
            cmd = "git checkout "  + self.branch
        else:
            cmd = "git checkout -b " + self.branch + " origin/" + self.branch
        runner.run(self.module.src_dir, cmd)

    def update(self, runner):
        runner.run(self.module.src_dir, "git pull --rebase")
        runner.run(self.module.src_dir, "git submodule update")

    def _list_local_branches(self):
        output = subprocess.check_output(["git", "branch"], cwd=self.module.src_dir)
        for line in output.splitlines():
            yield line[2:]


class KdeGit(Git):
    def __init__(self, module):
        Git.__init__(self, module)
        self.url = "kde:" + os.path.basename(module.name)


class Bzr(BaseVcs):
    def checkout(self, runner):
        cmd = "bzr branch %s %s" % (self.module.url, self.module.name)
        runner.run(self.module.base_dir, cmd)

    def update(self, runner):
        runner.run(self.module.src_dir, "bzr pull")


class Hg(BaseVcs):
    def checkout(self, runner):
        cmd = "hg clone %s %s" % (self.module.url, self.module.name)
        runner.run(self.module.base_dir, cmd)

    def update(self, runner):
        runner.run(self.module.src_dir, "hg pull")


class PartialSvn(BaseVcs):
    def __init__(self, module, repo_dirs):
        BaseVcs.__init__(self, module)
        self.repo_dirs = repo_dirs

    def checkout(self, runner):
        cmd = "svn checkout --depth files %s %s" % (self.module.url, self.module.name)
        runner.run(self.module.base_dir, cmd)
        self.update(runner)

    def update(self, runner):
        for repo_dir in self.repo_dirs:
            runner.run(self.module.src_dir, "svn up --non-interactive " + repo_dir)
