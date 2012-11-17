class Svn(object):
    def __init__(self, module):
        self.module = module

    def checkout(self):
        cmd = "svn checkout %s %s" % (self.module.url, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "svn up")


class Git(object):
    def __init__(self, module):
        self.module = module
        self.url = self.module.url
        self.branch = module.branch
        if self.branch == "":
            self.branch = "master"

    def checkout(self):
        cmd = "git clone"
        if self.branch != "master":
            cmd += " --branch " + self.branch
        cmd += " %s %s" % (self.url, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "git pull")


class KdeGit(Git):
    def __init__(self, module):
        Git.__init__(self, module)
        self.url = "kde:" + module.name


class Bzr(object):
    def __init__(self, module):
        self.module = module

    def checkout(self):
        cmd = "bzr branch %s %s" % (self.module.url, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "bzr up")


class Hg(object):
    def __init__(self, module):
        self.module = module

    def checkout(self):
        cmd = "hg clone %s %s" % (self.module.url, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "hg pull")