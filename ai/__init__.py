"""
オセロAIモジュール
既存のAI（GreedyAI、CornerAI、LookaheadAI）を提供
"""

from .greedy_ai import GreedyAI
from .corner_ai import CornerAI
from .lookahead_ai import LookaheadAI

__all__ = ['GreedyAI', 'CornerAI', 'LookaheadAI']
