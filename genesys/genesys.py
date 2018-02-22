"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import logging
import requests
from requests.auth import HTTPBasicAuth
import textwrap
from django.conf import settings
from xblock.core import XBlock
from django.contrib.auth.models import User
from xblock.fields import Scope, Integer, String, Float, List, Boolean, ScopeIds
from xblockutils.resources import ResourceLoader
from xblock.fragment import Fragment
from xblock.scorable import ScorableXBlockMixin, Score

from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.settings import XBlockWithSettingsMixin
from xblockutils.publish_event import PublishEventMixin
logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)



DEFAULT_DOCUMENT_URL = (
    'https://docs.google.com/presentation/d/1x2ZuzqHsMoh1epK8VsGAlanSo7r9z55ualwQlj-ofBQ/embed?'
    'start=true&loop=true&delayms=10000'
)

DEFAULT_EMBED_CODE = textwrap.dedent("""
    <iframe
        src="{}"
        frameborder="0"
        width="960"
        height="569"
        allowfullscreen="true"
        mozallowfullscreen="true"
        webkitallowfullscreen="true">
    </iframe>
""") .format(DEFAULT_DOCUMENT_URL)

@XBlock.needs('settings')
@XBlock.wants('user')
class GenesysXBlock(StudioEditableXBlockMixin, ScorableXBlockMixin, XBlockWithSettingsMixin, XBlock, PublishEventMixin):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default=u"Genesys"
    )

    invitation_url = String(
        help="The invitation url used to access tests by respondants on Genesys",
        scope=Scope.user_state,
        default=u""
    )

    respondent_id = String(
        help="The id of the respondent created/used for this invitation.",
        scope=Scope.user_state,
        default=u""
    )

    invitation_id = String(
        help="The numerical id of the invitation created on Genesys system.",
        scope=Scope.user_state,
        default=u""
    )

    embed_code = String(
        display_name="Embed Code",
        help=(
            "Google provides an embed code for Drive documents. In the Google Drive document, "
            "from the File menu, select Publish to the Web. Modify settings as needed, click "
            "Publish, and copy the embed code into this field."
        ),
        scope=Scope.settings,
        default=DEFAULT_EMBED_CODE
    )

    questionnaire_id = String(
        display_name="Questionnaire ID",
        help=(
            "Genesys Questionnaire ID needed to access test"
        ),
        scope=Scope.settings,
        default=''
    )
    
    external_id = String(
        display_name="External ID",
        help=(
            "Genesys external ID needed to access test"
        ),
        scope=Scope.settings,
        default=''
    )

    expiry_date = String(
        display_name="Expiry Date",
        help=(
            "Test Expriry Date"
        ),
        scope=Scope.settings,
        default=''
    )

    score = Score(help=("Dictionary with the current student score"),
        scope=Scope.user_state,
    )

    editable_fields = ('display_name', 'questionnaire_id ', 'external_id', 'expiry_date',)

    has_score = True

    @property
    def api_key(self):
        """
        Returns the Geneysis API token from Settings Service.
        The API key should be set in both lms/cms env.json files inside XBLOCK_SETTINGS.
        Example:
            "XBLOCK_SETTINGS": {
                "GenesysXBlock": {
                    "GENESYS_API_TOKEN": "YOUR API KEY GOES HERE"
                }
            },
        """
        return self.get_xblock_settings().get('GENESYS_API_KEY', '')

    @property
    def api_configuration_id(self):
        """
        Returns the Geneysis API token from Settings Service.
        The API key should be set in both lms/cms env.json files inside XBLOCK_SETTINGS.
        Example:
            "XBLOCK_SETTINGS": {
                "GenesysXBlock": {
                    "HARAMBEE_GENESYS_CONFIG_ID": "YOUR API KEY GOES HERE"
                }
            },
        """
        return self.get_xblock_settings().get('GENESYS_CONFIG_ID', '')

    @property
    def api_base_url(self):
        """
        Returns the URL of the Geneysis domain from the Settings Service.
        The URL hould be set in both lms/cms env.json files inside XBLOCK_SETTINGS.
        Example:
            "XBLOCK_SETTINGS": {
                "GenesysXBlock": {
                    "GENESYS_BASE_URL": "YOUR URL  GOES HERE"
                }
            },
        """
        return self.get_xblock_settings().get('GENESYS_BASE_URL' '')


    @property
    def api_invitation_url(self):

        return "{}/invitations/{}".format(
            self.api_base_url, 
            self.api_configuration_id
        )

    @property
    def api_results_url(self):

        return "{}/results/{}?respondantId={}".format(
            self.api_base_url, 
            self.api_configuration_id,
            self.respondent_id
        )

    @property
    def api_invitation_params():

        params = {
            "respondentFirstName":"Sam",
            "respondentFamilyName":"Sample",
            "respondentGender":"M",
            "respondentEmailAddress":"sam@sample.com",
            "questionnaireId": self.questionnaire_id, 
            "externalId": self.external_id, 
            "expiryDate": self.expiry_date
        }
        
        return params

    @property
    def get_headers(self):
        
        return {
            'Content-Type': 'application/json',
        }

    @property
    def api_authentication(self):

        username = self.get_xblock_settings().get('GENESYS_API_USERNAME', '')

        return HTTPBasicAuth(username, self.api_key)

    def get_genesys_invitation_handler(self):


        invitation = requests.post(
            url=self.api_invitation_url,
            headers=self.get_headers,
            auth=self.api_authentication,
            data=self.api_invitation_params,
            
        )

        if invitation.ok:
            self.invitation_id = invitation.json()['invitationId']
            self.respondent_id = invitation.json()['respondentId']
            self.invitation_url = invitation.json()['invitationUrl']

        return {
            'invitationId': self.invitation_id,
            'respondentId': self.respondent_id,
            'invitationUrl': self.invitation_url
        }

    def get_genesys_test_result(self, respondent_id, questionnaire_id):

        return ''

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the GenesysXBlock, shown to students
        when viewing courses.
        """

        content = {
            "src_url": DEFAULT_DOCUMENT_URL,
            "display_name": self.display_name
        }


        frag = Fragment(loader.render_django_template("static/html/genesys.html", context).format(self=self))
        frag.add_css(self.resource_string("static/css/genesys.css"))
        frag.add_javascript(self.resource_string("static/js/src/genesys.js"))
        frag.initialize_js('GenesysXBlock')
        return frag

    
    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        frag = Fragment()
        context = {'fields': []}
        
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
        frag.content = loader.render_django_template("static/html/genesys_edit.html", context)
        frag.add_javascript(loader.load_unicode("static/js/src/genesys_edit.js"))
        frag.initialize_js('StudioEditableXBlockMixin')
        return frag

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def calculate_score(self):
        """
        Calculate a new raw score based on the state of the problem.
        This method should not modify the state of the XBlock.
        Returns:
            Score(raw_earned=float, raw_possible=float)
        """
        raise NotImplementedError

    def get_score(self):
        score = self.runtime.publish(
            self, 
            "grade",
            {
                "value": submission_result,
                "max_value": max_value
            }
        )

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("GenesysXBlock",
             """<genesys/>
             """),
            ("Multiple GenesysXBlock",
             """<vertical_demo>
                <genesys/>
                <genesys/>
                <genesys/>
                </vertical_demo>
             """),
        ]
