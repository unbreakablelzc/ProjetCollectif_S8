#!/usr/bin/python2
# -*- encoding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class algorithme():
	__metaclass__ = ABCMeta

	#doit retourner une liste
	@abstractmethod
	def traiterVideo(self,video):
		pass

	@abstractmethod
	def get_nomAlgo(self):
			pass



