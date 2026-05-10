import time
from collections import Counter
import torch
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from ultralytics import YOLO
from utils.game_logic import Card, Suit, Value, Game, GameMode

_original_load = torch.load

def _patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)

torch.load = _patched_load


class CardGameDetector:
    def __init__(self, model_path, class_names):
        self.model = YOLO(model_path, verbose=False)
        self.class_names = class_names

    def aggregate_detections(self, detections):
        counts = Counter(detections)
        print(counts)
        return [key for key, count in counts.items() if count >= 3]

    def capture_and_process_frames(self, cap, num_frames=10, interval=0.2):
        all_detections = []
        for _ in range(num_frames):
            ret, frame = cap.read()
            if ret:
                results = self.model(frame, imgsz=416)
                frame_detections = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        frame_detections.append(self.class_names[cls])
                all_detections.append(frame_detections)
                time.sleep(interval)
        detections = self.aggregate_detections(all_detections)
        return detections

    def capture_a_frame(self, cap):
        ret, frame = cap.read()
        if ret:
            results = self.model(frame, imgsz=416)
            frame_detections = []
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    frame_detections.append(self.class_names[cls])
            return frame_detections
        return []

    def parse_card(self, detected_card):
        value = detected_card[:-1]
        suit = detected_card[-1]
        try:
            return Card(Value(value.upper()), Suit(suit))
        except ValueError:
            return None

    def parse_cards(self, detected_cards):
        all_cards = [self.parse_card(card) for card in detected_cards]
        parsed_cards = [parsed_card for parsed_card in all_cards if parsed_card is not None]
        return parsed_cards

    def predict(self, image):
        """Predict cards with their coordinates and merge duplicate corners."""
        results = self.model(image, conf=0.35, imgsz=416)

        # Diccionario para unificar las esquinas de una misma carta
        merged_cards = {}

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                card_name = self.class_names[cls]
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                if card_name not in merged_cards:
                    merged_cards[card_name] = [x1, y1, x2, y2]
                else:
                    # Expandir la caja delimitadora usando los mínimos y máximos de las esquinas
                    cx1, cy1, cx2, cy2 = merged_cards[card_name]
                    merged_cards[card_name] = [
                        min(cx1, x1), min(cy1, y1),
                        max(cx2, x2), max(cy2, y2)
                    ]

        detections = []
        coordinates = []
        boxes_list = []

        # Convertir el diccionario unificado en las listas de salida
        for card_name, box in merged_cards.items():
            x1, y1, x2, y2 = box

            # Obtener el centro geométrico de la carta física real
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2

            detections.append(card_name)
            coordinates.append([x_center, y_center])
            boxes_list.append([x1, y1, x2, y2])

        return detections, coordinates, boxes_list

    def auto_num_clusters(self, coordinates, max_k=8, eps_factor=1.6):
        """Estimate the number of players (including dealer) from card positions.

        The dealer may hold a single card, so its nearest neighbor belongs to a
        different hand and inflates the median nearest-neighbor distance. We use
        the 25th percentile to recover the true intra-hand spacing, and DBSCAN
        with min_samples=1 so an isolated dealer card forms its own cluster
        instead of being absorbed by the closest player. Orientation-agnostic.
        """
        if len(coordinates) <= 1:
            return max(1, len(coordinates))

        coords_arr = np.array(coordinates)
        diff = coords_arr[:, None, :] - coords_arr[None, :, :]
        dists = np.sqrt((diff ** 2).sum(axis=2))
        np.fill_diagonal(dists, np.inf)

        nn = dists.min(axis=1)
        intra_hand = float(np.percentile(nn, 25))

        labels = DBSCAN(eps=intra_hand * eps_factor, min_samples=1).fit_predict(coords_arr)
        return min(int(labels.max() + 1), max_k)

    def group_cards_by_position(self, detections, coordinates, boxes, num_clusters=2):
        """Group cards into player hands based on K-Means clustering.
        
        Args:
            detections: List of card names detected
            coordinates: List of [x, y] coordinates for each detection
            boxes: List of bounding boxes
            num_clusters: Total number of players (including dealer)
            
        Returns:
            Dictionary mapping player_id to list of cards, and a list of player_labels for each detection
        """
        if not coordinates:
            return {}, []

        coordinates = np.array(coordinates)
        num_clusters = min(num_clusters, len(coordinates))
        clustering = KMeans(n_clusters=num_clusters, random_state=89620, n_init='auto').fit(coordinates)
        labels = clustering.labels_
        
        players = {}
        player_labels = []
        for card, label in zip(detections, labels):
            if label not in players:
                players[label] = []
            players[label].append(card)
            player_labels.append(label)

        return dict(sorted(players.items())), player_labels
