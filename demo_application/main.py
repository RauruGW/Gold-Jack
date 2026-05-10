import streamlit as st
import cv2
import numpy as np
from utils.game_logic import Game, GameMode, BlackjackHand, BasicStrategy
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
        st.session_state.language = "es"
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
    if "num_players_detected" not in st.session_state:
        st.session_state.num_players_detected = 0
    if "confidence_threshold" not in st.session_state:
        st.session_state.confidence_threshold = 0.4

def change_language():
    """Change the language in session state."""
    st.session_state.texts = Texts(language=st.session_state.language)


def detect_from_image(detector, uploaded_file, num_players, confidence=0.4):
    texts = st.session_state.texts

    if uploaded_file is None:
        st.warning(texts.get("upload_image"))
        return

    file_bytes = uploaded_file.read()
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    max_dimension = 1920
    height, width = image.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Predict cards with coordinates
    detections, coordinates, boxes = detector.predict(image, conf=confidence)

    # Group cards by player position
    if detections:
        num_clusters = num_players + 1
        player_groups, player_labels = detector.group_cards_by_position(detections, coordinates, boxes, num_clusters=num_clusters)

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
        st.session_state.num_players_detected = num_clusters - 1
    else:
        st.session_state.current_image = image
        st.session_state.detection_status = "error"
        st.session_state.detection_message = texts.get("no_cards_detected")
        st.session_state.player_groups = {}
        st.session_state.all_detections = []
        st.session_state.num_players_detected = 0



def main():
    initialize_session_state()
    texts = st.session_state.texts
    detector = CardGameDetector(MODEL_PATH, CLASS_NAMES)

    st.set_page_config(page_title=texts.get("page_title"), layout="wide")
    st.title(texts.get("title"))


    subcol1, subcol2 = st.columns([9, 1])

    with subcol1:
        st.subheader(texts.get("stats_actions"))

    with subcol2:
        if st.button("EN / ES"):
            st.session_state.language = "es" if st.session_state.language == "en" else "en"
            change_language()
            st.rerun()


    sub_col1, sub_col2, sub_col3 = st.columns([2, 1, 1])
    with sub_col1:
        uploaded_image = st.file_uploader(texts.get("upload_image"), type=["jpg", "jpeg", "png", "bmp"])

    with sub_col2:
        num_players = st.number_input(texts.get("num_players"), min_value=1, value=1, step=1)

    with sub_col3:
        st.session_state.confidence_threshold = st.slider(
            "Confianza",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.confidence_threshold,
            step=0.05,
            format="%.2f"
        )

    if uploaded_image is not None:
        if st.button(texts.get("take_snapshot")):
            detect_from_image(detector, uploaded_image, num_players, confidence=st.session_state.confidence_threshold)
            st.rerun()

    st.markdown("---")

    if st.session_state.player_groups:
        st.subheader(texts.get("players_detected"))

        st.text(f"{st.session_state.num_players_detected} {texts.get('players_detected_debug')}" if st.session_state.num_players_detected > 0 else texts.get("no_dealer_detected"))

        parsed_groups = {
            pid: detector.parse_cards(cards_raw)
            for pid, cards_raw in st.session_state.player_groups.items()
        }

        # Dealer = the group with exactly 1 card detected
        dealer_candidates = [pid for pid, cards in parsed_groups.items() if len(cards) == 1]
        dealer_id = dealer_candidates[0] if len(dealer_candidates) == 1 else None

        for player_id, cards in parsed_groups.items():
            role = "🎩 Dealer" if player_id == dealer_id else f"👤 {texts.get('player') } {player_id + 1}"
            cards_str = ", ".join(str(c) for c in cards) if cards else texts.get("no_cards_detected")
            st.write(f"**{role}**: {cards_str}")

        st.markdown("---")
        st.subheader(texts.get("scoring_options"))

        dealer_cards = parsed_groups[dealer_id] if dealer_id is not None else []

        if not dealer_cards:
            st.warning(texts.get("no_dealer_detected"))
        else:
            dealer_upcard = dealer_cards[0]
            d_val = BasicStrategy.dealer_upcard_value(dealer_upcard)

            for pid in [p for p in parsed_groups if p != dealer_id]:
                cards = parsed_groups[pid]
                st.write(f"**👤 {texts.get('player')} {pid + 1}**")
                if len(cards) < 2:
                    st.warning(texts.get("not_enough_cards"))
                else:
                    player_hand = BlackjackHand(cards)
                    p_total, p_soft = player_hand.get_value()
                    soft_label = " (Soft)" if p_soft else ""
                    st.write(f"{texts.get('player_hand')}: {p_total}{soft_label} — {texts.get('dealer_upcard')}: {dealer_upcard} ({d_val})")
                    action = BasicStrategy.recommend(player_hand, dealer_upcard)
                    st.success(f"{BasicStrategy.ACTION_EMOJI[action]} **{action}** — {BasicStrategy.ACTION_DESC[action]}")

        st.markdown("---")

    # Image
    if st.session_state.current_image is not None:
        display_img = cv2.cvtColor(st.session_state.current_image, cv2.COLOR_BGR2RGB)
        st.image(display_img, channels="RGB", caption=texts.get("image_analyzed"), use_container_width=True)

        if st.session_state.detection_status == "success":
            st.success(st.session_state.detection_message)
        elif st.session_state.detection_status == "error":
            st.error(st.session_state.detection_message)
    
        st.write("---")


if __name__ == "__main__":
    main()