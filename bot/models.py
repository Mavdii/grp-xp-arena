
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models - نماذج البيانات
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any

@dataclass
class User:
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = 'ar'
    is_bot: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(**data)

@dataclass
class UserGroup:
    id: int
    user_id: int
    group_id: int
    xp: int = 0
    level_id: int = 1
    coins: int = 0
    total_messages: int = 0
    last_message_at: Optional[datetime] = None
    last_xp_gain: Optional[datetime] = None
    clan_id: Optional[int] = None
    is_active: bool = True
    joined_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserGroup':
        return cls(**data)

@dataclass
class Level:
    id: int
    level_number: int
    level_name: str
    level_emoji: str
    required_xp: int
    category: str
    tier: int
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Level':
        return cls(**data)

@dataclass
class ShopItem:
    id: int
    name: str
    description: Optional[str] = None
    price: int = 0
    item_type: str = 'booster'
    effect_type: str = 'xp_multiplier'
    effect_value: float = 1.0
    duration_hours: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShopItem':
        return cls(**data)

@dataclass
class Badge:
    id: int
    name: str
    description: Optional[str] = None
    emoji: str = '🏅'
    category: str = 'achievement'
    requirement_type: str = 'messages'
    requirement_value: int = 1
    rarity: str = 'common'
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Badge':
        return cls(**data)

@dataclass
class DailyQuest:
    id: int
    user_id: int
    group_id: int
    quest_type: str
    target_value: int
    current_progress: int = 0
    reward_xp: int = 0
    reward_coins: int = 0
    is_completed: bool = False
    quest_date: date = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyQuest':
        return cls(**data)

@dataclass
class Clan:
    id: int
    name: str
    description: Optional[str] = None
    leader_user_id: int = 0
    group_id: int = 0
    total_xp: int = 0
    member_count: int = 1
    max_members: int = 20
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Clan':
        return cls(**data)

@dataclass
class UserBadge:
    id: int
    user_id: int
    group_id: int
    badge_id: int
    earned_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserBadge':
        return cls(**data)

@dataclass
class MessageLog:
    id: int
    user_id: int
    group_id: int
    message_id: int
    xp_gained: int = 0
    coins_gained: int = 0
    message_type: str = 'text'
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageLog':
        return cls(**data)
