"""
Market System for NovaLux Phase 2

This module defines the market system components, including:
- Market listings and auctions
- Dynamic pricing algorithms
- Supply and demand simulation
- Market categories and restrictions
- Player-to-player trading mechanisms

The market system integrates with the core economy system to provide
a dynamic marketplace where prices fluctuate based on player behavior,
faction influence, and global economic conditions.
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
from core.economy import (
    CurrencyType, ItemRarity, ItemType, MarketCategory,
    Currency, Item, Inventory, Transaction, EconomySystem
)


@dataclass
class MarketListing:
    """Represents a listing in the marketplace."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str = ""
    item_id: str = ""
    quantity: int = 1
    price: float = 0.0
    currency_type: CurrencyType = CurrencyType.CREDITS
    market_category: MarketCategory = MarketCategory.GENERAL
    creation_timestamp: int = field(default_factory=lambda: int(time.time()))
    expiration_timestamp: Optional[int] = None
    is_active: bool = True
    is_featured: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class Auction:
    """Represents an auction in the marketplace."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str = ""
    item_id: str = ""
    quantity: int = 1
    starting_bid: float = 0.0
    current_bid: float = 0.0
    current_bidder_id: Optional[str] = None
    currency_type: CurrencyType = CurrencyType.CREDITS
    market_category: MarketCategory = MarketCategory.GENERAL
    creation_timestamp: int = field(default_factory=lambda: int(time.time()))
    expiration_timestamp: int = 0
    min_bid_increment: float = 1.0
    is_active: bool = True
    is_featured: bool = False
    bids: List[Dict[str, Any]] = field(default_factory=list)


class MarketSystem:
    """
    Market system for the NovaLux virtual economy.
    
    This class manages market listings, auctions, and player-to-player trading,
    integrating with the core economy system.
    """
    
    def __init__(self, economy_system: EconomySystem):
        """
        Initialize the market system.
        
        Args:
            economy_system: Reference to the core economy system
        """
        self.economy = economy_system
        self.listings: Dict[str, MarketListing] = {}
        self.auctions: Dict[str, Auction] = {}
        self.price_history: Dict[str, List[Dict[str, Any]]] = {}  # item_id -> list of price points
        self.market_fees = {
            MarketCategory.GENERAL: 0.05,  # 5% fee
            MarketCategory.FACTION: 0.03,  # 3% fee for faction markets
            MarketCategory.BLACK_MARKET: 0.10,  # 10% fee for black market
            MarketCategory.LIMITED: 0.07,  # 7% fee for limited-time markets
            MarketCategory.PLAYER: 0.05   # 5% fee for player-to-player trading
        }
        
        # Market configuration
        self.config = {
            'listing_duration_days': 7,  # Default listing duration in days
            'auction_duration_days': 3,  # Default auction duration in days
            'featured_listing_cost': 50.0,  # Cost to feature a listing
            'max_active_listings_per_player': 20,  # Maximum active listings per player
            'max_active_auctions_per_player': 5,  # Maximum active auctions per player
            'min_reputation_for_market': 10.0,  # Minimum reputation to use the market
            'min_reputation_for_auctions': 50.0,  # Minimum reputation to create auctions
            'price_history_max_points': 100,  # Maximum price history points to store per item
            'price_history_interval_hours': 6  # Interval between price history recordings
        }
    
    def create_listing(self, listing_data: Dict[str, Any]) -> Optional[MarketListing]:
        """
        Create a new market listing.
        
        Args:
            listing_data: Dictionary containing listing details
            
        Returns:
            Created MarketListing object or None if creation failed
        """
        seller_id = listing_data.get('seller_id', '')
        item_id = listing_data.get('item_id', '')
        quantity = listing_data.get('quantity', 1)
        price = listing_data.get('price', 0.0)
        currency_type = listing_data.get('currency_type', CurrencyType.CREDITS)
        market_category = listing_data.get('market_category', MarketCategory.GENERAL)
        is_featured = listing_data.get('is_featured', False)
        
        # Validate seller and item
        if not seller_id or not item_id:
            return None
        
        if seller_id not in self.economy.inventories:
            return None
        
        if item_id not in self.economy.items:
            return None
        
        # Check if seller has the item
        seller_inventory = self.economy.inventories[seller_id]
        if item_id not in seller_inventory.items or seller_inventory.items[item_id] < quantity:
            return None
        
        # Check if seller has reached the maximum number of active listings
        seller_listings = [l for l in self.listings.values() 
                          if l.seller_id == seller_id and l.is_active]
        if len(seller_listings) >= self.config['max_active_listings_per_player']:
            return None
        
        # Check if seller has enough reputation
        if CurrencyType.REPUTATION in seller_inventory.currencies:
            reputation = seller_inventory.currencies[CurrencyType.REPUTATION]
            if reputation < self.config['min_reputation_for_market']:
                return None
        else:
            return None
        
        # Calculate expiration timestamp
        duration_seconds = self.config['listing_duration_days'] * 24 * 60 * 60
        expiration_timestamp = int(time.time()) + duration_seconds
        
        # If featured, charge the fee
        if is_featured:
            if not seller_inventory.remove_currency(CurrencyType.CREDITS, self.config['featured_listing_cost']):
                is_featured = False
        
        # Remove item from seller's inventory
        if not seller_inventory.remove_item(item_id, quantity):
            return None
        
        # Create listing
        listing = MarketListing(
            seller_id=seller_id,
            item_id=item_id,
            quantity=quantity,
            price=price,
            currency_type=currency_type,
            market_category=market_category,
            expiration_timestamp=expiration_timestamp,
            is_featured=is_featured
        )
        
        # Add to listings
        self.listings[listing.id] = listing
        
        return listing
    
    def cancel_listing(self, listing_id: str) -> bool:
        """
        Cancel a market listing and return the item to the seller.
        
        Args:
            listing_id: ID of the listing to cancel
            
        Returns:
            True if successful, False otherwise
        """
        if listing_id not in self.listings:
            return False
        
        listing = self.listings[listing_id]
        
        if not listing.is_active:
            return False
        
        # Return item to seller
        seller_id = listing.seller_id
        if seller_id in self.economy.inventories:
            seller_inventory = self.economy.inventories[seller_id]
            seller_inventory.add_item(listing.item_id, listing.quantity)
        
        # Mark listing as inactive
        listing.is_active = False
        
        return True
    
    def purchase_listing(self, listing_id: str, buyer_id: str) -> Optional[Transaction]:
        """
        Purchase an item from a market listing.
        
        Args:
            listing_id: ID of the listing to purchase
            buyer_id: ID of the buyer
            
        Returns:
            Completed Transaction object or None if purchase failed
        """
        if listing_id not in self.listings:
            return None
        
        listing = self.listings[listing_id]
        
        if not listing.is_active:
            return None
        
        if buyer_id not in self.economy.inventories:
            return None
        
        # Create transaction data
        transaction_data = {
            'seller_id': listing.seller_id,
            'buyer_id': buyer_id,
            'item_id': listing.item_id,
            'item_quantity': listing.quantity,
            'currency_type': listing.currency_type,
            'amount': listing.price,
            'market_category': listing.market_category,
            'notes': f"Market purchase: Listing {listing_id}"
        }
        
        # Process transaction
        transaction = self.economy.process_transaction(transaction_data)
        
        if transaction and transaction.is_completed:
            # Mark listing as inactive
            listing.is_active = False
            
            # Record price in history
            self._record_price_history(listing.item_id, listing.price, listing.currency_type)
            
            return transaction
        
        return None
    
    def create_auction(self, auction_data: Dict[str, Any]) -> Optional[Auction]:
        """
        Create a new auction.
        
        Args:
            auction_data: Dictionary containing auction details
            
        Returns:
            Created Auction object or None if creation failed
        """
        seller_id = auction_data.get('seller_id', '')
        item_id = auction_data.get('item_id', '')
        quantity = auction_data.get('quantity', 1)
        starting_bid = auction_data.get('starting_bid', 0.0)
        currency_type = auction_data.get('currency_type', CurrencyType.CREDITS)
        market_category = auction_data.get('market_category', MarketCategory.GENERAL)
        is_featured = auction_data.get('is_featured', False)
        duration_days = auction_data.get('duration_days', self.config['auction_duration_days'])
        min_bid_increment = auction_data.get('min_bid_increment', 1.0)
        
        # Validate seller and item
        if not seller_id or not item_id:
            return None
        
        if seller_id not in self.economy.inventories:
            return None
        
        if item_id not in self.economy.items:
            return None
        
        # Check if seller has the item
        seller_inventory = self.economy.inventories[seller_id]
        if item_id not in seller_inventory.items or seller_inventory.items[item_id] < quantity:
            return None
        
        # Check if seller has reached the maximum number of active auctions
        seller_auctions = [a for a in self.auctions.values() 
                          if a.seller_id == seller_id and a.is_active]
        if len(seller_auctions) >= self.config['max_active_auctions_per_player']:
            return None
        
        # Check if seller has enough reputation
        if CurrencyType.REPUTATION in seller_inventory.currencies:
            reputation = seller_inventory.currencies[CurrencyType.REPUTATION]
            if reputation < self.config['min_reputation_for_auctions']:
                return None
        else:
            return None
        
        # Calculate expiration timestamp
        duration_seconds = duration_days * 24 * 60 * 60
        expiration_timestamp = int(time.time()) + duration_seconds
        
        # If featured, charge the fee
        if is_featured:
            if not seller_inventory.remove_currency(CurrencyType.CREDITS, self.config['featured_listing_cost']):
                is_featured = False
        
        # Remove item from seller's inventory
        if not seller_inventory.remove_item(item_id, quantity):
            return None
        
        # Create auction
        auction = Auction(
            seller_id=seller_id,
            item_id=item_id,
            quantity=quantity,
            starting_bid=starting_bid,
            current_bid=starting_bid,
            currency_type=currency_type,
            market_category=market_category,
            expiration_timestamp=expiration_timestamp,
            min_bid_increment=min_bid_increment,
            is_featured=is_featured
        )
        
        # Add to auctions
        self.auctions[auction.id] = auction
        
        return auction
    
    def place_bid(self, auction_id: str, bidder_id: str, bid_amount: float) -> bool:
        """
        Place a bid on an auction.
        
        Args:
            auction_id: ID of the auction
            bidder_id: ID of the bidder
            bid_amount: Bid amount
            
        Returns:
            True if bid was successful, False otherwise
        """
        if auction_id not in self.auctions:
            return False
        
        auction = self.auctions[auction_id]
        
        if not auction.is_active:
            return False
        
        if int(time.time()) > auction.expiration_timestamp:
            return False
        
        if bidder_id not in self.economy.inventories:
            return False
        
        # Check if bid is high enough
        if bid_amount < auction.current_bid + auction.min_bid_increment:
            return False
        
        # Check if bidder has enough currency
        bidder_inventory = self.economy.inventories[bidder_id]
        if not bidder_inventory.remove_currency(auction.currency_type, bid_amount):
            return False
        
        # Refund previous bidder if there was one
        if auction.current_bidder_id:
            previous_bidder_inventory = self.economy.inventories.get(auction.current_bidder_id)
            if previous_bidder_inventory:
                previous_bidder_inventory.add_currency(auction.currency_type, auction.current_bid)
        
        # Update auction
        auction.current_bid = bid_amount
        auction.current_bidder_id = bidder_id
        
        # Record bid
        auction.bids.append({
            'bidder_id': bidder_id,
            'amount': bid_amount,
            'timestamp': int(time.time())
        })
        
        return True
    
    def finalize_auction(self, auction_id: str) -> Optional[Transaction]:
        """
        Finalize an auction after it has expired.
        
        Args:
            auction_id: ID of the auction to finalize
            
        Returns:
            Completed Transaction object or None if finalization failed
        """
        if auction_id not in self.auctions:
            return None
        
        auction = self.auctions[auction_id]
        
        if not auction.is_active:
            return None
        
        # Check if auction has expired
        if int(time.time()) <= auction.expiration_timestamp:
            return None
        
        # If no bids, return item to seller
        if not auction.current_bidder_id:
            seller_inventory = self.economy.inventories.get(auction.seller_id)
            if seller_inventory:
                seller_inventory.add_item(auction.item_id, auction.quantity)
            
            auction.is_active = False
            return None
        
        # Create transaction data
        transaction_data = {
            'seller_id': auction.seller_id,
            'buyer_id': auction.current_bidder_id,
            'item_id': auction.item_id,
            'item_quantity': auction.quantity,
            'currency_type': auction.currency_type,
            'amount': auction.current_bid,
            'market_category': auction.market_category,
            'notes': f"Auction finalized: {auction_id}"
        }
        
        # Process transaction (note: payment already held from bidder)
        # This is a special case where we don't charge the buyer again
        
        # Add item directly to buyer's inventory
        buyer_inventory = self.economy.inventories.get(auction.current_bidder_id)
        if not buyer_inventory:
            return None
        
        if not buyer_inventory.add_item(auction.item_id, auction.quantity):
            # If buyer's inventory is full, refund and return item to seller
            buyer_inventory.add_currency(auction.currency_type, auction.current_bid)
            
            seller_inventory = self.economy.inventories.get(auction.seller_id)
            if seller_inventory:
                seller_inventory.add_item(auction.item_id, auction.quantity)
            
            auction.is_active = False
            return None
        
        # Pay seller (minus fee)
        seller_inventory = self.economy.inventories.get(auction.seller_id)
        if seller_inventory:
            fee_rate = self.market_fees.get(auction.market_category, 0.05)
            fee_amount = auction.current_bid * fee_rate
            seller_payment = auction.current_bid - fee_amount
            
            seller_inventory.add_currency(auction.currency_type, seller_payment)
        
        # Create transaction record
        transaction = Transaction(
            seller_id=auction.seller_id,
            buyer_id=auction.current_bidder_id,
            item_id=auction.item_id,
            item_quantity=auction.quantity,
            currency_type=auction.currency_type,
            amount=auction.current_bid,
            transaction_fee=fee_amount,
            market_category=auction.market_category,
            is_completed=True,
            notes=f"Auction finalized: {auction_id}"
        )
        
        # Add to transaction history
        self.economy.transactions.append(transaction)
        
        # Mark auction as inactive
        auction.is_active = False
        
        # Record price in history
        self._record_price_history(auction.item_id, auction.current_bid, auction.currency_type)
        
        return transaction
    
    def _record_price_history(self, item_id: str, price: float, currency_type: CurrencyType) -> None:
        """
        Record a price point in the item's price history.
        
        Args:
            item_id: ID of the item
            price: Price point to record
            currency_type: Currency type of the price
        """
        if item_id not in self.price_history:
            self.price_history[item_id] = []
        
        # Add price point
        self.price_history[item_id].append({
            'timestamp': int(time.time()),
            'price': price,
            'currency_type': currency_type.value
        })
        
        # Trim history if needed
        if len(self.price_history[item_id]) > self.config['price_history_max_points']:
            self.price_history[item_id] = self.price_history[item_id][-self.config['price_history_max_points']:]
    
    def get_price_history(self, item_id: str) -> List[Dict[str, Any]]:
        """
        Get the price history for an item.
        
        Args:
            item_id: ID of the item
            
        Returns:
            List of price points
        """
        return self.price_history.get(item_id, [])
    
    def get_market_analytics(self) -> Dict[str, Any]:
        """
        Get analytics data for the market.
        
        Returns:
            Dictionary containing market analytics
        """
        # Calculate total market volume
        total_volume = 0.0
        transactions_last_day = []
        
        current_time = int(time.time())
        one_day_ago = current_time - (24 * 60 * 60)
        
        for transaction in self.economy.transactions:
            if transaction.is_completed and transaction.timestamp >= one_day_ago:
                transactions_last_day.append(transaction)
                
                # Convert to credits for consistent measurement
                if transaction.currency_type == CurrencyType.CREDITS:
                    total_volume += transaction.amount
                else:
                    # Use exchange rate to convert to credits
                    currency = self.economy.currencies.get(transaction.currency_type)
                    if currency:
                        total_volume += transaction.amount * currency.exchange_rate
        
        # Calculate most traded items
        item_volumes = {}
        for transaction in transactions_last_day:
            if transaction.item_id:
                if transaction.item_id in item_volumes:
                    item_volumes[transaction.item_id] += 1
                else:
                    item_volumes[transaction.item_id] = 1
        
        most_traded_items = sorted(item_volumes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate market category distribution
        category_distribution = {}
        for transaction in transactions_last_day:
            category = transaction.market_category.value
            if category in category_distribution:
                category_distribution[category] += 1
            else:
                category_distribution[category] = 1
        
        # Calculate active listings and auctions
        active_listings = len([l for l in self.listings.values() if l.is_active])
        active_auctions = len([a for a in self.auctions.values() if a.is_active])
        
        return {
            'total_volume_last_24h': total_volume,
            'transaction_count_last_24h': len(transactions_last_day),
            'most_traded_items': [
                {
                    'item_id': item_id,
                    'name': self.economy.items[item_id].name if item_id in self.economy.items else 'Unknown',
                    'trade_count': count
                }
                for item_id, count in most_traded_items
            ],
            'category_distribution': category_distribution,
            'active_listings': active_listings,
            'active_auctions': active_auctions
        }
    
    def update_market(self) -> None:
        """
        Update the market state.
        
        This method should be called periodically to finalize expired auctions,
        remove expired listings, and update market conditions.
        """
        current_time = int(time.time())
        
        # Finalize expired auctions
        for auction_id, auction in list(self.auctions.items()):
            if auction.is_active and current_time > auction.expiration_timestamp:
                self.finalize_auction(auction_id)
        
        # Remove expired listings
        for listing_id, listing in list(self.listings.items()):
            if listing.is_active and listing.expiration_timestamp and current_time > listing.expiration_timestamp:
                self.cancel_listing(listing_id)
        
        # Update market conditions based on recent activity
        self._update_market_conditions()
    
    def _update_market_conditions(self) -> None:
        """Update market conditions based on recent activity."""
        # This would be a more sophisticated algorithm in a real implementation
        # For this prototype, we'll use a simple approach
        
        # Calculate average prices for each item
        for item_id, history in self.price_history.items():
            if not history:
                continue
            
            # Get recent price points (last 10)
            recent_prices = [point['price'] for point in history[-10:]]
            if not recent_prices:
                continue
            
            avg_price = sum(recent_prices) / len(recent_prices)
            
            # Adjust supply/demand factor based on price trend
            if item_id in self.economy.items:
                item = self.economy.items[item_id]
                base_value = item.base_value
                
                if base_value > 0:
                    price_ratio = avg_price / base_value
                    
                    # If price is higher than base value, increase supply/demand factor
                    # If price is lower than base value, decrease supply/demand factor
                    adjustment = (price_ratio - 1.0) * 0.01
                    
                    # Apply adjustment to global supply/demand factor
                    self.economy.market_conditions['supply_demand_factor'] += adjustment
                    
                    # Cap at reasonable limits
                    self.economy.market_conditions['supply_demand_factor'] = max(0.5, min(2.0, self.economy.market_conditions['supply_demand_factor']))
        
        # Update market volatility based on transaction volume
        transactions_last_day = [t for t in self.economy.transactions if t.timestamp >= int(time.time()) - (24 * 60 * 60)]
        transaction_count = len(transactions_last_day)
        
        # Higher transaction volume = lower volatility
        if transaction_count > 100:
            self.economy.market_conditions['market_volatility'] = 0.05
        elif transaction_count > 50:
            self.economy.market_conditions['market_volatility'] = 0.1
        elif transaction_count > 20:
            self.economy.market_conditions['market_volatility'] = 0.15
        else:
            self.economy.market_conditions['market_volatility'] = 0.2
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the market to a file.
        
        Args:
            filepath: Path to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to serializable format
            state = {
                'listings': {listing_id: {
                    'id': listing.id,
                    'seller_id': listing.seller_id,
                    'item_id': listing.item_id,
                    'quantity': listing.quantity,
                    'price': listing.price,
                    'currency_type': listing.currency_type.value,
                    'market_category': listing.market_category.value,
                    'creation_timestamp': listing.creation_timestamp,
                    'expiration_timestamp': listing.expiration_timestamp,
                    'is_active': listing.is_active,
                    'is_featured': listing.is_featured,
                    'tags': listing.tags
                } for listing_id, listing in self.listings.items()},
                
                'auctions': {auction_id: {
                    'id': auction.id,
                    'seller_id': auction.seller_id,
                    'item_id': auction.item_id,
                    'quantity': auction.quantity,
                    'starting_bid': auction.starting_bid,
                    'current_bid': auction.current_bid,
                    'current_bidder_id': auction.current_bidder_id,
                    'currency_type': auction.currency_type.value,
                    'market_category': auction.market_category.value,
                    'creation_timestamp': auction.creation_timestamp,
                    'expiration_timestamp': auction.expiration_timestamp,
                    'min_bid_increment': auction.min_bid_increment,
                    'is_active': auction.is_active,
                    'is_featured': auction.is_featured,
                    'bids': auction.bids
                } for auction_id, auction in self.auctions.items()},
                
                'price_history': self.price_history,
                'market_fees': {category.value: fee for category, fee in self.market_fees.items()},
                'config': self.config
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving market state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the state of the market from a file.
        
        Args:
            filepath: Path to load the state from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Load listings
            self.listings = {}
            for listing_id, listing_data in state.get('listings', {}).items():
                self.listings[listing_id] = MarketListing(
                    id=listing_data['id'],
                    seller_id=listing_data['seller_id'],
                    item_id=listing_data['item_id'],
                    quantity=listing_data['quantity'],
                    price=listing_data['price'],
                    currency_type=CurrencyType(listing_data['currency_type']),
                    market_category=MarketCategory(listing_data['market_category']),
                    creation_timestamp=listing_data['creation_timestamp'],
                    expiration_timestamp=listing_data['expiration_timestamp'],
                    is_active=listing_data['is_active'],
                    is_featured=listing_data['is_featured'],
                    tags=listing_data['tags']
                )
            
            # Load auctions
            self.auctions = {}
            for auction_id, auction_data in state.get('auctions', {}).items():
                self.auctions[auction_id] = Auction(
                    id=auction_data['id'],
                    seller_id=auction_data['seller_id'],
                    item_id=auction_data['item_id'],
                    quantity=auction_data['quantity'],
                    starting_bid=auction_data['starting_bid'],
                    current_bid=auction_data['current_bid'],
                    current_bidder_id=auction_data['current_bidder_id'],
                    currency_type=CurrencyType(auction_data['currency_type']),
                    market_category=MarketCategory(auction_data['market_category']),
                    creation_timestamp=auction_data['creation_timestamp'],
                    expiration_timestamp=auction_data['expiration_timestamp'],
                    min_bid_increment=auction_data['min_bid_increment'],
                    is_active=auction_data['is_active'],
                    is_featured=auction_data['is_featured'],
                    bids=auction_data['bids']
                )
            
            # Load price history
            self.price_history = state.get('price_history', {})
            
            # Load market fees
            market_fees = state.get('market_fees', {})
            self.market_fees = {MarketCategory(category): fee for category, fee in market_fees.items()}
            
            # Load config
            self.config = state.get('config', self.config)
            
            return True
        
        except Exception as e:
            print(f"Error loading market state: {e}")
            return False
