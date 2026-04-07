import streamlit as st
import cv2
import numpy as np
from utils.game_logic import Game, GameMode
from utils.card_game_detector import CardGameDetector
from utils.constants import MODEL_PATH, CLASS_NAMES
from utils.text_constants import Texts


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "game" not in st.session_state:
        st.session_state.game = Game()
    if "cards_team_a" not in st.session_state:
        st.session_state.cards_team_a = []
    if "cards_team_b" not in st.session_state:
        st.session_state.cards_team_b = []
    if "team_a_last10" not in st.session_state:
        st.session_state.team_a_last10 = False
    if "current_game_mode_index" not in st.session_state:
        st.session_state.current_game_mode_index = 0
    if "language" not in st.session_state:
        st.session_state.language = "en"
    if "texts" not in st.session_state:
        st.session_state.texts = Texts(language=st.session_state.language)
    if "current_image" not in st.session_state:
        st.session_state.current_image = None
    if "detection_status" not in st.session_state:
        st.session_state.detection_status = None
    if "detection_message" not in st.session_state:
        st.session_state.detection_message = None
    if "player_groups" not in st.session_state:
        st.session_state.player_groups = {}
    if "all_detections" not in st.session_state:
        st.session_state.all_detections = []


def change_language():
    """Change the language in session state."""
    st.session_state.texts = Texts(language=st.session_state.language)


def display_team_scores():
    """Display the team scores table."""
    texts = st.session_state.texts
    team_a_scores = st.session_state.game.get_team_belotscore_history(0)
    team_b_scores = st.session_state.game.get_team_belotscore_history(1)

    table_data = [
        {texts.get("team_a"): team_a, texts.get("team_b"): team_b}
        for team_a, team_b in zip(team_a_scores, team_b_scores)
    ]
    st.table(table_data)


def detect_from_image(detector, uploaded_file):
    texts = st.session_state.texts
    
    if uploaded_file is None:
        st.warning("Por favor carga una imagen")
        return
    
    file_bytes = uploaded_file.read()
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Redimensionar la imagen para mejorar detección y visualización
    max_dimension = 600
    height, width = image.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Predict cards with coordinates
    detections, coordinates, boxes = detector.predict(image)

    # Group cards by player position
    if detections:
        player_groups, player_labels = detector.group_cards_by_position(detections, coordinates)

        # Draw bounding boxes with different colors per player
        colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (0, 0, 255),    # Red
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
            (255, 255, 0),  # Cyan
        ]

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            label = player_labels[i]
            color = colors[label % len(colors)]
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 4)
            cv2.putText(image, detections[i], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        st.session_state.current_image = image
        st.session_state.detection_status = "success"
        st.session_state.detection_message = texts.get("cards_detected")
        st.session_state.player_groups = player_groups
        st.session_state.all_detections = detections
    else:
        st.session_state.current_image = image
        st.session_state.detection_status = "error"
        st.session_state.detection_message = texts.get("no_cards_detected")
        st.session_state.player_groups = {}
        st.session_state.all_detections = []


def handle_game_mode_change(mode_choice):
    """Handle changes to the selected game mode."""
    texts = st.session_state.texts
    game_mode_map = {
        texts.get_modes()[0]: GameMode.ALL_TRUMPS,
        texts.get_modes()[1]: GameMode.NO_TRUMPS,
        texts.get_modes()[2]: GameMode.SPADES,
        texts.get_modes()[3]: GameMode.HEARTS,
        texts.get_modes()[4]: GameMode.DIAMONDS,
        texts.get_modes()[5]: GameMode.CLUBS,
    }

    if mode_choice != texts.get_modes()[st.session_state.current_game_mode_index]:
        st.session_state.game.change_gamemode(game_mode_map[mode_choice])
        st.session_state.current_game_mode_index = texts.get_modes().index(mode_choice)

        st.session_state.cards_team_a = st.session_state.game.sort_cards(st.session_state.cards_team_a)
        st.session_state.cards_team_b = st.session_state.game.sort_cards(st.session_state.cards_team_b)
        st.rerun()


def main():
    initialize_session_state()
    texts = st.session_state.texts
    detector = CardGameDetector(MODEL_PATH, CLASS_NAMES)

    st.set_page_config(page_title=texts.get("page_title"), layout="wide")
    st.title(texts.get("title"))

    col1, spacer, col2 = st.columns([1, 0.2, 2])
    with col1:
        st.subheader(texts.get("team_scores"))
        display_team_scores()

    with col2:
        subcol1, subcol2 = st.columns([9, 1])

        with subcol1:
            st.subheader(texts.get("stats_actions"))

        with subcol2:
            if st.button("🇬🇧 / 🇧🇬"):
                st.session_state.language = "bg" if st.session_state.language == "en" else "en"
                change_language()
                st.rerun()

        # Display current image if available
        if st.session_state.current_image is not None:
            display_img = cv2.cvtColor(st.session_state.current_image, cv2.COLOR_BGR2RGB)
            st.image(display_img, channels="RGB", caption=texts.get("image_analyzed"), use_container_width=True)

            # Display detection status message if available
            if st.session_state.detection_status == "success":
                st.success(st.session_state.detection_message)
            elif st.session_state.detection_status == "error":
                st.error(st.session_state.detection_message)
        
        st.write("---")
        
        # Display detected player groups
        if st.session_state.player_groups:
            st.subheader("Jugadores Detectados")
            for player_id, cards_raw in st.session_state.player_groups.items():
                # Parse and sort cards
                parsed_cards = st.session_state.game.sort_cards(
                    detector.parse_cards(cards_raw)
                )
                player_name = f"Jugador {player_id + 1}"
                cards_str = ", ".join(str(card) for card in parsed_cards) if parsed_cards else "Sin cartas"
                st.write(f"**{player_name}**: {cards_str}")
        else:
            st.write(
                f"{texts.get('cards_team_a')} - {st.session_state.game.get_points(st.session_state.cards_team_a, st.session_state.team_a_last10)} {texts.get('points')}:"
            )
            st.write(
                ", ".join(str(card) for card in st.session_state.cards_team_a) if st.session_state.cards_team_a else ""
            )
            st.write(
                f"{texts.get('cards_team_b')} - {st.session_state.game.get_points(st.session_state.cards_team_b, not st.session_state.team_a_last10)} {texts.get('points')}:"
            )
            st.write(
                ", ".join(str(card) for card in st.session_state.cards_team_b) if st.session_state.cards_team_b else ""
            )

        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            uploaded_image = st.file_uploader("Carga una imagen de cartas", type=["jpg", "jpeg", "png", "bmp"])
            if uploaded_image is not None:
                if st.button(texts.get("take_snapshot")):
                    detect_from_image(detector, uploaded_image)
                    st.rerun()

        with sub_col2:
            if st.button(texts.get("flip_cards")):
                st.session_state.cards_team_a, st.session_state.cards_team_b = (
                    st.session_state.cards_team_b,
                    st.session_state.cards_team_a,
                )
                st.rerun()

        st.markdown("---")

        st.subheader(texts.get("scoring_options"))

        mode_choice = st.selectbox(
            texts.get("game_mode"),
            texts.get_modes(),
            key="game_mode_select",
            index=st.session_state.current_game_mode_index,
        )

        handle_game_mode_change(mode_choice)

        team_a_bonus = st.number_input(texts.get("bonus_points_team_a"), min_value=0, step=1, key="bonus_a")
        team_b_bonus = st.number_input(texts.get("bonus_points_team_b"), min_value=0, step=1, key="bonus_b")

        bool_10 = st.checkbox(texts.get("team_a_last_10"), value=st.session_state.team_a_last10)

        if bool_10 != st.session_state.team_a_last10:
            st.session_state.team_a_last10 = bool_10
            st.rerun()

        sub_col1, sub_col2, sub_col3 = st.columns(3)

        with sub_col1:
            if st.button(texts.get("update_scores")):
                st.session_state.game.add_current_round_points(
                    taken_cards=st.session_state.cards_team_a,
                    team_index=0,
                    has_taken_last=st.session_state.team_a_last10,
                    bonuses_points=team_a_bonus,
                    enemy_bonuses_points=team_b_bonus,
                )
                st.success(texts.get("scores_updated"))
                st.rerun()
        with sub_col2:
            if st.button(texts.get("revert_last_round")):
                st.session_state.game.revert_last_round()
                st.success(texts.get("last_round_reverted"))
                st.rerun()

        with sub_col3:
            if st.button(texts.get("start_new_game")):
                st.session_state.game = Game()
                st.session_state.cards_team_a = []
                st.session_state.cards_team_b = []
                st.session_state.team_a_last10 = False
                st.success(texts.get("new_game_started"))
                st.rerun()


if __name__ == "__main__":
    main()
