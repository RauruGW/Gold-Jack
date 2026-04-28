# constants.py
class Texts:
    def __init__(self, language="en"):
        self.language = language
        self.texts = {
            "en": {
                "page_title": "GoldJack - Blackjack Assistant",
                "title": "GoldJack - Intelligent Blackjack Assistant - Card Detection",
                "team_scores": "Hand History",
                "stats_actions": "Game Analysis",
                "team_a": "Your Hand",
                "team_b": "Dealer's Hand",
                "cards_team_a": "Your Cards",
                "cards_team_b": "Dealer's Cards",
                "points": "points",
                "take_snapshot": "Detect Cards",
                "capturing_cards": "Detecting cards... Please wait.",
                "cards_detected": "Cards detected successfully!",
                "no_cards_detected": "No cards detected. Please try again.",
                "flip_cards": "Swap Hands",
                "scoring_options": "Decision Analysis",
                "game_mode": "Strategy",
                "bonus_points_team_a": "Bet (Your Hand)",
                "bonus_points_team_b": "Bet (Dealer)",
                "team_a_last_10": "Did you win the last hand?",
                "update_scores": "Record Result",
                "scores_updated": "Result recorded successfully!",
                "revert_last_round": "Undo Last Hand",
                "start_new_game": "New Session",
                "new_game_started": "New session started successfully!",
                "game_modes": ["Hit", "Stand", "Double", "Split"],
                "image_analyzed": "Analyzed image",
            },
            "es": {
                "page_title": "GoldJack - Asistente de Blackjack",
                "title": "GoldJack - Asistente Inteligente de Blackjack - Detección de Cartas",
                "team_scores": "Historial de Manos",
                "stats_actions": "Análisis de Juego",
                "team_a": "Tu Mano",
                "team_b": "Mano del Crupier",
                "cards_team_a": "Tus Cartas",
                "cards_team_b": "Cartas del Crupier",
                "points": "puntos",
                "take_snapshot": "Detectar Cartas",
                "capturing_cards": "Detectando cartas... Por favor espera.",
                "cards_detected": "¡Cartas detectadas correctamente!",
                "no_cards_detected": "No se detectaron cartas. Por favor intenta de nuevo.",
                "flip_cards": "Intercambiar Manos",
                "scoring_options": "Análisis de Decisión",
                "game_mode": "Estrategia",
                "bonus_points_team_a": "Apuesta (Tu Mano)",
                "bonus_points_team_b": "Apuesta (Crupier)",
                "team_a_last_10": "¿Ganaste la última mano?",
                "update_scores": "Registrar Resultado",
                "scores_updated": "¡Resultado registrado!",
                "revert_last_round": "Deshacer Última Mano",
                "start_new_game": "Nueva Sesión",
                "new_game_started": "¡Nueva sesión iniciada!",
                "game_modes": ["Hit", "Stand", "Double", "Split"],
                "image_analyzed": "Imagen analizada",
            },
        }

    def get(self, key):
        return self.texts[self.language].get(key, key)

    def get_modes(self):
        return self.texts[self.language]["game_modes"]
