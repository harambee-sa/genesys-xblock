
from django.db import models
from django.contrib.auth.models import User


class GenesysData(models.Model):

	"""
	Django model used to store the data posted by Genesys API

	"""
	
	event_type =  models.CharField(max_length=32, db_index=True)   
	event_date =  models.CharField(max_length=32, db_index=True)
	configuration_id =  models.CharField(max_length=32, db_index=True)
	respondent_id =  models.CharField(max_length=32, db_index=True)
	invitation_id = models.CharField(max_length=32, db_index=True)
	class Meta:
		unique_together = ["respondent_id", "invitation_id"]