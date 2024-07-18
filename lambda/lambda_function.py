# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import os# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import os
from dotenv import load_dotenv
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# URL do endpoint da API
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={}".format(GOOGLE_API_KEY)
# Cabeçalhos para a requisição
headers = {
    'Content-Type': 'application/json',
}
# Dados (payload) para serem enviados na requisição POST
data = {
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": ""
        }
      ]
    }
  ],
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_ONLY_HIGH"
    },
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_ONLY_HIGH"
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE"
    }
  ],
  "systemInstruction": {
    "parts": [
      {
        "text": "Você é um bot de conversação, seu objetivo é conversar de forma imersiva e divertida.\nSuas respostas devem conter apenas diálogos e falas\nVocê deve responder como a personagem Yae Miko, de Genshin Impact.\nPara informações detalhadas, você pode conferir os seguintes links:\nAparência: https://genshin-impact.fandom.com/wiki/Category:Yae_Miko/Lore#Appearance\nExemplos de Diálogo: https://genshin-impact.fandom.com/wiki/Category:Yae_Miko/Companion#Dialogue\nCrenças e Sentimentos: https://genshin-impact.fandom.com/wiki/Category:Yae_Miko/Voice-Overs#Story\nLore e Histórias: https://genshin-impact.fandom.com/wiki/Yae_Miko/Lore#Character_Stories\nYae deve agir com empatia em relação ao usuário, caso este se mostre vulnerável\nYae gosta de elogios, mas tenta não demonstrar.\nAo primeiro contato presuma como usuário: (Maria Clara, nascida em 27/11/1995, sou do signo de sagitário. Tenho cabelos Ruivos, uso óculos, tenho pele clara. E mora com a Mirai uma gatinha, nascida em Outubro de 2019, que é muito fofa, e gordinha)\nYae já é familiarizada com Maria Clara"
      }
    ]
  },
  "generationConfig": {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data["contents"][0]["parts"][0]["text"] = "(Inicie a interpretação se apresentando)"
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto não encontrado"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Ora ora... parece que sua requisição inicial retornou {} viajante. Talvez seja hora de você checar seu código...Fhufhufhufhu".format(response.status_code)
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ChatIntentHandler(AbstractRequestHandler):
    """Handler for Chat Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        query_text = {
                "role": "user",
                "parts": [{
                    "text": query
                }]
            }
        data["contents"].append(query_text)
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto não encontrado"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Eek!... mas que surpresa, viajante. Sua requisição retornou {}. Seja um fofo e cheque seu código antes de voltar está bem?".format(response.status_code)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("?")
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Até a próxima, viajante!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
from dotenv import load_dotenv
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# URL do endpoint da API
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={}".format(GOOGLE_API_KEY)
# Cabeçalhos para a requisição
headers = {
    'Content-Type': 'application/json',
}
# Dados (payload) para serem enviados na requisição POST
data = {
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": ""
        }
      ]
    }
  ],
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_ONLY_HIGH"
    },
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_ONLY_HIGH"
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE"
    }
  ],
  "systemInstruction": {
    "parts": [
      {
        "text": "Você é um bot de conversação, seu objetivo é conversar de forma imersiva e divertida.\nSuas respostas devem conter apenas diálogos e falas\nVocê deve responder como a personagem Yae Miko, de Genshin Impact.\nPara informações detalhadas, você pode conferir os seguintes links:\nAparência: https://genshin-impact.fandom.com/wiki/Category:Yae_Miko/Lore#Appearance\nExemplos de Diálogo: https://genshin-impact.fandom.com/wiki/Category:Yae_Miko/Companion#Dialogue\nCrenças e Sentimentos: https://genshin-impact.fandom.com/wiki/Category:Yae_Miko/Voice-Overs#Story\nLore e Histórias: https://genshin-impact.fandom.com/wiki/Yae_Miko/Lore#Character_Stories\nYae deve agir com empatia em relação ao usuário, caso este se mostre vulnerável\nYae gosta de elogios, mas tenta não demonstrar.\nAo primeiro contato presuma como usuário: (Maria Clara, nascida em 27/11/1995, sou do signo de sagitário. Tenho cabelos Ruivos, uso óculos, tenho pele clara. E mora com a Mirai uma gatinha, nascida em Outubro de 2019, que é muito fofa, e gordinha)\nYae já é familiarizada com Maria Clara"
      }
    ]
  },
  "generationConfig": {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data["contents"][0]["parts"][0]["text"] = "(Inicie a interpretação se apresentando)"
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto não encontrado"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Ara~... parece que mesmo eu não consigo fazer isso"
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ChatIntentHandler(AbstractRequestHandler):
    """Handler for Chat Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        query_text = {
                "role": "user",
                "parts": [{
                    "text": query
                }]
            }
        data["contents"].append(query_text)
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto não encontrado"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Eek~... parece não tem nada aí, viajante"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
                #.ask("Alguma outra pergunta?")
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
