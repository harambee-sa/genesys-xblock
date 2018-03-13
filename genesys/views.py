



import requests  
import json
import urlparse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden
from .models import GenesysData

@csrf_exempt
def genesys_result_receiver(request):

	if request.method == 'POST':
		referer = request.META.get('HTTP_REFERER')
    	referer_parts = urlparse.urlparse(referer) if referer else None
    	referer_hostname = referer_parts.hostname if referer_parts is not None else None
    	domain_is_whitelisted = (
        	referer_hostname in getattr(settings, 'CORS_ORIGIN_WHITELIST', [])
    	)
    	if not domain_is_whitelisted:
    		return HttpResponseForbidden('Permission denied.')
    	else:
			received_json_data = json.loads(request.body)
			GenesysData.objects.create(
				event_type = received_json_data['eventType'],
				event_date = received_json_data['eventDate'],
				configuration_id = received_json_data['configurationId'],
				respondent_id = received_json_data['respondantId'],
				invitation_id = received_json_data['invitationId'],
			)
	return HttpResponse()