import logging

logger = logging.getLogger(__name__)

def log_question_creation(quiz_session_id, species_id, observation_id, image_id):
    logger.info(f"Quiz {quiz_session_id}: Created question with Species {species_id}, Observation {observation_id}, Image {image_id}")

def log_observation_selection(quiz_session_id, species_id, observation_id):
    logger.info(f"Quiz {quiz_session_id}: Selected Observation {observation_id} for Species {species_id}")