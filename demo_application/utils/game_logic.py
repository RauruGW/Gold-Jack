from enum import Enum


class Suit(Enum):
    SPADES = "s"
    HEARTS = "h"
    DIAMONDS = "d"
    CLUBS = "c"


class Value(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


class GameMode(Enum):
    ALL_TRUMPS = "a"
    NO_TRUMPS = "n"
    SPADES = "s"
    HEARTS = "h"
    DIAMONDS = "d"
    CLUBS = "c"


class CardTrumpOrder(Enum):
    TWO = 8
    THREE = 9
    FOUR = 10
    FIVE = 11
    SIX = 12
    JACK = 0
    NINE = 1
    ACE = 2
    TEN = 3
    KING = 4
    QUEEN = 5
    EIGHT = 6
    SEVEN = 7


class CardNonTrumpOrder(Enum):
    TWO = 8
    THREE = 9
    FOUR = 10
    FIVE = 11
    SIX = 12
    ACE = 0
    TEN = 1
    KING = 2
    QUEEN = 3
    JACK = 4
    NINE = 5
    EIGHT = 6
    SEVEN = 7


class CardTrumpValue(Enum):
    TWO = 0
    THREE = 0
    FOUR = 0
    FIVE = 0
    SIX = 0
    SEVEN = 0
    EIGHT = 0
    QUEEN = 3
    KING = 4
    TEN = 10
    ACE = 11
    NINE = 14
    JACK = 20


class CardNonTrumpValue(Enum):
    TWO = 0
    THREE = 0
    FOUR = 0
    FIVE = 0
    SIX = 0
    SEVEN = 0
    EIGHT = 0
    NINE = 0
    JACK = 2
    QUEEN = 3
    KING = 4
    TEN = 10
    ACE = 11


class BlackjackHand:
    def __init__(self, cards):
        self.cards = cards

    def get_value(self):
        """Returns (best_value, is_soft). is_soft=True if an Ace counts as 11."""
        total = 0
        aces = 0
        for card in self.cards:
            if card.value == Value.ACE:
                aces += 1
                total += 11
            elif card.value in (Value.JACK, Value.QUEEN, Value.KING):
                total += 10
            else:
                total += int(card.value.value)
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total, aces > 0

    def is_blackjack(self):
        total, _ = self.get_value()
        return len(self.cards) == 2 and total == 21

    def is_bust(self):
        total, _ = self.get_value()
        return total > 21

    def is_pair(self):
        if len(self.cards) != 2:
            return False
        def bj_val(card):
            if card.value in (Value.JACK, Value.QUEEN, Value.KING):
                return 10
            if card.value == Value.ACE:
                return 11
            return int(card.value.value)
        return bj_val(self.cards[0]) == bj_val(self.cards[1])

    def pair_card_value(self):
        c = self.cards[0]
        if c.value in (Value.JACK, Value.QUEEN, Value.KING):
            return 10
        if c.value == Value.ACE:
            return 11
        return int(c.value.value)


class BasicStrategy:
    """Optimal basic strategy (6-8 decks, dealer stands soft 17)."""

    HARD = {
        **{t: {d: "HIT" for d in range(2, 12)} for t in range(4, 9)},
        9:  {2:"HIT",  3:"DOUBLE",4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        10: {2:"DOUBLE",3:"DOUBLE",4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"DOUBLE",8:"DOUBLE",9:"DOUBLE",10:"HIT",11:"HIT"},
        11: {d:"DOUBLE" for d in range(2, 12)},
        12: {2:"HIT",  3:"HIT", 4:"STAND",5:"STAND",6:"STAND",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        13: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        14: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        15: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        16: {2:"STAND",3:"STAND",4:"STAND",5:"STAND",6:"STAND",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        **{t: {d: "STAND" for d in range(2, 12)} for t in range(17, 22)},
    }

    SOFT = {
        2:  {2:"HIT",  3:"HIT", 4:"HIT",   5:"DOUBLE",6:"DOUBLE",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        3:  {2:"HIT",  3:"HIT", 4:"HIT",   5:"DOUBLE",6:"DOUBLE",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        4:  {2:"HIT",  3:"HIT", 4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        5:  {2:"HIT",  3:"HIT", 4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"HIT", 8:"HIT", 9:"HIT", 10:"HIT",11:"HIT"},
        6:  {2:"HIT",  3:"DOUBLE",4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"HIT",8:"HIT",9:"HIT",10:"HIT",11:"HIT"},
        7:  {2:"STAND",3:"DOUBLE",4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"STAND",8:"STAND",9:"HIT",10:"HIT",11:"HIT"},
        8:  {d:"STAND" for d in range(2, 12)},
        9:  {d:"STAND" for d in range(2, 12)},
        10: {d:"STAND" for d in range(2, 12)},
    }

    PAIRS = {
        2:  {2:"SPLIT",3:"SPLIT",4:"SPLIT",5:"SPLIT",6:"SPLIT",7:"SPLIT",8:"HIT",  9:"HIT",  10:"HIT",  11:"HIT"},
        3:  {2:"SPLIT",3:"SPLIT",4:"SPLIT",5:"SPLIT",6:"SPLIT",7:"SPLIT",8:"HIT",  9:"HIT",  10:"HIT",  11:"HIT"},
        4:  {2:"HIT",  3:"HIT",  4:"HIT",  5:"SPLIT",6:"SPLIT",7:"HIT",  8:"HIT",  9:"HIT",  10:"HIT",  11:"HIT"},
        5:  {2:"DOUBLE",3:"DOUBLE",4:"DOUBLE",5:"DOUBLE",6:"DOUBLE",7:"DOUBLE",8:"DOUBLE",9:"DOUBLE",10:"HIT",11:"HIT"},
        6:  {2:"SPLIT",3:"SPLIT",4:"SPLIT",5:"SPLIT",6:"SPLIT",7:"HIT",  8:"HIT",  9:"HIT",  10:"HIT",  11:"HIT"},
        7:  {2:"SPLIT",3:"SPLIT",4:"SPLIT",5:"SPLIT",6:"SPLIT",7:"SPLIT",8:"HIT",  9:"HIT",  10:"HIT",  11:"HIT"},
        8:  {d:"SPLIT" for d in range(2, 12)},
        9:  {2:"SPLIT",3:"SPLIT",4:"SPLIT",5:"SPLIT",6:"SPLIT",7:"STAND",8:"SPLIT",9:"SPLIT",10:"STAND",11:"STAND"},
        10: {d:"STAND" for d in range(2, 12)},
        11: {d:"SPLIT" for d in range(2, 12)},
    }

    ACTION_EMOJI = {"HIT": "👊", "STAND": "✋", "DOUBLE": "⚡", "SPLIT": "✂️",
                    "BLACKJACK": "🃏", "BUST": "💀"}
    ACTION_DESC = {
        "HIT":      "Pide otra carta.",
        "STAND":    "Plantarse. Tu mano es suficientemente fuerte.",
        "DOUBLE":   "Dobla tu apuesta y recibe exactamente una carta más.",
        "SPLIT":    "Divide tu par en dos manos independientes.",
        "BLACKJACK":"¡Blackjack natural! Ganas automáticamente.",
        "BUST":     "Te has pasado de 21. Pierdes automáticamente.",
    }

    @classmethod
    def dealer_upcard_value(cls, card):
        if card.value == Value.ACE:
            return 11
        if card.value in (Value.JACK, Value.QUEEN, Value.KING):
            return 10
        return int(card.value.value)

    @classmethod
    def recommend(cls, player_hand, dealer_upcard):
        if player_hand.is_blackjack():
            return "BLACKJACK"
        if player_hand.is_bust():
            return "BUST"
        d = cls.dealer_upcard_value(dealer_upcard)
        total, is_soft = player_hand.get_value()

        if player_hand.is_pair():
            pv = player_hand.pair_card_value()
            if pv in cls.PAIRS and d in cls.PAIRS[pv]:
                return cls.PAIRS[pv][d]

        if is_soft and len(player_hand.cards) == 2:
            for card in player_hand.cards:
                if card.value != Value.ACE:
                    nv = 10 if card.value in (Value.JACK, Value.QUEEN, Value.KING) else int(card.value.value)
                    if nv in cls.SOFT and d in cls.SOFT[nv]:
                        return cls.SOFT[nv][d]

        t = min(max(total, 4), 21)
        if t in cls.HARD and d in cls.HARD[t]:
            return cls.HARD[t][d]
        return "STAND" if total >= 17 else "HIT"


class Card:
    def __init__(self, value: Value, suit: Suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.value.value}{self._get_suit_symbol()}"

    def __str__(self):
        return f"{self.value.value}{self._get_suit_symbol()}"

    def _get_suit_symbol(self):
        return {
            Suit.SPADES: "♠️",
            Suit.HEARTS: "♥️",
            Suit.DIAMONDS: "♦️",
            Suit.CLUBS: "♣️",
        }[self.suit]


class EndHand:
    def __init__(self, cards, points, game_mode, has_last_hand=False, bonuses_points=0):
        self.cards = cards
        self.points = points

        self.has_last_hand = has_last_hand
        self.bonuses_points = bonuses_points
        self.game_mode = game_mode

        self.belotscore = self.convert_points_to_belotscore() + bonuses_points

    def convert_points_to_belotscore(self):
        total_points = self.points
        if self.game_mode == GameMode.NO_TRUMPS:
            total_points *= 2

        last_digit = total_points % 10
        belotscore = total_points // 10

        if self.game_mode == GameMode.ALL_TRUMPS:
            print("All trumps")
            if last_digit >= 4:
                belotscore += 1
        elif self.game_mode == GameMode.NO_TRUMPS:
            print("No trumps")
            if last_digit >= 5:
                belotscore += 1
        else:
            print("Specific suit")
            if last_digit >= 6:
                belotscore += 1

        return belotscore


class TeamScore:
    def __init__(self):
        self.total_belotscore = 0
        self.belotscore_history = [0]
        self.hands = []

    def update_round(self, end_hand):
        self.total_belotscore += end_hand.belotscore
        self.belotscore_history.append(self.total_belotscore)
        self.hands.append(end_hand)

    def get_total_rounds(self):
        return len(self.hands)

    def get_last_hand(self):
        return self.hands[-1].cards if self.hands else []


class Game:

    def __init__(self, game_mode=None):
        self.cards = []
        self.game_mode = None
        self.generate_all_cards()
        self.last_take_points = 10

        self.team_scores = [TeamScore(), TeamScore()]
        game_mode_argument = GameMode.ALL_TRUMPS if game_mode is None else game_mode
        self.change_gamemode(game_mode_argument)

    def change_gamemode(self, game_mode):
        self.game_mode = game_mode
        self.cards = self.sort_cards(self.cards)

    def generate_all_cards(self):
        for suit in Suit:
            for value in Value:
                self.cards.append(Card(value, suit))

    def get_card_gamevalue(self, card, trump_value_class=CardTrumpValue, non_trump_value_class=CardNonTrumpValue):
        if self.game_mode == GameMode.ALL_TRUMPS:
            return trump_value_class[card.value.name].value
        elif self.game_mode == GameMode.NO_TRUMPS:
            return non_trump_value_class[card.value.name].value
        elif card.suit.value == self.game_mode.value:
            return trump_value_class[card.value.name].value
        else:
            return non_trump_value_class[card.value.name].value

    def sort_by_gamevalue(self, cards_to_sort):
        cards_to_sort.sort(key=self.get_card_gamevalue, reverse=True)
        return cards_to_sort

    def sort_by_ordervalue(self, cards_to_sort):
        cards_to_sort.sort(key=lambda x: self.get_card_gamevalue(x, CardTrumpOrder, CardNonTrumpOrder))
        return cards_to_sort

    def sort_by_suit(self, cards_to_sort):
        suit_order = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]

        def suit_sort_key(card):
            if card.suit.value == self.game_mode.value:
                return (0, suit_order.index(card.suit))
            else:
                return (1, suit_order.index(card.suit))

        cards_to_sort.sort(key=suit_sort_key)
        return self.cards

    def sort_cards(self, cards_to_sort):
        self.sort_by_ordervalue(cards_to_sort)
        self.sort_by_suit(cards_to_sort)

        return cards_to_sort

    def get_max_points(self):
        return sum([self.get_card_gamevalue(card) for card in self.cards]) + self.last_take_points

    def get_points(self, taken_cards, has_taken_last=False):
        return sum([self.get_card_gamevalue(card) for card in taken_cards]) + (
            self.last_take_points if has_taken_last else 0
        )

    def get_other_cards(self, taken_cards):
        return [card for card in self.cards if str(card) not in [str(taken_card) for taken_card in taken_cards]]

    def add_current_round_points(
        self, taken_cards, team_index=0, has_taken_last=False, bonuses_points=0, enemy_bonuses_points=0
    ):
        current_team_points = self.get_points(taken_cards, has_taken_last)
        current_team_hand = EndHand(taken_cards, current_team_points, self.game_mode, has_taken_last, bonuses_points)
        self.team_scores[team_index].update_round(current_team_hand)

        enemy_team_points = self.get_max_points() - current_team_points
        enemy_cards = [card for card in self.cards if card not in taken_cards]
        enemy_team_hand = EndHand(
            enemy_cards, enemy_team_points, self.game_mode, not has_taken_last, enemy_bonuses_points
        )

        self.team_scores[1 - team_index].update_round(enemy_team_hand)

    def get_team_belotscore(self, team_index=0):
        return self.team_scores[team_index].total_belotscore

    def get_team_belotscore_history(self, team_index=0):
        return self.team_scores[team_index].belotscore_history

    def get_round(self):
        return self.team_scores[0].get_total_rounds()

    def start_new_game(self):
        self.team_scores = [TeamScore(), TeamScore()]

    def revert_last_round(self):
        if self.get_round() <= 0:
            return

        for team in self.team_scores:
            team.hands.pop()
            team.belotscore_history.pop()
            team.total_belotscore = team.belotscore_history[-1] if team.belotscore_history else 0