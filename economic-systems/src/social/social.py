"""
Social Interaction System for NovaLux Phase 2

This module defines the social interaction components, including:
- Player relationships and social connections
- Social actions and interactions
- Reputation and influence systems
- Faction dynamics and allegiances
- Social rewards and incentives

The social system integrates with the core economy and narrative systems
to create meaningful player-to-player interactions and social dynamics
within the NovaLux ecosystem.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import uuid
import time
import json
import random
import math
from enum import Enum
from dataclasses import dataclass, field
import sys
import os

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.economy import CurrencyType


class SocialActionType(Enum):
    """Types of social actions in the NovaLux ecosystem."""
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPT = "friend_accept"
    FRIEND_REJECT = "friend_reject"
    FRIEND_REMOVE = "friend_remove"
    MESSAGE = "message"
    GIFT = "gift"
    TRADE = "trade"
    TEAM_INVITE = "team_invite"
    TEAM_JOIN = "team_join"
    TEAM_LEAVE = "team_leave"
    FACTION_SUPPORT = "faction_support"
    FACTION_OPPOSE = "faction_oppose"
    REPUTATION_BOOST = "reputation_boost"
    REPUTATION_PENALTY = "reputation_penalty"


class RelationshipStatus(Enum):
    """Status of relationships between players."""
    NONE = "none"
    PENDING = "pending"
    FRIENDS = "friends"
    ALLIES = "allies"
    RIVALS = "rivals"
    BLOCKED = "blocked"


class FactionAlignment(Enum):
    """Alignment levels with factions."""
    HOSTILE = -3
    UNFRIENDLY = -2
    SUSPICIOUS = -1
    NEUTRAL = 0
    FRIENDLY = 1
    TRUSTED = 2
    EXALTED = 3


@dataclass
class SocialAction:
    """Represents a social action in the NovaLux ecosystem."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: SocialActionType = SocialActionType.MESSAGE
    initiator_id: str = ""
    target_id: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time()))
    data: Dict[str, Any] = field(default_factory=dict)
    is_public: bool = False
    faction_id: Optional[str] = None
    location_id: Optional[str] = None


@dataclass
class Relationship:
    """Represents a relationship between two players."""
    player1_id: str = ""
    player2_id: str = ""
    status: RelationshipStatus = RelationshipStatus.NONE
    affinity: float = 0.0  # -100 to 100
    last_interaction: int = 0
    interaction_count: int = 0
    notes: str = ""


@dataclass
class FactionRelationship:
    """Represents a player's relationship with a faction."""
    player_id: str = ""
    faction_id: str = ""
    alignment: FactionAlignment = FactionAlignment.NEUTRAL
    influence: float = 0.0  # 0 to 100
    reputation: float = 0.0  # 0 to 100
    quests_completed: int = 0
    last_interaction: int = 0
    rank: int = 0
    special_status: Optional[str] = None


@dataclass
class Faction:
    """Represents a faction in the NovaLux ecosystem."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    leader_id: Optional[str] = None
    territory_control: Dict[str, float] = field(default_factory=dict)  # location_id -> control percentage
    resources: Dict[str, float] = field(default_factory=dict)  # resource_type -> amount
    power_level: float = 50.0  # 0 to 100
    member_count: int = 0
    creation_timestamp: int = field(default_factory=lambda: int(time.time()))
    faction_relationships: Dict[str, float] = field(default_factory=dict)  # faction_id -> relationship (-100 to 100)
    is_player_created: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class SocialProfile:
    """Represents a player's social profile."""
    player_id: str = ""
    display_name: str = ""
    title: Optional[str] = None
    bio: str = ""
    achievements: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    primary_faction_id: Optional[str] = None
    social_rank: int = 0
    influence_score: float = 0.0
    reputation_score: float = 0.0
    friend_count: int = 0
    last_active: int = field(default_factory=lambda: int(time.time()))
    is_public: bool = True
    tags: List[str] = field(default_factory=list)


class SocialSystem:
    """
    Social system for the NovaLux ecosystem.
    
    This class manages social interactions, relationships, factions,
    and reputation systems.
    """
    
    def __init__(self):
        """Initialize the social system."""
        self.social_actions: List[SocialAction] = []
        self.relationships: Dict[str, Relationship] = {}  # composite key "player1_id:player2_id"
        self.faction_relationships: Dict[str, FactionRelationship] = {}  # composite key "player_id:faction_id"
        self.factions: Dict[str, Faction] = {}
        self.social_profiles: Dict[str, SocialProfile] = {}
        
        # Initialize default factions
        self._initialize_default_factions()
        
        # Social action impact configuration
        self.action_impacts = {
            SocialActionType.FRIEND_ACCEPT: {
                'affinity': 10.0,
                'reputation': 1.0
            },
            SocialActionType.GIFT: {
                'affinity': 5.0,
                'reputation': 2.0,
                'influence': 1.0
            },
            SocialActionType.TRADE: {
                'affinity': 2.0,
                'reputation': 1.0
            },
            SocialActionType.TEAM_JOIN: {
                'affinity': 5.0,
                'reputation': 1.0
            },
            SocialActionType.FACTION_SUPPORT: {
                'faction_alignment': 0.1,
                'faction_influence': 5.0,
                'faction_reputation': 2.0
            },
            SocialActionType.FACTION_OPPOSE: {
                'faction_alignment': -0.1,
                'faction_influence': -5.0,
                'faction_reputation': -2.0
            },
            SocialActionType.REPUTATION_BOOST: {
                'reputation': 5.0
            },
            SocialActionType.REPUTATION_PENALTY: {
                'reputation': -5.0
            }
        }
    
    def _initialize_default_factions(self) -> None:
        """Initialize the default factions in the NovaLux ecosystem."""
        # Architects - Order, structure, technology
        architects = Faction(
            name="Architects",
            description="Masters of technology and structure, the Architects seek to rebuild society through innovation and order.",
            power_level=70.0,
            member_count=0,
            territory_control={
                "central_district": 80.0,
                "research_labs": 90.0,
                "corporate_sector": 60.0
            },
            resources={
                "technology": 90.0,
                "energy": 70.0,
                "information": 80.0
            },
            tags=["order", "technology", "innovation"]
        )
        
        # Guardians - Protection, tradition, stability
        guardians = Faction(
            name="Guardians",
            description="Protectors of tradition and stability, the Guardians maintain order and security in a chaotic world.",
            power_level=65.0,
            member_count=0,
            territory_control={
                "security_zone": 85.0,
                "residential_district": 60.0,
                "old_city": 70.0
            },
            resources={
                "security": 85.0,
                "community": 75.0,
                "history": 80.0
            },
            tags=["protection", "tradition", "stability"]
        )
        
        # Seekers - Knowledge, exploration, freedom
        seekers = Faction(
            name="Seekers",
            description="Explorers of the unknown, the Seekers value knowledge, freedom, and pushing boundaries.",
            power_level=60.0,
            member_count=0,
            territory_control={
                "university_district": 75.0,
                "frontier_zone": 80.0,
                "data_haven": 65.0
            },
            resources={
                "knowledge": 90.0,
                "exploration": 85.0,
                "creativity": 80.0
            },
            tags=["knowledge", "exploration", "freedom"]
        )
        
        # Shadows - Chaos, rebellion, transformation
        shadows = Faction(
            name="Shadows",
            description="Agents of change and chaos, the Shadows work from the darkness to transform society through disruption.",
            power_level=55.0,
            member_count=0,
            territory_control={
                "underground": 90.0,
                "nightlife_district": 70.0,
                "abandoned_sector": 85.0
            },
            resources={
                "secrets": 85.0,
                "black_market": 80.0,
                "influence": 75.0
            },
            tags=["chaos", "rebellion", "transformation"]
        )
        
        # Set faction relationships
        architects.faction_relationships = {
            "Guardians": 40.0,
            "Seekers": 20.0,
            "Shadows": -60.0
        }
        
        guardians.faction_relationships = {
            "Architects": 40.0,
            "Seekers": -20.0,
            "Shadows": -80.0
        }
        
        seekers.faction_relationships = {
            "Architects": 20.0,
            "Guardians": -20.0,
            "Shadows": 10.0
        }
        
        shadows.faction_relationships = {
            "Architects": -60.0,
            "Guardians": -80.0,
            "Seekers": 10.0
        }
        
        # Add factions to system
        self.factions[architects.id] = architects
        self.factions[guardians.id] = guardians
        self.factions[seekers.id] = seekers
        self.factions[shadows.id] = shadows
    
    def create_social_profile(self, player_id: str, display_name: str, bio: str = "") -> SocialProfile:
        """
        Create a social profile for a player.
        
        Args:
            player_id: ID of the player
            display_name: Display name for the profile
            bio: Player biography
            
        Returns:
            Created SocialProfile object
        """
        profile = SocialProfile(
            player_id=player_id,
            display_name=display_name,
            bio=bio
        )
        
        self.social_profiles[player_id] = profile
        return profile
    
    def update_social_profile(self, player_id: str, profile_data: Dict[str, Any]) -> Optional[SocialProfile]:
        """
        Update a player's social profile.
        
        Args:
            player_id: ID of the player
            profile_data: Dictionary containing profile updates
            
        Returns:
            Updated SocialProfile object or None if profile doesn't exist
        """
        if player_id not in self.social_profiles:
            return None
        
        profile = self.social_profiles[player_id]
        
        # Update fields
        if 'display_name' in profile_data:
            profile.display_name = profile_data['display_name']
        
        if 'title' in profile_data:
            profile.title = profile_data['title']
        
        if 'bio' in profile_data:
            profile.bio = profile_data['bio']
        
        if 'primary_faction_id' in profile_data:
            profile.primary_faction_id = profile_data['primary_faction_id']
        
        if 'is_public' in profile_data:
            profile.is_public = profile_data['is_public']
        
        if 'tags' in profile_data:
            profile.tags = profile_data['tags']
        
        # Update last active timestamp
        profile.last_active = int(time.time())
        
        return profile
    
    def get_social_profile(self, player_id: str) -> Optional[SocialProfile]:
        """
        Get a player's social profile.
        
        Args:
            player_id: ID of the player
            
        Returns:
            SocialProfile object or None if profile doesn't exist
        """
        return self.social_profiles.get(player_id)
    
    def record_social_action(self, action_type: SocialActionType, initiator_id: str,
                           target_id: Optional[str] = None, data: Dict[str, Any] = None,
                           is_public: bool = False, faction_id: Optional[str] = None,
                           location_id: Optional[str] = None) -> SocialAction:
        """
        Record a social action.
        
        Args:
            action_type: Type of social action
            initiator_id: ID of the player initiating the action
            target_id: ID of the target player (optional)
            data: Additional data for the action (optional)
            is_public: Whether the action is public (default: False)
            faction_id: ID of the related faction (optional)
            location_id: ID of the location where the action occurred (optional)
            
        Returns:
            Created SocialAction object
        """
        action = SocialAction(
            action_type=action_type,
            initiator_id=initiator_id,
            target_id=target_id,
            data=data or {},
            is_public=is_public,
            faction_id=faction_id,
            location_id=location_id
        )
        
        # Add to action history
        self.social_actions.append(action)
        
        # Update relationship if applicable
        if target_id:
            self._update_relationship_from_action(action)
        
        # Update faction relationship if applicable
        if faction_id:
            self._update_faction_relationship_from_action(action)
        
        # Update social metrics
        self._update_social_metrics_from_action(action)
        
        return action
    
    def _update_relationship_from_action(self, action: SocialAction) -> None:
        """
        Update player relationship based on a social action.
        
        Args:
            action: Social action to process
        """
        if not action.target_id:
            return
        
        # Get or create relationship
        relationship_key = self._get_relationship_key(action.initiator_id, action.target_id)
        relationship = self.relationships.get(relationship_key)
        
        if not relationship:
            relationship = Relationship(
                player1_id=action.initiator_id,
                player2_id=action.target_id
            )
            self.relationships[relationship_key] = relationship
        
        # Update relationship based on action type
        if action.action_type == SocialActionType.FRIEND_REQUEST:
            relationship.status = RelationshipStatus.PENDING
        
        elif action.action_type == SocialActionType.FRIEND_ACCEPT:
            relationship.status = RelationshipStatus.FRIENDS
            relationship.affinity += self.action_impacts.get(SocialActionType.FRIEND_ACCEPT, {}).get('affinity', 0.0)
        
        elif action.action_type == SocialActionType.FRIEND_REJECT:
            relationship.status = RelationshipStatus.NONE
            relationship.affinity -= 5.0
        
        elif action.action_type == SocialActionType.FRIEND_REMOVE:
            relationship.status = RelationshipStatus.NONE
            relationship.affinity -= 10.0
        
        elif action.action_type == SocialActionType.GIFT:
            relationship.affinity += self.action_impacts.get(SocialActionType.GIFT, {}).get('affinity', 0.0)
            
            # Adjust based on gift value
            if 'value' in action.data:
                value_factor = min(action.data['value'] / 100.0, 5.0)
                relationship.affinity += value_factor
        
        elif action.action_type == SocialActionType.TRADE:
            relationship.affinity += self.action_impacts.get(SocialActionType.TRADE, {}).get('affinity', 0.0)
        
        elif action.action_type == SocialActionType.TEAM_INVITE or action.action_type == SocialActionType.TEAM_JOIN:
            relationship.affinity += self.action_impacts.get(SocialActionType.TEAM_JOIN, {}).get('affinity', 0.0)
        
        # Update interaction metrics
        relationship.last_interaction = action.timestamp
        relationship.interaction_count += 1
        
        # Cap affinity at -100 to 100
        relationship.affinity = max(-100.0, min(100.0, relationship.affinity))
    
    def _update_faction_relationship_from_action(self, action: SocialAction) -> None:
        """
        Update faction relationship based on a social action.
        
        Args:
            action: Social action to process
        """
        if not action.faction_id:
            return
        
        # Get or create faction relationship
        relationship_key = f"{action.initiator_id}:{action.faction_id}"
        faction_relationship = self.faction_relationships.get(relationship_key)
        
        if not faction_relationship:
            faction_relationship = FactionRelationship(
                player_id=action.initiator_id,
                faction_id=action.faction_id
            )
            self.faction_relationships[relationship_key] = faction_relationship
        
        # Update relationship based on action type
        if action.action_type == SocialActionType.FACTION_SUPPORT:
            # Increase alignment
            alignment_change = self.action_impacts.get(SocialActionType.FACTION_SUPPORT, {}).get('faction_alignment', 0.0)
            self._adjust_faction_alignment(faction_relationship, alignment_change)
            
            # Increase influence and reputation
            faction_relationship.influence += self.action_impacts.get(SocialActionType.FACTION_SUPPORT, {}).get('faction_influence', 0.0)
            faction_relationship.reputation += self.action_impacts.get(SocialActionType.FACTION_SUPPORT, {}).get('faction_reputation', 0.0)
            
            # Adjust based on support value
            if 'value' in action.data:
                value_factor = min(action.data['value'] / 100.0, 5.0)
                faction_relationship.influence += value_factor
                faction_relationship.reputation += value_factor / 2.0
        
        elif action.action_type == SocialActionType.FACTION_OPPOSE:
            # Decrease alignment
            alignment_change = self.action_impacts.get(SocialActionType.FACTION_OPPOSE, {}).get('faction_alignment', 0.0)
            self._adjust_faction_alignment(faction_relationship, alignment_change)
            
            # Decrease influence and reputation
            faction_relationship.influence += self.action_impacts.get(SocialActionType.FACTION_OPPOSE, {}).get('faction_influence', 0.0)
            faction_relationship.reputation += self.action_impacts.get(SocialActionType.FACTION_OPPOSE, {}).get('faction_reputation', 0.0)
            
            # Adjust based on opposition value
            if 'value' in action.data:
                value_factor = min(action.data['value'] / 100.0, 5.0)
                faction_relationship.influence -= value_factor
                faction_relationship.reputation -= value_factor / 2.0
        
        # Update interaction metrics
        faction_relationship.last_interaction = action.timestamp
        
        # Cap influence and reputation at 0 to 100
        faction_relationship.influence = max(0.0, min(100.0, faction_relationship.influence))
        faction_relationship.reputation = max(0.0, min(100.0, faction_relationship.reputation))
        
        # Update faction member count
        if faction_relationship.alignment.value > 0 and action.faction_id in self.factions:
            faction = self.factions[action.faction_id]
            
            # Count players with positive alignment as members
            member_count = sum(1 for rel in self.faction_relationships.values()
                              if rel.faction_id == action.faction_id and rel.alignment.value > 0)
            
            faction.member_count = member_count
    
    def _adjust_faction_alignment(self, relationship: FactionRelationship, change: float) -> None:
        """
        Adjust faction alignment based on a change value.
        
        Args:
            relationship: Faction relationship to adjust
            change: Alignment change value
        """
        current_value = relationship.alignment.value
        new_value = current_value + change
        
        # Cap at -3 to 3
        new_value = max(-3, min(3, new_value))
        
        # Convert to enum
        if new_value <= -3:
            relationship.alignment = FactionAlignment.HOSTILE
        elif new_value <= -2:
            relationship.alignment = FactionAlignment.UNFRIENDLY
        elif new_value <= -1:
            relationship.alignment = FactionAlignment.SUSPICIOUS
        elif new_value < 1:
            relationship.alignment = FactionAlignment.NEUTRAL
        elif new_value < 2:
            relationship.alignment = FactionAlignment.FRIENDLY
        elif new_value < 3:
            relationship.alignment = FactionAlignment.TRUSTED
        else:
            relationship.alignment = FactionAlignment.EXALTED
    
    def _update_social_metrics_from_action(self, action: SocialAction) -> None:
        """
        Update social metrics based on a social action.
        
        Args:
            action: Social action to process
        """
        # Update initiator's social profile
        initiator_profile = self.social_profiles.get(action.initiator_id)
        if initiator_profile:
            # Update last active timestamp
            initiator_profile.last_active = action.timestamp
            
            # Update reputation based on action
            if action.action_type in self.action_impacts:
                reputation_impact = self.action_impacts[action.action_type].get('reputation', 0.0)
                initiator_profile.reputation_score += reputation_impact
            
            # Update influence based on action
            if action.action_type in self.action_impacts:
                influence_impact = self.action_impacts[action.action_type].get('influence', 0.0)
                initiator_profile.influence_score += influence_impact
            
            # Update friend count
            initiator_profile.friend_count = self._count_friends(action.initiator_id)
            
            # Cap scores at 0 to 100
            initiator_profile.reputation_score = max(0.0, min(100.0, initiator_profile.reputation_score))
            initiator_profile.influence_score = max(0.0, min(100.0, initiator_profile.influence_score))
        
        # Update target's social profile if applicable
        if action.target_id:
            target_profile = self.social_profiles.get(action.target_id)
            if target_profile:
                # Update friend count
                target_profile.friend_count = self._count_friends(action.target_id)
    
    def _count_friends(self, player_id: str) -> int:
        """
        Count the number of friends a player has.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Number of friends
        """
        friend_count = 0
        
        for relationship in self.relationships.values():
            if (relationship.player1_id == player_id or relationship.player2_id == player_id) and relationship.status == RelationshipStatus.FRIENDS:
                friend_count += 1
        
        return friend_count
    
    def _get_relationship_key(self, player1_id: str, player2_id: str) -> str:
        """
        Get the key for a relationship between two players.
        
        Args:
            player1_id: ID of the first player
            player2_id: ID of the second player
            
        Returns:
            Relationship key
        """
        # Ensure consistent ordering of player IDs
        if player1_id < player2_id:
            return f"{player1_id}:{player2_id}"
        else:
            return f"{player2_id}:{player1_id}"
    
    def get_relationship(self, player1_id: str, player2_id: str) -> Optional[Relationship]:
        """
        Get the relationship between two players.
        
        Args:
            player1_id: ID of the first player
            player2_id: ID of the second player
            
        Returns:
            Relationship object or None if no relationship exists
        """
        relationship_key = self._get_relationship_key(player1_id, player2_id)
        return self.relationships.get(relationship_key)
    
    def get_faction_relationship(self, player_id: str, faction_id: str) -> Optional[FactionRelationship]:
        """
        Get a player's relationship with a faction.
        
        Args:
            player_id: ID of the player
            faction_id: ID of the faction
            
        Returns:
            FactionRelationship object or None if no relationship exists
        """
        relationship_key = f"{player_id}:{faction_id}"
        return self.faction_relationships.get(relationship_key)
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """
        Get a faction by ID.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Faction object or None if faction doesn't exist
        """
        return self.factions.get(faction_id)
    
    def get_faction_by_name(self, faction_name: str) -> Optional[Faction]:
        """
        Get a faction by name.
        
        Args:
            faction_name: Name of the faction
            
        Returns:
            Faction object or None if faction doesn't exist
        """
        for faction in self.factions.values():
            if faction.name.lower() == faction_name.lower():
                return faction
        
        return None
    
    def create_faction(self, name: str, description: str, leader_id: str,
                      territory_control: Dict[str, float] = None,
                      resources: Dict[str, float] = None,
                      tags: List[str] = None) -> Optional[Faction]:
        """
        Create a new faction.
        
        Args:
            name: Name of the faction
            description: Description of the faction
            leader_id: ID of the faction leader
            territory_control: Initial territory control (optional)
            resources: Initial resources (optional)
            tags: Faction tags (optional)
            
        Returns:
            Created Faction object or None if creation failed
        """
        # Check if faction name already exists
        for faction in self.factions.values():
            if faction.name.lower() == name.lower():
                return None
        
        # Create faction
        faction = Faction(
            name=name,
            description=description,
            leader_id=leader_id,
            territory_control=territory_control or {},
            resources=resources or {},
            power_level=10.0,  # Start with low power
            member_count=1,  # Leader is the first member
            is_player_created=True,
            tags=tags or []
        )
        
        # Add faction to system
        self.factions[faction.id] = faction
        
        # Create leader's relationship with faction
        relationship = FactionRelationship(
            player_id=leader_id,
            faction_id=faction.id,
            alignment=FactionAlignment.EXALTED,
            influence=50.0,
            reputation=50.0,
            rank=10,  # Leader rank
            special_status="Founder"
        )
        
        relationship_key = f"{leader_id}:{faction.id}"
        self.faction_relationships[relationship_key] = relationship
        
        # Update leader's social profile
        leader_profile = self.social_profiles.get(leader_id)
        if leader_profile:
            leader_profile.primary_faction_id = faction.id
        
        return faction
    
    def update_faction(self, faction_id: str, faction_data: Dict[str, Any]) -> Optional[Faction]:
        """
        Update a faction.
        
        Args:
            faction_id: ID of the faction
            faction_data: Dictionary containing faction updates
            
        Returns:
            Updated Faction object or None if faction doesn't exist
        """
        if faction_id not in self.factions:
            return None
        
        faction = self.factions[faction_id]
        
        # Update fields
        if 'description' in faction_data:
            faction.description = faction_data['description']
        
        if 'leader_id' in faction_data:
            faction.leader_id = faction_data['leader_id']
        
        if 'territory_control' in faction_data:
            faction.territory_control.update(faction_data['territory_control'])
        
        if 'resources' in faction_data:
            faction.resources.update(faction_data['resources'])
        
        if 'tags' in faction_data:
            faction.tags = faction_data['tags']
        
        return faction
    
    def get_player_factions(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all factions a player is affiliated with.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of faction data with relationship information
        """
        player_factions = []
        
        for relationship_key, relationship in self.faction_relationships.items():
            if relationship.player_id == player_id and relationship.alignment.value > 0:
                faction_id = relationship.faction_id
                faction = self.factions.get(faction_id)
                
                if faction:
                    player_factions.append({
                        'faction_id': faction_id,
                        'name': faction.name,
                        'description': faction.description,
                        'alignment': relationship.alignment.value,
                        'alignment_name': relationship.alignment.name,
                        'influence': relationship.influence,
                        'reputation': relationship.reputation,
                        'rank': relationship.rank,
                        'special_status': relationship.special_status,
                        'is_primary': player_id in self.social_profiles and self.social_profiles[player_id].primary_faction_id == faction_id
                    })
        
        # Sort by influence (highest first)
        player_factions.sort(key=lambda f: f['influence'], reverse=True)
        
        return player_factions
    
    def get_player_friends(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all friends of a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of friend data with relationship information
        """
        friends = []
        
        for relationship_key, relationship in self.relationships.items():
            if (relationship.player1_id == player_id or relationship.player2_id == player_id) and relationship.status == RelationshipStatus.FRIENDS:
                friend_id = relationship.player2_id if relationship.player1_id == player_id else relationship.player1_id
                friend_profile = self.social_profiles.get(friend_id)
                
                if friend_profile:
                    friends.append({
                        'player_id': friend_id,
                        'display_name': friend_profile.display_name,
                        'title': friend_profile.title,
                        'affinity': relationship.affinity,
                        'last_interaction': relationship.last_interaction,
                        'interaction_count': relationship.interaction_count,
                        'primary_faction': self.factions.get(friend_profile.primary_faction_id).name if friend_profile.primary_faction_id in self.factions else None
                    })
        
        # Sort by affinity (highest first)
        friends.sort(key=lambda f: f['affinity'], reverse=True)
        
        return friends
    
    def get_social_feed(self, player_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get social feed for a player.
        
        Args:
            player_id: ID of the player
            limit: Maximum number of feed items to return
            
        Returns:
            List of social feed items
        """
        feed_items = []
        
        # Get player's friends
        friend_ids = [f['player_id'] for f in self.get_player_friends(player_id)]
        
        # Get player's factions
        faction_ids = [f['faction_id'] for f in self.get_player_factions(player_id)]
        
        # Filter actions
        for action in reversed(self.social_actions):  # Newest first
            # Include public actions
            if action.is_public:
                # Include actions by friends
                if action.initiator_id in friend_ids or (action.target_id and action.target_id in friend_ids):
                    feed_items.append(self._format_action_for_feed(action))
                
                # Include actions related to player's factions
                elif action.faction_id in faction_ids:
                    feed_items.append(self._format_action_for_feed(action))
            
            # Include actions involving the player
            elif action.initiator_id == player_id or action.target_id == player_id:
                feed_items.append(self._format_action_for_feed(action))
            
            # Stop when we have enough items
            if len(feed_items) >= limit:
                break
        
        return feed_items
    
    def _format_action_for_feed(self, action: SocialAction) -> Dict[str, Any]:
        """
        Format a social action for the social feed.
        
        Args:
            action: Social action to format
            
        Returns:
            Formatted feed item
        """
        initiator_profile = self.social_profiles.get(action.initiator_id)
        initiator_name = initiator_profile.display_name if initiator_profile else "Unknown Player"
        
        target_name = "Unknown Player"
        if action.target_id:
            target_profile = self.social_profiles.get(action.target_id)
            if target_profile:
                target_name = target_profile.display_name
        
        faction_name = "Unknown Faction"
        if action.faction_id:
            faction = self.factions.get(action.faction_id)
            if faction:
                faction_name = faction.name
        
        # Format message based on action type
        message = "performed an action"
        
        if action.action_type == SocialActionType.FRIEND_REQUEST:
            message = f"sent a friend request to {target_name}"
        
        elif action.action_type == SocialActionType.FRIEND_ACCEPT:
            message = f"accepted {target_name}'s friend request"
        
        elif action.action_type == SocialActionType.GIFT:
            item_name = action.data.get('item_name', 'an item')
            message = f"sent {item_name} to {target_name}"
        
        elif action.action_type == SocialActionType.TRADE:
            message = f"completed a trade with {target_name}"
        
        elif action.action_type == SocialActionType.TEAM_INVITE:
            message = f"invited {target_name} to join their team"
        
        elif action.action_type == SocialActionType.TEAM_JOIN:
            message = f"joined {target_name}'s team"
        
        elif action.action_type == SocialActionType.FACTION_SUPPORT:
            message = f"supported the {faction_name} faction"
        
        elif action.action_type == SocialActionType.FACTION_OPPOSE:
            message = f"opposed the {faction_name} faction"
        
        return {
            'id': action.id,
            'timestamp': action.timestamp,
            'initiator_id': action.initiator_id,
            'initiator_name': initiator_name,
            'target_id': action.target_id,
            'target_name': target_name if action.target_id else None,
            'faction_id': action.faction_id,
            'faction_name': faction_name if action.faction_id else None,
            'action_type': action.action_type.value,
            'message': message,
            'data': action.data,
            'location_id': action.location_id
        }
    
    def update_faction_dynamics(self) -> None:
        """
        Update faction dynamics based on player actions and relationships.
        
        This method should be called periodically to simulate faction power shifts,
        territory control changes, and inter-faction relationships.
        """
        # Calculate faction power levels
        for faction_id, faction in self.factions.items():
            # Sum influence of all faction members
            total_influence = 0.0
            member_count = 0
            
            for relationship in self.faction_relationships.values():
                if relationship.faction_id == faction_id and relationship.alignment.value > 0:
                    total_influence += relationship.influence
                    member_count += 1
            
            # Calculate base power from member influence
            base_power = total_influence / 100.0 if member_count > 0 else 0.0
            
            # Adjust for territory control
            territory_factor = sum(faction.territory_control.values()) / 100.0
            
            # Adjust for resources
            resource_factor = sum(faction.resources.values()) / 100.0
            
            # Calculate new power level
            new_power = (base_power * 0.5) + (territory_factor * 0.3) + (resource_factor * 0.2)
            new_power = new_power * 100.0  # Scale to 0-100
            
            # Apply gradual change
            faction.power_level = faction.power_level * 0.9 + new_power * 0.1
            
            # Cap at 0 to 100
            faction.power_level = max(0.0, min(100.0, faction.power_level))
            
            # Update member count
            faction.member_count = member_count
        
        # Update territory control based on faction power
        self._update_territory_control()
        
        # Update faction relationships
        self._update_faction_relationships()
    
    def _update_territory_control(self) -> None:
        """Update territory control based on faction power."""
        # Get all territories
        all_territories = set()
        for faction in self.factions.values():
            all_territories.update(faction.territory_control.keys())
        
        # For each territory, adjust control based on faction power
        for territory in all_territories:
            # Get factions with control in this territory
            controlling_factions = {}
            
            for faction_id, faction in self.factions.items():
                if territory in faction.territory_control:
                    controlling_factions[faction_id] = faction.territory_control[territory]
            
            # Skip if only one faction controls the territory
            if len(controlling_factions) <= 1:
                continue
            
            # Calculate power ratio for each faction
            power_ratios = {}
            total_power = 0.0
            
            for faction_id in controlling_factions:
                faction = self.factions[faction_id]
                power_ratios[faction_id] = faction.power_level
                total_power += faction.power_level
            
            # Normalize power ratios
            if total_power > 0:
                for faction_id in power_ratios:
                    power_ratios[faction_id] /= total_power
            
            # Adjust territory control
            for faction_id, ratio in power_ratios.items():
                faction = self.factions[faction_id]
                current_control = faction.territory_control.get(territory, 0.0)
                
                # Target control based on power ratio
                target_control = ratio * 100.0
                
                # Apply gradual change
                new_control = current_control * 0.95 + target_control * 0.05
                
                # Update territory control
                faction.territory_control[territory] = new_control
            
            # Normalize territory control to sum to 100%
            total_control = sum(self.factions[faction_id].territory_control.get(territory, 0.0) for faction_id in controlling_factions)
            
            if total_control > 0:
                for faction_id in controlling_factions:
                    faction = self.factions[faction_id]
                    faction.territory_control[territory] = (faction.territory_control.get(territory, 0.0) / total_control) * 100.0
    
    def _update_faction_relationships(self) -> None:
        """Update relationships between factions."""
        # For each pair of factions, adjust relationship based on player interactions
        faction_ids = list(self.factions.keys())
        
        for i in range(len(faction_ids)):
            for j in range(i + 1, len(faction_ids)):
                faction1_id = faction_ids[i]
                faction2_id = faction_ids[j]
                
                faction1 = self.factions[faction1_id]
                faction2 = self.factions[faction2_id]
                
                # Get current relationship
                current_relationship1 = faction1.faction_relationships.get(faction2.name, 0.0)
                current_relationship2 = faction2.faction_relationships.get(faction1.name, 0.0)
                
                # Count positive and negative interactions between members
                positive_interactions = 0
                negative_interactions = 0
                
                # Get members of each faction
                faction1_members = [rel.player_id for rel in self.faction_relationships.values()
                                  if rel.faction_id == faction1_id and rel.alignment.value > 0]
                
                faction2_members = [rel.player_id for rel in self.faction_relationships.values()
                                  if rel.faction_id == faction2_id and rel.alignment.value > 0]
                
                # Check relationships between members
                for member1 in faction1_members:
                    for member2 in faction2_members:
                        relationship = self.get_relationship(member1, member2)
                        
                        if relationship:
                            if relationship.affinity > 20.0:
                                positive_interactions += 1
                            elif relationship.affinity < -20.0:
                                negative_interactions += 1
                
                # Calculate relationship adjustment
                adjustment = (positive_interactions - negative_interactions) * 0.5
                
                # Apply adjustment with dampening
                new_relationship1 = current_relationship1 * 0.95 + adjustment * 0.05
                new_relationship2 = current_relationship2 * 0.95 + adjustment * 0.05
                
                # Cap at -100 to 100
                new_relationship1 = max(-100.0, min(100.0, new_relationship1))
                new_relationship2 = max(-100.0, min(100.0, new_relationship2))
                
                # Update relationships
                faction1.faction_relationships[faction2.name] = new_relationship1
                faction2.faction_relationships[faction1.name] = new_relationship2
    
    def get_faction_analytics(self) -> Dict[str, Any]:
        """
        Get analytics data for factions.
        
        Returns:
            Dictionary containing faction analytics
        """
        # Calculate faction metrics
        faction_metrics = {}
        
        for faction_id, faction in self.factions.items():
            # Calculate average member influence and reputation
            total_influence = 0.0
            total_reputation = 0.0
            member_count = 0
            
            for relationship in self.faction_relationships.values():
                if relationship.faction_id == faction_id and relationship.alignment.value > 0:
                    total_influence += relationship.influence
                    total_reputation += relationship.reputation
                    member_count += 1
            
            avg_influence = total_influence / member_count if member_count > 0 else 0.0
            avg_reputation = total_reputation / member_count if member_count > 0 else 0.0
            
            # Calculate territory control
            total_territory = sum(faction.territory_control.values())
            
            # Calculate resource control
            total_resources = sum(faction.resources.values())
            
            faction_metrics[faction_id] = {
                'name': faction.name,
                'power_level': faction.power_level,
                'member_count': member_count,
                'avg_influence': avg_influence,
                'avg_reputation': avg_reputation,
                'total_territory': total_territory,
                'total_resources': total_resources,
                'is_player_created': faction.is_player_created
            }
        
        # Calculate faction popularity
        faction_popularity = {}
        
        for player_id, profile in self.social_profiles.items():
            if profile.primary_faction_id:
                faction_id = profile.primary_faction_id
                
                if faction_id in faction_popularity:
                    faction_popularity[faction_id] += 1
                else:
                    faction_popularity[faction_id] = 1
        
        # Format results
        results = {
            'faction_metrics': faction_metrics,
            'faction_popularity': faction_popularity,
            'faction_relationships': {faction_id: faction.faction_relationships for faction_id, faction in self.factions.items()}
        }
        
        return results
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the social system to a file.
        
        Args:
            filepath: Path to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to serializable format
            state = {
                'social_actions': [{
                    'id': action.id,
                    'action_type': action.action_type.value,
                    'initiator_id': action.initiator_id,
                    'target_id': action.target_id,
                    'timestamp': action.timestamp,
                    'data': action.data,
                    'is_public': action.is_public,
                    'faction_id': action.faction_id,
                    'location_id': action.location_id
                } for action in self.social_actions],
                
                'relationships': {key: {
                    'player1_id': relationship.player1_id,
                    'player2_id': relationship.player2_id,
                    'status': relationship.status.value,
                    'affinity': relationship.affinity,
                    'last_interaction': relationship.last_interaction,
                    'interaction_count': relationship.interaction_count,
                    'notes': relationship.notes
                } for key, relationship in self.relationships.items()},
                
                'faction_relationships': {key: {
                    'player_id': relationship.player_id,
                    'faction_id': relationship.faction_id,
                    'alignment': relationship.alignment.value,
                    'influence': relationship.influence,
                    'reputation': relationship.reputation,
                    'quests_completed': relationship.quests_completed,
                    'last_interaction': relationship.last_interaction,
                    'rank': relationship.rank,
                    'special_status': relationship.special_status
                } for key, relationship in self.faction_relationships.items()},
                
                'factions': {faction_id: {
                    'id': faction.id,
                    'name': faction.name,
                    'description': faction.description,
                    'leader_id': faction.leader_id,
                    'territory_control': faction.territory_control,
                    'resources': faction.resources,
                    'power_level': faction.power_level,
                    'member_count': faction.member_count,
                    'creation_timestamp': faction.creation_timestamp,
                    'faction_relationships': faction.faction_relationships,
                    'is_player_created': faction.is_player_created,
                    'tags': faction.tags
                } for faction_id, faction in self.factions.items()},
                
                'social_profiles': {player_id: {
                    'player_id': profile.player_id,
                    'display_name': profile.display_name,
                    'title': profile.title,
                    'bio': profile.bio,
                    'achievements': profile.achievements,
                    'badges': profile.badges,
                    'primary_faction_id': profile.primary_faction_id,
                    'social_rank': profile.social_rank,
                    'influence_score': profile.influence_score,
                    'reputation_score': profile.reputation_score,
                    'friend_count': profile.friend_count,
                    'last_active': profile.last_active,
                    'is_public': profile.is_public,
                    'tags': profile.tags
                } for player_id, profile in self.social_profiles.items()},
                
                'action_impacts': {action_type.value: impacts for action_type, impacts in self.action_impacts.items()}
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving social state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the state of the social system from a file.
        
        Args:
            filepath: Path to load the state from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Load social actions
            self.social_actions = []
            for action_data in state.get('social_actions', []):
                self.social_actions.append(SocialAction(
                    id=action_data['id'],
                    action_type=SocialActionType(action_data['action_type']),
                    initiator_id=action_data['initiator_id'],
                    target_id=action_data['target_id'],
                    timestamp=action_data['timestamp'],
                    data=action_data['data'],
                    is_public=action_data['is_public'],
                    faction_id=action_data['faction_id'],
                    location_id=action_data['location_id']
                ))
            
            # Load relationships
            self.relationships = {}
            for key, relationship_data in state.get('relationships', {}).items():
                self.relationships[key] = Relationship(
                    player1_id=relationship_data['player1_id'],
                    player2_id=relationship_data['player2_id'],
                    status=RelationshipStatus(relationship_data['status']),
                    affinity=relationship_data['affinity'],
                    last_interaction=relationship_data['last_interaction'],
                    interaction_count=relationship_data['interaction_count'],
                    notes=relationship_data['notes']
                )
            
            # Load faction relationships
            self.faction_relationships = {}
            for key, relationship_data in state.get('faction_relationships', {}).items():
                self.faction_relationships[key] = FactionRelationship(
                    player_id=relationship_data['player_id'],
                    faction_id=relationship_data['faction_id'],
                    alignment=FactionAlignment(relationship_data['alignment']),
                    influence=relationship_data['influence'],
                    reputation=relationship_data['reputation'],
                    quests_completed=relationship_data['quests_completed'],
                    last_interaction=relationship_data['last_interaction'],
                    rank=relationship_data['rank'],
                    special_status=relationship_data['special_status']
                )
            
            # Load factions
            self.factions = {}
            for faction_id, faction_data in state.get('factions', {}).items():
                self.factions[faction_id] = Faction(
                    id=faction_data['id'],
                    name=faction_data['name'],
                    description=faction_data['description'],
                    leader_id=faction_data['leader_id'],
                    territory_control=faction_data['territory_control'],
                    resources=faction_data['resources'],
                    power_level=faction_data['power_level'],
                    member_count=faction_data['member_count'],
                    creation_timestamp=faction_data['creation_timestamp'],
                    faction_relationships=faction_data['faction_relationships'],
                    is_player_created=faction_data['is_player_created'],
                    tags=faction_data['tags']
                )
            
            # Load social profiles
            self.social_profiles = {}
            for player_id, profile_data in state.get('social_profiles', {}).items():
                self.social_profiles[player_id] = SocialProfile(
                    player_id=profile_data['player_id'],
                    display_name=profile_data['display_name'],
                    title=profile_data['title'],
                    bio=profile_data['bio'],
                    achievements=profile_data['achievements'],
                    badges=profile_data['badges'],
                    primary_faction_id=profile_data['primary_faction_id'],
                    social_rank=profile_data['social_rank'],
                    influence_score=profile_data['influence_score'],
                    reputation_score=profile_data['reputation_score'],
                    friend_count=profile_data['friend_count'],
                    last_active=profile_data['last_active'],
                    is_public=profile_data['is_public'],
                    tags=profile_data['tags']
                )
            
            # Load action impacts
            action_impacts = state.get('action_impacts', {})
            self.action_impacts = {SocialActionType(action_type): impacts for action_type, impacts in action_impacts.items()}
            
            return True
        
        except Exception as e:
            print(f"Error loading social state: {e}")
            return False
