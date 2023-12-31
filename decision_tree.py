# -*- coding: utf-8 -*-
"""decision tree.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lbF-_N7KPMY7kv7SbgR6U1w6CLYyb-ac
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %load_ext autoreload
# %autoreload 2

import numpy as np

words = np.loadtxt('/content/drive/MyDrive/dict.txt', dtype = str)
num_words = len( words )

def my_fit( words):
	verbose = False
	dt = Tree( min_leaf_size = 1, max_depth = 15 )
	dt.fit( words, verbose )
	return dt

class Tree:
	def __init__( self, min_leaf_size, max_depth ):
		self.root = None
		self.words = None
		self.min_leaf_size = min_leaf_size
		self.max_depth = max_depth

	def fit( self, words, verbose = False ):
		self.words = words
		self.root = Node( depth = 0, parent = None )
		if verbose:
			print( "root" )
			print( "└───", end = '' )
		# The root is trained with all the words
		self.root.fit( all_words = self.words, my_words_idx = np.arange( len( self.words ) ), min_leaf_size = self.min_leaf_size, max_depth = self.max_depth, verbose = verbose )

class Node:
	# A node stores its own depth (root = depth 0), a link to its parent
	# A link to all the words as well as the words that reached that node
	# A dictionary is used to store the children of a non-leaf node.
	# Each child is paired with the response that selects that child.
	# A node also stores the query-response history that led to that node
	# Note: my_words_idx only stores indices and not the words themselves
	def __init__( self, depth, parent ):
		self.depth = depth
		self.parent = parent
		self.all_words = None
		self.my_words_idx = None
		self.children = {}
		self.is_leaf = True
		self.query_idx = None
		self.history = []

	# Each node must implement a get_query method that generates the
	# query that gets asked when we reach that node. Note that leaf nodes
	# also generate a query which is usually the final answer
	def get_query( self ):
		return self.query_idx

	# Each non-leaf node must implement a get_child method that takes a
	# response and selects one of the children based on that response
	def get_child( self, response ):
		# This case should not arise if things are working properly
		# Cannot return a child if I am a leaf so return myself as a default action
		if self.is_leaf:
			print( "Why is a leaf node being asked to produce a child? Melbot should look into this!!" )
			child = self
		else:
			# This should ideally not happen. The node should ensure that all possibilities
			# are covered, e.g. by having a catch-all response. Fix the model if this happens
			# For now, hack things by modifying the response to one that exists in the dictionary
			if response not in self.children:
				print( f"Unknown response {response} -- need to fix the model" )
				response = list(self.children.keys())[0]

			child = self.children[ response ]

		return child

	def get_intersection( self, history ):
		lst = history[0]
		res = lst[1]
		ans = " "
		for li in history:
			respo = li[1]
			for i in range(min(len(res),len(respo))):
				if res[i]=='_' and respo[i]=='_':
					ans += "_ "
				elif res[i]!='_' and res[i]!=" ":
					ans += res[i]
					ans += " "
				elif respo[i]!='_' and respo[i]!=" ":
					ans += respo[i]
					ans += " "
			res = respo
		return ans.split()

	# Dummy leaf action -- just return the first word
	def process_leaf( self, my_words_idx, history ):
			return my_words_idx[0]

	def reveal( self, word, query ):
		# Find out the intersections between the query and the word
		mask = [ *( '_' * len( word ) ) ]

		for i in range( min( len( word ), len( query ) ) ):
			if word[i] == query[i]:
				mask[i] = word[i]

		return ' '.join( mask )

	# def indices(self, answer, all_words):
	# 	self.all_words = all_words
	# 	flag = 1
	# 	idc = []
	# 	for index,word in enumerate(all_words):
	# 		flag=1
	# 		for i in range(min(len(word),len(answer))):
	# 			if answer[i]!='_' and answer[i]!=word[i]:
	# 				flag = 0
	# 		if flag==1:
	# 			idc.append(index)
	# 	return idc

	def get_optimized_query( self, my_words_idx, all_words,history):
			self.history=history
			self.all_words = all_words
			self.my_words_idx = my_words_idx
			# random_idx = np.random.choice(len(all_words),500,replace=False)
			# random_word_pairs = [(i, all_words[i]) for i in random_idx]
			# ans = self.get_intersection(history)
			# get_optimized_ind = self.indices(ans, all_words)
			# print(ans)
			# for j in get_optimized_ind:
			# 	print(all_words[j])
			ans = self.get_intersection( history )
			if '_' not in ans:
				query = ans
			a = {}
			max = -100
			query_idx = 0
			query = all_words[0]
			for id in my_words_idx:
				q = all_words[id]
				if q==ans and query==ans:
					query_idx = id
					query = q
					self.process_leaf(id,history)
					break
				for idx in my_words_idx:
					mask = self.reveal( all_words[ idx ], q)
					if mask not in a:
						a[ mask ] = 0
					a[ mask ]+=1

				N = len(my_words_idx)
				sum = 0
				for (rev,l) in a.items():
					sum+=l*np.log(l)/(N*np.log(2))
				if np.log(N)/np.log(2)-sum > max:
					max = np.log(N)/np.log(2)-sum
					query_idx = id
					query = q
				a.clear()

			return (query_idx,query)


	# Dummy node splitting action -- use a random word as query
	# Note that any word in the dictionary can be the query
	def process_node( self, all_words, my_words_idx, history, verbose ):
		# For the root we do not ask any query -- Melbot simply gives us the length of the secret word
		if len( history ) == 0:
			query_idx = -1
			query = ""
		else:
			(query_idx,query) = self.get_optimized_query(my_words_idx, all_words,history)

		split_dict = {}

		if self.depth == 0:
			for (i,word) in enumerate(all_words):
				mask =( "_ " * len(word) )[:-1]
				if mask not in split_dict:
					split_dict[mask] = []

				split_dict[mask].append(i)
			return (query_idx, split_dict)

		else:
			for idx in my_words_idx:
				mask = self.reveal( all_words[ idx ], query )
				if mask not in split_dict:
					split_dict[ mask ] = []

				split_dict[ mask ].append( idx )
			if len( split_dict.items() ) < 2 and verbose:
				print( "Warning: did not make any meaningful split with this query!" )
			return ( query_idx, split_dict )

	def fit( self, all_words, my_words_idx, min_leaf_size, max_depth, fmt_str = "    ", verbose = False ):
		self.all_words = all_words
		self.my_words_idx = my_words_idx

		# If the node is too small or too deep, make it a leaf
		# In general, can also include purity considerations into account
		if len( my_words_idx ) <= min_leaf_size or self.depth >= max_depth:
			self.is_leaf = True
			self.query_idx = self.process_leaf( self.my_words_idx, self.history )
			if verbose:
				print( '█' )
		else:
			self.is_leaf = False
			( self.query_idx, split_dict ) = self.process_node( self.all_words, self.my_words_idx, self.history, verbose )

			if verbose:
				print( all_words[ self.query_idx ] )

			for ( i, ( response, split ) ) in enumerate( split_dict.items() ):
				if verbose:
					if i == len( split_dict ) - 1:
						print( fmt_str + "└───", end = '' )
						fmt_str += "    "
					else:
						print( fmt_str + "├───", end = '' )
						fmt_str += "│   "

				# Create a new child for every split
				self.children[ response ] = Node( depth = self.depth + 1, parent = self )
				history = self.history.copy()
				history.append( [ self.query_idx, response ] )
				self.children[ response ].history = history

				# Recursively train this child node
				self.children[ response ].fit( self.all_words, split, min_leaf_size, max_depth, fmt_str, verbose )

import time as tm
import pickle
import warnings
import os

class Merlin:
	def __init__( self, query_max, words ):
		self.words = words
		self.num_words = len( words )
		self.secret = ""
		self.query_max = query_max
		self.arthur = None
		self.win_count = 0
		self.tot_query_count = 0
		self.rnd_query_count = 0

	def meet( self, arthur ):
		self.arthur = arthur

	def reset( self, secret ):
		self.secret = secret
		self.rnd_query_count = 0

	# Receive a message from Arthur
	# Process it and terminate the round or else message Arthur back
	# Arthur can set is_done to request termination of this round after this query
	def msg( self, query_idx, is_done = False ):

		# Supplying an illegal value for query_idx is a way for Arthur to request
		# termination of this round immediately without even processing the current query
		# However, this results in query count being set to max for this round
		if query_idx < 0 or query_idx > self.num_words - 1:
			warnings.warn( "Warning: Arthur has sent an illegal query -- terminating this round", UserWarning )
			self.tot_query_count += self.query_max
			return

		# Arthur has made a valid query
		# Find the guessed word and increase the query counter
		query = self.words[ query_idx ]
		self.rnd_query_count += 1
		# Find out the intersections between the query and the secret
		reveal = [ *( '_' * len( self.secret ) ) ]

		for i in range( min( len( self.secret ), len( query ) ) ):
			if self.secret[i] == query[i]:
				reveal[ i ] = self.secret[i]

		# The word was correctly guessed
		if '_' not in reveal:
			self.win_count += 1
			self.tot_query_count += self.rnd_query_count
			return
		# print(reveal)
		# Too many queries have been made - terminate the round
		if self.rnd_query_count >= self.query_max:
			self.tot_query_count += self.rnd_query_count
			return

		# If Arthur is done playing, terminate this round
		if is_done:
			self.tot_query_count += self.rnd_query_count
			return

		# If none of the above happen, continue playing
		self.arthur.msg( ' '.join( reveal ) )


	def reset_and_play( self, secret ):
		self.reset( secret )
		self.arthur.msg( ( "_ " * len( self.secret ) )[:-1] )

class Arthur:
	def __init__( self, model ):
		self.dt = model
		self.curr_node = self.dt.root
		self.merlin = None
		self.is_done = False

	def meet( self, merlin ):
		self.merlin = merlin

	def reset( self ):
		self.curr_node = self.dt.root
		self.is_done = False

	def msg( self, response ):
  # If we are not at a leaf, lets go to the appropriate child based on the response
		if not self.curr_node.is_leaf:
			self.curr_node = self.curr_node.get_child( response )

		# If we are at a leaf, we should reqeust Merlin to terminate the round after this query
		else:
			self.is_done = True

		# Either way, get the query to be sent to Merlin
		query = self.curr_node.get_query()
		self.merlin.msg( query, self.is_done )

query_max = 15
n_trials = 5

t_train = 0
m_size = 0
win = 0
query = 0

for t in range( n_trials ):
	tic = tm.perf_counter()
	model = my_fit( words )
	toc = tm.perf_counter()
	t_train += toc - tic

	with open( f"model_dump_{t}.pkl", "wb" ) as outfile:
		pickle.dump( model, outfile, protocol=pickle.HIGHEST_PROTOCOL )

	m_size += os.path.getsize( f"model_dump_{t}.pkl" )

	merlin = Merlin( query_max, words )
	arthur = Arthur( model )
	merlin.meet( arthur )
	arthur.meet( merlin )

	for ( i, secret ) in enumerate( words ):
		arthur.reset()
		merlin.reset_and_play(secret)

	win += merlin.win_count / num_words
	query += merlin.tot_query_count / num_words

t_train /= n_trials
m_size /= n_trials
win /= n_trials
query /= n_trials

print( t_train, m_size, win, query )