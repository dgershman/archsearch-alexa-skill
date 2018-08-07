import requests
import json
from datetime import datetime

SKILL_NAME = "ARCHSEARCH"
HELP_MESSAGE = "help message"
HELP_REPROMPT = "help reprompt"
STOP_MESSAGE = "Goodbye!"
FALLBACK_MESSAGE = "fallback message"
FALLBACK_REPROMPT = 'fallback reprompt'
days_of_the_week = ["", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def lambda_handler(event, context):
    """  App entry point  """

    #print(event)

    if event['session']['new']:
        on_session_started()

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended()


def on_intent(request, session):
    """ called on receipt of an Intent  """
    intent_name = request['intent']['name']

    # process the intents
    if intent_name == "ArchsearchFindMeetingIntent":
        return get_meetings(request['intent']['slots']['Location']['value'])
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.StopIntent":
        return get_stop_response()
    elif intent_name == "AMAZON.CancelIntent":
        return get_stop_response()
    elif intent_name == "AMAZON.FallbackIntent":
        return get_fallback_response()
    else:
        print("invalid Intent reply with help")
        return get_fallback_response()


def welcome_message():
    """ get and return a random fact """
    speechOutput = "Welcome To Archsearch.  You can search for a location now."
    cardcontent = speechOutput
    return response(speech_response_with_card(SKILL_NAME, speechOutput,
                                                          cardcontent, False))


def get_location(location):
    print(location)
    speechOutput = "Searching for meetings in {}.".format(location)
    cardcontent = speechOutput
    return response(speech_response_with_card(SKILL_NAME, speechOutput,
                                                          cardcontent, False))

def get_meetings(location):
    speechResponse = ''
    coordinates = get_coordinates_for_address(location)
    max_results = 5
    today = 1 if datetime.today().weekday() == 6 else datetime.today().weekday() + 2
    tomorrow = 1 if today == 6 else today + 2
    get_meetings_from_yap = requests.get('https://archsearch.org/yap/api/getMeetings.php?latitude={}&longitude={}&results_count={}&today={}&tomorrow={}'
        .format(coordinates['latitude'], coordinates['longitude'], max_results, today, tomorrow))
    meetings = json.loads(get_meetings_from_yap.text)['filteredList']
    x = 1
    for meeting in meetings:
        municipality = " , " + meeting['location_municipality'] if meeting['location_municipality'] != "" else ""
        province = " , " + meeting['location_province'] if meeting['location_province'] != "" else ""

        this_response= "Result Number " + str(x) + ". " + \
            meeting['meeting_name'] + ". " + " Starts at " + \
            days_of_the_week[int(meeting['weekday_tinyint'])] + " " + datetime.strptime(meeting['start_time'], "%H:%M:%S").strftime("%I:%M %p") + ". " + \
            meeting['location_street'] + municipality + province + ".  "

        speechResponse = speechResponse + this_response
        if x == max_results:
            break
        x += 1

    return response(speech_response_prompt(speechResponse, speechResponse, False))


def get_coordinates_for_address(address):
    if len(address) > 0:
        map_details_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}&components={}'
                                   .format('', address, 'country:us'))
        map_details = json.loads(map_details_response.text)
        if len(map_details['results']) > 0:
            geometry = map_details['results'][0]['geometry']['location']
            return { "latitude" :  geometry['lat'], "longitude" : geometry['lng'] }


def get_help_response():
    """ get and return the help string  """

    speech_message = HELP_MESSAGE
    return response(speech_response_prompt(speech_message, speech_message, False))


def get_launch_response():
    """ get and return the help string  """

    return welcome_message()


def get_stop_response():
    """ end the session, user wants to quit the game """

    speech_output = STOP_MESSAGE
    return response(speech_response(speech_output, True))


def get_fallback_response():
    """ end the session, user wants to quit the game """

    speech_output = FALLBACK_MESSAGE
    return response(speech_response(speech_output, False))


def on_session_started():
    """" called when the session starts  """
    #print("on_session_started")


def on_session_ended():
    """ called on session ends """
    #print("on_session_ended")


def on_launch(request):
    """ called on Launch, we reply with a launch message  """

    return get_launch_response()


# --------------- Speech response handlers -----------------

def speech_response(output, endsession):
    """  create a simple json response  """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }


def dialog_response(endsession):
    """  create a simple json response with card """

    return {
        'version': '1.0',
        'response':{
            'directives': [
                {
                    'type': 'Dialog.Delegate'
                }
            ],
            'shouldEndSession': endsession
        }
    }


def speech_response_with_card(title, output, cardcontent, endsession):
    """  create a simple json response with card """

    return {
        'card': {
            'type': 'Simple',
            'title': title,
            'content': cardcontent
        },
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }


def response_ssml_text_and_prompt(output, endsession, reprompt_text):
    """ create a Ssml response with prompt  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }


def speech_response_prompt(output, reprompt_text, endsession):
    """ create a simple json response with a prompt """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': endsession
    }


def response(speech_message):
    """ create a simple json response  """
    return {
        'version': '1.0',
        'response': speech_message
    }


#get_meetings("Willow Spring North Carolina")