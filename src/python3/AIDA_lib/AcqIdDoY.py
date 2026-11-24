#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

class AcqIdDoY(object):
   """
   Classe d'objet pour les acqid où le numero d'acquisition correspond au 
   numero du jour dans l'année.
   On peut initialiser soit avec une chaine AcqId, soit avec
   l'abreviation de la plateforme et la date sous forme d'un datetime :

   Utilisation : 

   AcqIDoY ( acqid=<chaine acqid>, plateforme=<chaine abreviation plateforme>, date=<datetime> )
   
   """
   @staticmethod
   def date_to_acqid (plateforme, date):
       """ Transformation de plateforme + date(de type datetime) en acqid """
       if isinstance(date, datetime.date) :
          acqid = plateforme[0:2] + date.strftime("%y") + '{:04d}'.format(int(date.strftime("%j")))
          return acqid
       else :
          raise ValueError ("L'argument date n'est pas de type datetime")


   def __init__ (self, acqid="", plateforme="", date=None):
      if plateforme and date :
         self._valeur = self.date_to_acqid (plateforme, date)
      elif acqid :
         self._valeur = acqid
      else :
         self._valeur = None
      self._date = datetime.datetime.strptime(self._valeur[2:8], "%y0%j")
       
   def __str__ (self) :
      return(self._valeur) 

   def __str__ (self):
      return(self._valeur)

   def __add__ (self, other):
      date = self.acqid_to_date()
      date_new = date + datetime.timedelta(days=other)
      acqid = self.__class__(plateforme=self._valeur[0:2], date=date_new)
      return acqid

   def __sub__ (self, other):
      date = self.acqid_to_date()
      date_new = date - datetime.timedelta(days=other)
      acqid = self.__class__(plateforme=self._valeur[0:2], date=date_new)
      return acqid

   def __lt__ (self, other):
      date1 = self.acqid_to_date()
      date2 = other.acqid_to_date()
      if date1 < date2:
         return True
      else :
         return False

   def __gt__ (self, other):
      date1 = self.acqid_to_date()
      date2 = other.acqid_to_date()
      if date1 > date2:
         return True
      else :
         return False

   def __le__ (self, other):
      date1 = self.acqid_to_date()
      date2 = other.acqid_to_date()
      if date1 <= date2:
         return True
      else :
         return False

   def __ge__ (self, other):
      date1 = self.acqid_to_date()
      date2 = other.acqid_to_date()
      if date1 >= date2:
         return True
      else :
         return False

   def __eq__ (self, other):
      date1 = self.acqid_to_date()
      date2 = other.acqid_to_date()
      if date1 == date2:
         return True
      else :
         return False

   def __ne__ (self, other):
      date1 = self.acqid_to_date()
      date2 = other.acqid_to_date()
      if date1 != date2:
         return True
      else :
         return False

   def acqid_to_date (self) :
      """ Transformation d'un AcqId en date de type datetime """
      return self._date
