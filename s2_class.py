#!/usr/bin/python
import os
import os.path
import shutil
import glob
import time
import markdown

class S2:
	def __init__(self,argdict):
		self.s2dir = argdict['dir']
		if (self.s2dir == None):
			self.s2dir = '.'
		self.source_dir = os.path.join(self.s2dir,'source') 
		#self.posts_dir = os.path.join(self.s2dir,'source/posts')
		self.wstatic_dir = os.path.join(self.s2dir,'wstatic')
		self.www_dir = os.path.join(self.s2dir,'www')
		self.data_dir = os.path.join(self.s2dir,'data')

	def create(self,argdict):
		#check dir permissions
		if (not os.access(self.s2dir, os.W_OK) ):
			print "You don't have WRITE permission on the specified directory."
			return -1
		#check dir is empty
		if (os.listdir(self.s2dir) != []):
			print "The specified directory is NOT empty. It must be empty."
			return -1
		#defince dirs: source, source/posts, wstatic, www, data
		#create dirs
		os.mkdir(self.source_dir)
		os.mkdir(self.wstatic_dir)
		os.mkdir(self.www_dir)
		os.mkdir(self.data_dir)
		#cp _index.html to source
		#THIS NEXT LINE IS A HERESY!
		shutil.copy('/usr/local/etc/s2/_index.html',os.path.join(self.s2dir,'source'))
		
	def addpost(self,argdict):
		rawtitle = argdict['title']
		if (rawtitle == None):
			print "You must specify the post title."
			return -1
		#lowercase, collapse all spaces to 1, replace all spaces by '-', 
		ptitle=('-'.join(rawtitle.split())).lower()
		pdir = os.path.join(self.source_dir,ptitle)
		os.mkdir(pdir)
		pfname = ptitle + '.s2md'
		pfile = open(os.path.join(pdir,pfname),'w')
		pfile.write('<!--' + ptitle + '-->\n\n')
		#now maybe add some YAML metadata: init time, last mod time, pub time, author, tags
		pfile.write("# " +rawtitle +'\n\n')
		pfile.write("This is the body of the post.\n")
		pfile.close()



	def generate(self,argdict):
		self.gen_time = int(time.time())
		# do rsync of wstatic/* to www
		# cp _index.html to www/index.html
		#each dir is a "post", or "page"

		#this sourcefiles now it takes all, but in reality it should be the files that
		# the program detects have changed.
		#so, instead of listdir, I should be calling a function that does all the comparisons
		#etc, and gives me the modified sources.
		modsources = os.listdir(self.source_dir)
		if (not os.path.isfile(os.path.join(self.data_dir,'modtimes.txt'))):
			#create the first record of modification times
			print "CREATING FIRST RECORD OF MOD TIMES"
			print "NOT DONE YET"

		for f in modsources:
			cfn = os.path.join(self.source_dir,f)
			if os.path.isdir(cfn):  #it's a post
				mdfiles = glob.glob(os.path.join(cfn,'*.s2md') )
				if len(mdfiles) > 1:
					print f + " has more than one markdown file. Using first one."
				else:
					if len(mdfiles) == 0:
						print "Skipping " + f + " because it has no markdown."
					else:
						mf = mdfiles[0]
						mdfile = open(mf,'r')
						mdcontent = mdfile.read()
						mdfile.close()
						#we need to mix the rendered html with the index.html
						print markdown.markdown(mdcontent)
						#LOOK AT THE EXTENSIONS, I can use the id and class things etc.
						#and put it in the right "place" (folder) year/month/day/title
						#that should be the "publication date" (there might be corrections)
						#afterward... but should keep the orig pub date.

		#I ALSO need to generate the archives, etc.

		#get list of folders in source/posts. Folder name is name of post. It's a folder because
		#I just want to use a "bucket" for while I write, test things, etc.
		#within a post's folder, the file with extension "s2md" (s2 markdown) is the post
		#so, go through each post folder
		#if ANYTHING has changed, we need to re-generate the post 
		# how do we know if anything has changed
		# stat -c%Y source/_index.html   gives me the time of last modification (seconds since Epoch)
		#os.stat(filename).st_mtime
		# int(os.stat('_index.html').st_mtime) this gives me the last mod time (from within python)

		# I can keep a file of filenames + last mod time
		# and use python's difflib to compare the mod times from last geneation, to now...
		