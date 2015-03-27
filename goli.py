import json
import sys
import requests

license_filenames = ["LICENSE", "LICENSE.txt"]

def main():
	with open(sys.argv[1]) as f:
		godeps_json = json.load(f)
	deps = [dep_from_json(d) for d in godeps_json["Deps"]]
	for d in deps:
		license_info = d.license()
		if license_info:
			print "Found license for " + d.import_path + " at " + license_info[0]+ ":\n\n" + license_info[1] + "\n\n"
		else:
			print "No license found for " + d.import_path + ", tried urls: "+ str(d._possible_license_urls()) + "\n\n"

def dep_from_json(j):
	return Dep(j["ImportPath"], j["Rev"])

class Dep(object):
	def __init__(self, import_path, rev):
		self.import_path = import_path
		self.rev = rev

	def license(self):
		for u in self._possible_license_urls():
			r = requests.get(u)
			if r.status_code == requests.codes.ok:
				return u, r.text

	def _possible_license_urls(self):
		if self.import_path.startswith("github.com/"):
			return possible_github_license_urls("/".join(self.import_path.split("/")[1:3]), self.rev)
		elif self.import_path.startswith("code.google.com/"):
			reponame = self.import_path.split("/")[2]

			extra_parts = self.import_path.split("/")[3:]
			urls = []
			for i in range(len(extra_parts)+1):
				suffix = "/".join(extra_parts[:i])
				if suffix:
					suffix += "/"
				for f in license_filenames:
					url = "https://"+reponame+".googlecode.com/hg-history/"+self.rev+"/"+suffix+f
					urls.append(url)
			return urls
		elif self.import_path.startswith("gopkg.in/"):
			package = self.import_path.split("/")[1].split(".")[0]
			return possible_github_license_urls("go-"+package+"/"+package, self.rev)
		elif self.import_path.startswith("golang.org/x/"):
			package = self.import_path.split("/")[2]
			return possible_github_license_urls("golang/"+package, self.rev)
		else:
			return []

def possible_github_license_urls(reponame, rev):
	urls = []
	for f in license_filenames:
		urls.append("https://github.com/"+reponame+"/raw/"+rev+"/"+f)
	return urls

if __name__ == "__main__":
	main()
