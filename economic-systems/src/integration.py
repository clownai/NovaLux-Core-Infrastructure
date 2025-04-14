"""
Integration Module for NovaLux Economic and Social Systems

This module provides integration between the various components of the
economic and social systems, including:
- Economy Core
- Market System
- Currency System
- Social Interaction System

The integration module ensures that these systems work together seamlessly
and provides a unified API for the game to interact with the economic
and social features.
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

# Import core modules
from core.economy import (
    CurrencyType, ItemRarity, ItemType, MarketCategory,
    Currency, Item, Inventory, Transaction, EconomySystem
)

from market.market import (
    MarketListing, Auction, MarketSystem
)

from currency.currency import (
    CurrencyAction, CurrencyTransaction, CurrencySystem
)

from social.social import (
    SocialActionType, RelationshipStatus, FactionAlignment,
    SocialAction, Relationship, FactionRelationship, Faction,
    SocialProfile, SocialSystem
)


class EconomicSocialSystem:
    """
    Integration class for the NovaLux economic and social systems.
    
    This class provides a unified interface for interacting with all
    economic and social features, ensuring proper integration between
    the various subsystems.
    """
    
    def __init__(self):
        """Initialize the integrated economic and social system."""
        # Initialize core systems
        self.economy = EconomySystem()
        self.market = MarketSystem(self.economy)
        self.currency = CurrencySystem(self.economy)
        self.social = SocialSystem()
        
        # Integration configuration
        self.config = {
            'social_currency_rewards': {
                SocialActionType.FRIEND_ACCEPT: {
                    CurrencyType.REPUTATION: 5.0
                },
                SocialActionType.GIFT: {
                    CurrencyType.REPUTATION: 10.0
                },
                SocialActionType.FACTION_SUPPORT: {
                    CurrencyType.FACTION_INFLUENCE: 20.0,
                    CurrencyType.REPUTATION: 5.0
                }
            },
            'faction_market_discounts': {
                FactionAlignment.FRIENDLY: 0.05,  # 5% discount
                FactionAlignment.TRUSTED: 0.10,   # 10% discount
                FactionAlignment.EXALTED: 0.15    # 15% discount
            },
            'reputation_market_fee_reduction': 0.001,  # 0.1% fee reduction per point of reputation (max 50%)
            'friend_trade_fee_reduction': 0.50,  # 50% fee reduction for trades between friends
            'update_interval_seconds': 3600  # 1 hour
        }
        
        # Last update timestamp
        self.last_update = int(time.time())
    
    def create_player(self, player_id: str, display_name: str, starting_inventory_slots: int = 100) -> Dict[str, Any]:
        """
        Create a new player with all necessary profiles and inventories.
        
        Args:
            player_id: ID of the player
            display_name: Display name for the player
            starting_inventory_slots: Number of inventory slots to start with
            
        Returns:
            Dictionary containing created player data
        """
        # Create inventory
        inventory = self.economy.create_inventory(player_id, starting_inventory_slots)
        
        # Create social profile
        social_profile = self.social.create_social_profile(player_id, display_name)
        
        # Return player data
        return {
            'player_id': player_id,
            'display_name': display_name,
            'inventory': {
                'slots': inventory.max_slots,
                'currencies': {currency_type.value: amount for currency_type, amount in inventory.currencies.items()},
                'items': inventory.items
            },
            'social_profile': {
                'display_name': social_profile.display_name,
                'reputation_score': social_profile.reputation_score,
                'influence_score': social_profile.influence_score,
                'friend_count': social_profile.friend_count
            }
        }
    
    def process_social_action(self, action_type: SocialActionType, initiator_id: str,
                             target_id: Optional[str] = None, data: Dict[str, Any] = None,
                             is_public: bool = False, faction_id: Optional[str] = None,
                             location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a social action and update all relevant systems.
        
        Args:
            action_type: Type of social action
            initiator_id: ID of the player initiating the action
            target_id: ID of the target player (optional)
            data: Additional data for the action (optional)
            is_public: Whether the action is public
            faction_id: ID of the related faction (optional)
            location_id: ID of the location where the action occurred (optional)
            
        Returns:
            Dictionary containing action results
        """
        # Record social action
        social_action = self.social.record_social_action(
            action_type=action_type,
            initiator_id=initiator_id,
            target_id=target_id,
            data=data or {},
            is_public=is_public,
            faction_id=faction_id,
            location_id=location_id
        )
        
        # Process currency rewards if applicable
        currency_transactions = []
        
        if action_type in self.config['social_currency_rewards']:
            rewards = self.config['social_currency_rewards'][action_type]
            
            for currency_type, amount in rewards.items():
                # Adjust amount based on action data
                adjusted_amount = amount
                
                if 'value' in data:
                    value_factor = min(data['value'] / 100.0, 5.0)
                    adjusted_amount *= (1.0 + value_factor)
                
                # Award currency
                transaction = self.currency.earn_currency(
                    player_id=initiator_id,
                    currency_type=currency_type,
                    amount=adjusted_amount,
                    source=f"social_action_{action_type.value}",
                    notes=f"Reward for {action_type.value}" + (f" with {target_id}" if target_id else "")
                )
                
                if transaction:
                    currency_transactions.append({
                        'id': transaction.id,
                        'currency_type': transaction.currency_type.value,
                        'amount': transaction.amount
                    })
        
        # Handle specific action types
        additional_results = {}
        
        if action_type == SocialActionType.GIFT and 'item_id' in data and target_id:
            # Process item gift
            if self._process_item_gift(initiator_id, target_id, data):
                additional_results['gift_successful'] = True
        
        elif action_type == SocialActionType.FACTION_SUPPORT and faction_id:
            # Update faction power
            faction = self.social.get_faction(faction_id)
            if faction:
                # Small immediate power boost
                faction.power_level = min(100.0, faction.power_level + 0.1)
                additional_results['faction_power'] = faction.power_level
        
        # Return results
        return {
            'action_id': social_action.id,
            'action_type': social_action.action_type.value,
            'timestamp': social_action.timestamp,
            'currency_rewards': currency_transactions,
            **additional_results
        }
    
    def _process_item_gift(self, sender_id: str, receiver_id: str, data: Dict[str, Any]) -> bool:
        """
        Process an item gift between players.
        
        Args:
            sender_id: ID of the sender
            receiver_id: ID of the receiver
            data: Gift data containing item_id and quantity
            
        Returns:
            True if gift was successful, False otherwise
        """
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        if not item_id:
            return False
        
        # Check if sender has the item
        sender_inventory = self.economy.inventories.get(sender_id)
        if not sender_inventory or item_id not in sender_inventory.items or sender_inventory.items[item_id] < quantity:
            return False
        
        # Check if receiver has space
        receiver_inventory = self.economy.inventories.get(receiver_id)
        if not receiver_inventory:
            return False
        
        # Remove item from sender
        if not sender_inventory.remove_item(item_id, quantity):
            return False
        
        # Add item to receiver
        if not receiver_inventory.add_item(item_id, quantity):
            # Return item to sender if receiver's inventory is full
            sender_inventory.add_item(item_id, quantity)
            return False
        
        return True
    
    def process_market_transaction(self, transaction_type: str, player_id: str,
                                 data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a market transaction and update all relevant systems.
        
        Args:
            transaction_type: Type of transaction ('buy', 'sell', 'bid', 'create_auction')
            player_id: ID of the player
            data: Transaction data
            
        Returns:
            Dictionary containing transaction results
        """
        results = {'success': False}
        
        # Apply social factors to transaction
        adjusted_data = self._apply_social_factors_to_transaction(player_id, data)
        
        # Process transaction based on type
        if transaction_type == 'buy':
            listing_id = adjusted_data.get('listing_id')
            if listing_id:
                transaction = self.market.purchase_listing(listing_id, player_id)
                
                if transaction:
                    results['success'] = True
                    results['transaction_id'] = transaction.id
                    results['amount'] = transaction.amount
                    results['item_id'] = transaction.item_id
                    
                    # Record social action for significant purchases
                    if transaction.amount >= 1000.0:
                        self.social.record_social_action(
                            action_type=SocialActionType.TRADE,
                            initiator_id=player_id,
                            target_id=transaction.seller_id,
                            data={
                                'item_id': transaction.item_id,
                                'amount': transaction.amount,
                                'currency_type': transaction.currency_type.value
                            },
                            is_public=True
                        )
        
        elif transaction_type == 'sell':
            listing_data = adjusted_data.copy()
            listing_data['seller_id'] = player_id
            
            listing = self.market.create_listing(listing_data)
            
            if listing:
                results['success'] = True
                results['listing_id'] = listing.id
                results['price'] = listing.price
                
                # Record social action for significant listings
                if listing.price >= 1000.0:
                    self.social.record_social_action(
                        action_type=SocialActionType.TRADE,
                        initiator_id=player_id,
                        data={
                            'item_id': listing.item_id,
                            'price': listing.price,
                            'currency_type': listing.currency_type.value
                        },
                        is_public=True
                    )
        
        elif transaction_type == 'bid':
            auction_id = adjusted_data.get('auction_id')
            bid_amount = adjusted_data.get('bid_amount', 0.0)
            
            if auction_id and bid_amount > 0:
                success = self.market.place_bid(auction_id, player_id, bid_amount)
                
                if success:
                    results['success'] = True
                    results['auction_id'] = auction_id
                    results['bid_amount'] = bid_amount
                    
                    # Get auction details
                    auction = self.market.auctions.get(auction_id)
                    if auction:
                        # Record social action for significant bids
                        if bid_amount >= 1000.0:
                            self.social.record_social_action(
                                action_type=SocialActionType.TRADE,
                                initiator_id=player_id,
                                target_id=auction.seller_id,
                                data={
                                    'item_id': auction.item_id,
                                    'bid_amount': bid_amount,
                                    'currency_type': auction.currency_type.value
                                },
                                is_public=True
                            )
        
        elif transaction_type == 'create_auction':
            auction_data = adjusted_data.copy()
            auction_data['seller_id'] = player_id
            
            auction = self.market.create_auction(auction_data)
            
            if auction:
                results['success'] = True
                results['auction_id'] = auction.id
                results['starting_bid'] = auction.starting_bid
                
                # Record social action for significant auctions
                if auction.starting_bid >= 1000.0:
                    self.social.record_social_action(
                        action_type=SocialActionType.TRADE,
                        initiator_id=player_id,
                        data={
                            'item_id': auction.item_id,
                            'starting_bid': auction.starting_bid,
                            'currency_type': auction.currency_type.value
                        },
                        is_public=True
                    )
        
        return results
    
    def _apply_social_factors_to_transaction(self, player_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply social factors to a market transaction.
        
        Args:
            player_id: ID of the player
            data: Transaction data
            
        Returns:
            Adjusted transaction data
        """
        adjusted_data = data.copy()
        
        # Apply faction discounts for purchases
        if 'listing_id' in data:
            listing_id = data['listing_id']
            listing = self.market.listings.get(listing_id)
            
            if listing and listing.seller_id and listing.faction_id:
                # Check if player has a relationship with the faction
                faction_relationship = self.social.get_faction_relationship(player_id, listing.faction_id)
                
                if faction_relationship and faction_relationship.alignment.value > 0:
                    # Apply discount based on alignment
                    discount = self.config['faction_market_discounts'].get(faction_relationship.alignment, 0.0)
                    
                    if discount > 0:
                        # Adjust price in the market system directly
                        listing.price = listing.price * (1.0 - discount)
        
        # Apply reputation-based fee reduction
        player_profile = self.social.get_social_profile(player_id)
        if player_profile:
            reputation = player_profile.reputation_score
            
            # Calculate fee reduction (max 50%)
            fee_reduction = min(reputation * self.config['reputation_market_fee_reduction'], 0.5)
            
            # Store in data for market system to use
            adjusted_data['fee_reduction'] = fee_reduction
        
        # Apply friend discount for direct trades
        if 'target_id' in data:
            target_id = data['target_id']
            relationship = self.social.get_relationship(player_id, target_id)
            
            if relationship and relationship.status == RelationshipStatus.FRIENDS:
                # Apply friend fee reduction
                adjusted_data['fee_reduction'] = self.config['friend_trade_fee_reduction']
        
        return adjusted_data
    
    def process_currency_exchange(self, player_id: str, from_currency: CurrencyType,
                                to_currency: CurrencyType, amount: float) -> Dict[str, Any]:
        """
        Process a currency exchange and update all relevant systems.
        
        Args:
            player_id: ID of the player
            from_currency: Currency type to convert from
            to_currency: Currency type to convert to
            amount: Amount to convert
            
        Returns:
            Dictionary containing exchange results
        """
        # Process exchange
        result = self.currency.convert_currency(player_id, from_currency, to_currency, amount)
        
        if not result:
            return {'success': False}
        
        spend_transaction, earn_transaction = result
        
        # Record significant exchanges as social actions
        if amount >= 1000.0:
            self.social.record_social_action(
                action_type=SocialActionType.TRADE,
                initiator_id=player_id,
                data={
                    'from_currency': from_currency.value,
                    'to_currency': to_currency.value,
                    'amount': amount,
                    'converted_amount': earn_transaction.amount
                },
                is_public=False
            )
        
        return {
            'success': True,
            'from_currency': from_currency.value,
            'to_currency': to_currency.value,
            'amount': amount,
            'converted_amount': earn_transaction.amount,
            'exchange_rate': earn_transaction.amount / amount
        }
    
    def get_player_dashboard(self, player_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive dashboard of player data from all systems.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Dictionary containing player dashboard data
        """
        dashboard = {'player_id': player_id}
        
        # Get economic status
        economic_status = self.economy.get_player_economic_status(player_id)
        if 'error' not in economic_status:
            dashboard['economic'] = economic_status
        
        # Get social profile
        social_profile = self.social.get_social_profile(player_id)
        if social_profile:
            dashboard['social'] = {
                'display_name': social_profile.display_name,
                'title': social_profile.title,
                'bio': social_profile.bio,
                'reputation_score': social_profile.reputation_score,
                'influence_score': social_profile.influence_score,
                'friend_count': social_profile.friend_count,
                'last_active': social_profile.last_active
            }
        
        # Get faction affiliations
        dashboard['factions'] = self.social.get_player_factions(player_id)
        
        # Get friends
        dashboard['friends'] = self.social.get_player_friends(player_id)
        
        # Get recent market activity
        dashboard['market_activity'] = self._get_player_market_activity(player_id)
        
        # Get currency history
        dashboard['currency_history'] = self._get_player_currency_history(player_id)
        
        # Get social feed
        dashboard['social_feed'] = self.social.get_social_feed(player_id, 10)
        
        return dashboard
    
    def _get_player_market_activity(self, player_id: str) -> Dict[str, Any]:
        """
        Get a player's recent market activity.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Dictionary containing market activity data
        """
        # Get active listings
        active_listings = []
        for listing_id, listing in self.market.listings.items():
            if listing.seller_id == player_id and listing.is_active:
                active_listings.append({
                    'id': listing_id,
                    'item_id': listing.item_id,
                    'item_name': self.economy.items[listing.item_id].name if listing.item_id in self.economy.items else "Unknown Item",
                    'price': listing.price,
                    'currency_type': listing.currency_type.value,
                    'creation_timestamp': listing.creation_timestamp,
                    'expiration_timestamp': listing.expiration_timestamp
                })
        
        # Get active auctions
        active_auctions = []
        for auction_id, auction in self.market.auctions.items():
            if auction.seller_id == player_id and auction.is_active:
                active_auctions.append({
                    'id': auction_id,
                    'item_id': auction.item_id,
                    'item_name': self.economy.items[auction.item_id].name if auction.item_id in self.economy.items else "Unknown Item",
                    'current_bid': auction.current_bid,
                    'current_bidder_id': auction.current_bidder_id,
                    'currency_type': auction.currency_type.value,
                    'creation_timestamp': auction.creation_timestamp,
                    'expiration_timestamp': auction.expiration_timestamp
                })
        
        # Get active bids
        active_bids = []
        for auction_id, auction in self.market.auctions.items():
            if auction.is_active and auction.current_bidder_id == player_id:
                active_bids.append({
                    'auction_id': auction_id,
                    'item_id': auction.item_id,
                    'item_name': self.economy.items[auction.item_id].name if auction.item_id in self.economy.items else "Unknown Item",
                    'current_bid': auction.current_bid,
                    'seller_id': auction.seller_id,
                    'currency_type': auction.currency_type.value,
                    'expiration_timestamp': auction.expiration_timestamp
                })
        
        return {
            'active_listings': active_listings,
            'active_auctions': active_auctions,
            'active_bids': active_bids
        }
    
    def _get_player_currency_history(self, player_id: str) -> Dict[str, Any]:
        """
        Get a player's currency transaction history.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Dictionary containing currency history data
        """
        # Get recent transactions
        recent_transactions = self.currency.get_player_currency_history(
            player_id=player_id,
            limit=20
        )
        
        # Format transactions
        formatted_transactions = []
        for transaction in recent_transactions:
            formatted_transactions.append({
                'id': transaction.id,
                'currency_type': transaction.currency_type.value,
                'amount': transaction.amount,
                'action': transaction.action.value,
                'source': transaction.source,
                'timestamp': transaction.timestamp,
                'related_player_id': transaction.related_player_id,
                'notes': transaction.notes
            })
        
        # Calculate currency totals
        totals = {}
        if player_id in self.economy.inventories:
            inventory = self.economy.inventories[player_id]
            totals = {currency_type.value: amount for currency_type, amount in inventory.currencies.items()}
        
        return {
            'recent_transactions': formatted_transactions,
            'totals': totals
        }
    
    def update_systems(self) -> None:
        """
        Update all systems to simulate the passage of time.
        
        This method should be called periodically to update market conditions,
        faction dynamics, and other time-dependent features.
        """
        current_time = int(time.time())
        
        # Check if it's time for an update
        if current_time - self.last_update < self.config['update_interval_seconds']:
            return
        
        # Update economy
        self.economy.update_economy()
        
        # Update market
        self.market.update_market()
        
        # Update currency system
        self.currency.update_currency_system()
        
        # Update social system
        self.social.update_faction_dynamics()
        
        # Update last update timestamp
        self.last_update = current_time
    
    def save_state(self, directory: str) -> bool:
        """
        Save the state of all systems to files.
        
        Args:
            directory: Directory to save the state files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
            
            # Save each system
            economy_success = self.economy.save_state(os.path.join(directory, 'economy.json'))
            market_success = self.market.save_state(os.path.join(directory, 'market.json'))
            currency_success = self.currency.save_state(os.path.join(directory, 'currency.json'))
            social_success = self.social.save_state(os.path.join(directory, 'social.json'))
            
            # Save integration config
            with open(os.path.join(directory, 'integration.json'), 'w') as f:
                json.dump({
                    'config': self.config,
                    'last_update': self.last_update
                }, f, indent=2)
            
            return economy_success and market_success and currency_success and social_success
        
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self, directory: str) -> bool:
        """
        Load the state of all systems from files.
        
        Args:
            directory: Directory containing the state files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load each system
            economy_success = self.economy.load_state(os.path.join(directory, 'economy.json'))
            market_success = self.market.load_state(os.path.join(directory, 'market.json'))
            currency_success = self.currency.load_state(os.path.join(directory, 'currency.json'))
            social_success = self.social.load_state(os.path.join(directory, 'social.json'))
            
            # Load integration config
            with open(os.path.join(directory, 'integration.json'), 'r') as f:
                integration_data = json.load(f)
                self.config = integration_data.get('config', self.config)
                self.last_update = integration_data.get('last_update', int(time.time()))
            
            return economy_success and market_success and currency_success and social_success
        
        except Exception as e:
            print(f"Error loading state: {e}")
            return False
