

from .models import GenesysData

import requests  
import json

def genesys_result_receiver(request):

	if request.method == 'POST':
		 # a new test result entry for this user
		received_json_data = json.loads(request.body)

		GenesysData.objects.create(
			event_type = received_json_data['eventType'],
			event_date = received_json_data['eventDate'],
			configuration_id = received_json_data['configurationId'],
			respondent_id = received_json_data['respondantId'],
			invitation_id = received_json_data['invitationId'],

		)


