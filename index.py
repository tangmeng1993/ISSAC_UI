from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher

app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ISSAC-702e5c96171c.json'
os.environ['DIALOGFLOW_PROJECT_ID'] = 'issac-b2751'




@app.route('/')
def index():
    print('here is main')
    return render_template('index.html')

@app.route('/test', methods=['POST'])
def get_movie_detail():
    print('here is get_movie_detail')
    data = request.get_json(silent=True,force=True)
    print(data['queryResult']['intent']['displayName'])

    try:

        movie = data['queryResult']['parameters']['movie']
        api_key = os.getenv('OMDB_API_KEY')
        
        movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
        movie_detail = json.loads(movie_detail)

        response =  """
            Title : {0}
            Released: {1}
            Actors: {2}
            Plot: {3}
        """.format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])
    except:
        response = "Could not get movie detail at the moment, please try again"
    
    reply = { "fulfillmentText": response }
    
    return jsonify(reply)

def detect_intent_texts(project_id, session_id, text,knowledge_base_id, language_code):
    import dialogflow_v2beta1 as dialogflow
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        
        query_input = dialogflow.types.QueryInput(text=text_input)
        
        knowledge_base_path = dialogflow.knowledge_bases_client.KnowledgeBasesClient.knowledge_base_path(project_id, knowledge_base_id)
        
        query_params = dialogflow.types.QueryParameters(knowledge_base_names=[knowledge_base_path])
        
        response = session_client.detect_intent(
            session=session, query_input=query_input,
            query_params=query_params)

        return response.query_result.fulfillment_text


@app.route('/send_message', methods=['POST'])
def send_message():
    print('here is send_message')
        
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message,"MzExMTU5MTUxODMyNzAxMzM3Ng", 'en')
    response_text = { "message":  fulfillment_text }
                        
    return jsonify(response_text)

# run Flask app
if __name__ == "__main__":
    app.run()