import time
from collections import Counter
import torch
import numpy as np
from sklearn.cluster import DBSCAN
from ultralytics import YOLO
from utils.game_logic import Card, Suit, Value, Game, GameMode
from scipy.spatial.distance import pdist

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
        results = self.model(image, conf=0.25, imgsz=416)

        # Diccionario para unificar las esquinas de una misma carta
        merged_cards = {}

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                card_name = self.class_names[cls]
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                if card_name not in merged_cards:
                    merged_cards[card_name] = []
                
                merged_cards[card_name].append({
                    'box': [x1, y1, x2, y2],
                    'center': [(x1 + x2) / 2, (y1 + y2) / 2]
                })

        detections = []
        coordinates = []
        boxes_list = []

        # Convertir el diccionario unificado en las listas de salida
        for card_name, detections_list in merged_cards.items():
            # Promediar centros de duplicados
            avg_center = np.mean([d['center'] for d in detections_list], axis=0)
            
            # Usar el box que está más cerca del promedio
            closest_idx = np.argmin([
                np.linalg.norm(np.array(d['center']) - avg_center) 
                for d in detections_list
            ])
            closest_box = detections_list[closest_idx]['box']
            
            detections.append(card_name)
            coordinates.append(avg_center.tolist())
            boxes_list.append(closest_box)

        return detections, coordinates, boxes_list

    def group_cards_by_position(self, detections, coordinates, boxes_list, eps=250, min_samples=1):
        """Group cards into player hands based on spatial proximity.
        
        Args:
            detections: List of card names detected
            coordinates: List of [x, y] coordinates for each detection
            eps: Maximum distance between cards in same group (pixels)
            min_samples: Minimum cards to form a group
            
        Returns:
            Dictionary mapping player_id to list of cards, and a list of player_labels for each detection
        """
        if not coordinates or len(boxes_list) < 2:
            return {}, []
        
        coordinates_array = np.array(coordinates)
        distances = pdist(coordinates_array)

        # Estrategia: buscar el mayor salto en la PRIMERA MITAD de las distancias
        if len(distances) == 1:
            eps = distances[0] * 0.8
        else:
            distances_sorted = np.sort(distances)
            n = len(distances_sorted)
            
            # Calcular diferencias consecutivas
            diffs = np.diff(distances_sorted)
            
            # Buscar el máximo salto solo en la primera mitad
            midpoint = n // 2
            first_half_diffs = diffs[:midpoint]
            
            if len(first_half_diffs) > 0:
                max_jump_in_first_half = np.argmax(first_half_diffs)
                eps = distances_sorted[max_jump_in_first_half]
            else:
                # Si no hay primera mitad (muy pocas distancias), usar percentil
                eps = np.percentile(distances, 40)

        clustering = DBSCAN(eps=eps, min_samples=1).fit(coordinates_array)
        labels = clustering.labels_
        
        players = {}
        player_labels = []
        
        for card, label in zip(detections, labels):
            if label not in players:
                players[label] = []
            
            players[label].append(card)
            player_labels.append(label)

        return dict(sorted(players.items())), player_labels