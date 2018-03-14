"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import logging
import json
import requests
import random
from .models import GenesysData
from django.conf import settings
from xblock.core import XBlock
from django.contrib.auth.models import User
from student.models import UserProfile
from xblock.fields import Scope, Integer, String, Float, List, Boolean, ScopeIds
from xblock.fields import JSONField
from xblock.validation import ValidationMessage
from xblockutils.resources import ResourceLoader
from xblock.fragment import Fragment
from xblock.scorable import ScorableXBlockMixin, Score
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.settings import XBlockWithSettingsMixin
from xblockutils.publish_event import PublishEventMixin
logger = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


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

    instruction = String(
        display_name="Instruction Message",
        help="The instruction message that appears above the hyperlink to the Genesys test",
        scope=Scope.settings,
        default=u"Click on the link below when you are ready to start the test."
    )

    start_now = String(
        display_name="Start Message",
        help="The text value of the hyperlink",
        scope=Scope.settings,
        default=u"Start test now!"
    )

    completed_message = String(
        display_name="Completed Message",
        help="The message for completing the test",
        scope=Scope.settings,
        default=u"You have completed all the tests."
    )

    invitation_url = String(
        help="The invitation url used to access tests by respondents on Genesys",
        scope=Scope.user_state,
        default=None
    )

    respondent_id = Integer(
        help="The id of the respondent created/used for this invitation.",
        scope=Scope.user_state,
        default=None
    )

    invitation_id = Integer(
        help="The numerical id of the invitation created on Genesys system.",
        scope=Scope.user_state,
        default=u""
    )

    questionnaire_id = String(
        display_name="Questionnaire ID",
        help=(
            "Genesys Questionnaire ID needed to access test"
        ),
        scope=Scope.settings,
        default=None
    )
    
    external_id = String(
        display_name="External ID",
        help=(
            "Genesys external ID needed to access test"
        ),
        scope=Scope.settings,
        default=None
    )

    expiry_date = String(
        display_name="Expiry Date",
        help=(
            "Test Expriry Date"
        ),
        scope=Scope.settings,
        default=''
    )

    test_started = Boolean(
        scope=Scope.user_state,
        default=False
    )

    invitation_successful = Boolean(
        scope=Scope.user_state,
        default=False
    )

    test_completed= Boolean(
        scope=Scope.user_state,
        default=False
    )

    test_id_list = List(
        display_name="Genesys Test ID's and Scores",
        help="Test ID's of the Genesys test you wish to include in Xblock.",
        allow_reset=False,
        scope=Scope.settings
    )

    score = JSONField(help="Dictionary with the current student score", scope=Scope.user_state)

    editable_fields = (
        'display_name',
        'questionnaire_id',
        'external_id',
        'expiry_date',
        'test_id_list',
        'instruction',
        'start_now',
        'completed_message',
    )

    has_score = True

    def validate_field_data(self, validation, data):
        """
        Validate this block's field data. We are validating that the chosen
        freetextresponse xblocks ID's exist in the course
        """
        if len(data.test_id_list) == 0:
            validation.add(
                ValidationMessage(
                    ValidationMessage.ERROR,
                    u"Please specify Genesys Test ID's and Scores."
                )
            )
        if data.external_id is None:
            validation.add(
                ValidationMessage(
                    ValidationMessage.ERROR,
                    u"Please specify an external ID."
                )
            )
        if data.questionnaire_id is None:
            validation.add(
                ValidationMessage(
                    ValidationMessage.ERROR,
                    u"Please specify Questionnaire ID."
                )
            )


    @property
    def api_configuration_id(self):
        """
        Returns the Geneysis API token from Settings Service.
        The API key should be set in both lms/cms env.json files inside XBLOCK_SETTINGS.
        Example:
            "XBLOCK_SETTINGS": {
                "GenesysXBlock": {
                    "GENESYS_CONFIG_ID": "YOUR API KEY GOES HERE"
                }
            },
        """
        return self.get_xblock_settings().get('GENESYS_CONFIG_ID', '')
        # return 'harambee-staging'

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
        return self.get_xblock_settings().get('GENESYS_BASE_URL', '')
        # return 'https://api-rest.genesysonline.net/'


    @property
    def api_invitation_url(self):

        return "{}invitations/{}".format(
            self.api_base_url, 
            self.api_configuration_id
        )

    @property
    def api_results_url(self):

        return "{}/results/{}?respondentId={}".format(
            self.api_base_url, 
            self.api_configuration_id,
            self.respondent_id
        )

    @property
    def get_headers(self):
        """
        """
        
        return self.get_xblock_settings().get('GENESYS_HEADERS', '')

    def api_invitation_params(self, user):
        """
        Define the Genesys invitation params sent to the Genesys invitations
        endpoint
        """
        # Check the user has a first and last name, and gender defined in profile
        if user.profile.gender is None:
            user.profile.gender = 'o'
            user.save()
        if not user.first_name or not user.last_name:
            user.first_name = user.profile.name.split(' ')[0]
            user.last_name = user.profile.name.split(' ')[-1]
            user.save()
        
        params = {
            "respondentFirstName":user.first_name,
            "respondentFamilyName":user.last_name,
            "respondentGender": user.profile.gender,
            "respondentEmailAddress": user.email,
            "questionnaireId": self.questionnaire_id, 
            "externalId": self.external_id, 
            "expiryDate": self.expiry_date
        }

        data = json.dumps(params)
        return data

    def get_genesys_invitation(self, user):
        """
        This function sends a request to the Genesys invitations endpoint.
        It raises an Exception is the request is not successful.
        """
        invitation = requests.post(
            url=self.api_invitation_url,
            headers=self.get_headers,
            data=self.api_invitation_params(user),
            
        )

        if invitation.ok:
            self.invitation_id = invitation.json()['invitationId']
            self.respondent_id = invitation.json()['respondentId']
            self.invitation_url = invitation.json()['invitationUrl']
            self.invitation_successful = True
        
            return {
                'invitation_id': self.invitation_id,
                'respondent_id': self.respondent_id,
                'invitation_url': self.invitation_url
            }
        else:
            raise Exception('There was an error with the Genesys invitations endpoint. {}'.format(str(invitation.text)))

        
    def get_genesys_test_result(self):
        """
        Using the Genesys respondent ID, it checks for an fetches the respondents test results
        using the Genesys results endpoint
        """
        result = requests.get(
            url=self.api_results_url,
            headers=self.get_headers
        )

        if result.ok:
            self.test_completed = True
            self.invitation_successful = True
            # set the score in the user state
            self.score = self.get_individual_test_scores(result)
            # publish the raw_earned and raw_possible score
            individual_scores = self.extract_earned_test_scores(result)
            calculated_total_score = self.calculate_score(result)
            self.publish_grade(score=calculated_total_score)
        else:
            raise Exception('The was an error with the Genesys results endpoint. {}'.format(str(result.text)))

    def get_test_total(self):
        """
        Using the total scores for the tests specified in Studio settings, tally
        up the sum of the test scores.
        """
        total_test_score = 0.0
        for test_score in self.test_id_list:
            total_test_score += float(test_score[1])

        return total_test_score

    def get_individual_test_scores(self, result):
        """
        Using the result obtained from get_genesys_test_result(), clean up the
        JSON and return a tidy dictionary for all the individual test results.
        """
        individual_test_scores = {}
        cleaned_results = {}
        result_dict = json.loads(result.text)
        result_list = result_dict[0]['results']

        for i in range(len(result_list)):
            cleaned_results[result_list[i]['testId']] = result_list[i]['scales'][0]['raw']

        for i in range(len(self.test_id_list)):
            individual_test_scores[self.test_id_list[i][0]] = float(self.test_id_list[i][1])

        final_scores = {}
        for key, value in cleaned_results.items():
            try:
                final_scores[str(key)] = (value, individual_test_scores[key])
            except KeyError as e:
                logger.error(str(e))
                final_scores[str(key)] = 'Test ID {} does not exist in results.'.format(str(key))

        return final_scores


    def extract_earned_test_scores(self, result):
        """
        Using the result obtained from get_genesys_test_result(), clean up the
        JSON and return the SUM of score earned for all tests specified in 
        test_id_list
        """
        cleaned_results = {}
        result_dict = json.loads(result.text)
        result_list = result_dict[0]['results']
        earned_test_score = 0.0

        # Total the test score
        for i in range(len(result_list)):
            earned_test_score += result_list[i]['scales'][0]['raw']

        return earned_test_score


    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the GenesysXBlock, shown to students
        when viewing courses.
        """
        no_name = False
        studio_runtime = False
        # Check if the runtime is cms or lms
        if settings.ROOT_URLCONF == 'cms.urls':
            studio_runtime = True
        # If no invitation has been received, call Genesys invitations endpoint
        try:
            user =  self.runtime.get_real_user(self.runtime.anonymous_student_id)
            print type(user.first_name)
            if not user.first_name or not user.last_name:
                no_name = True
        except Exception as e:
            logger.error(str(e))

        if self.respondent_id is None:
            try:
                invitation = self.get_genesys_invitation(user)
            except Exception as e:
                logger.error(str(e))
        else:
        # If an invitation has been received,
        # try fetch the results, ideally this should happen when the webhook is  POSTed to
            try:
                result = self.get_genesys_test_result()
            except Exception as e:
                logger.error(str(e))


        student_account_url = reverse('account_settings')

        context = {
            "no_name": no_name,
            "invitation_successful": self.invitation_successful,
            "src_url": self.invitation_url,
            "display_name": self.display_name,
            "instruction": self.instruction,
            "start_now": self.start_now,
            "completed": self.test_completed,
            "test_started": self.test_started,
            "studio_runtime": studio_runtime,
            "completed_message": self.completed_message,
            "student_account_url": student_account_url,
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
        context = {
            'fields': [],
            'test_id_list': self.test_id_list,

        }
        
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            if field.scope not in (Scope.content, Scope.settings):
                    logger.error(
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

    def set_score(self, score):     
        """       
        Sets the internal score for the problem. This is not derived directly     
        from the internal LCP in keeping with the ScorableXBlock spec.        
        """ 
        result = self.get_genesys_test_result()      
        earned = self.extract_earned_test_scores(result)
        possible = self.get_test_total() 
        return Score(raw_earned=earned, raw_possible=possible)


    def calculate_score(self, result):
        """
        Calculate a new raw score based on the state of the problem.
        This method should not modify the state of the XBlock.
        Returns:
            Score(raw_earned=float, raw_possible=float)
        """
        earned =  self.extract_earned_test_scores(result)
        possible = self.get_test_total()
        return Score(raw_earned=earned, raw_possible=possible)

    def publish_grade(self, score=None):
        """
        Publishes the student's current grade to the system as an event
        """
        if score is None:
            try:
                result = self.get_genesys_test_result()
                score = Score(earned=self.extract_earned_test_scores(result), possible=self.get_test_total())
            except Exception as e:
                logger.error(str(e))

        self.runtime.publish(
            self,
            'grade',
            {
                'value': score.raw_earned,
                'max_value': score.raw_possible,
            }
        )

        return {'grade': score.raw_earned, 'max_grade': score.raw_possible}

    @XBlock.json_handler
    def test_started_handler(self, data, suffix=''):

        '''
        This is a XBlock json handler for the async pdf download
        '''
        
        self.test_started = True
        return {"started": True}

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
