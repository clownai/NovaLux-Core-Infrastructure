"""
Virtual Economy System for NovaLux Phase 2

This module defines the core components of the virtual economy system, including:
- Currency management
- Item definitions and properties
- Market dynamics and pricing
- Transaction processing
- Economic balancing mechanisms

The economy system is designed to be dynamic and responsive to player behavior,
with prices that fluctuate based on supply and demand, rarity-based item values,
and faction-influenced market conditions.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import uuid
import time
import json
import random
import math
from enum import Enum
from dataclasses import dataclass, field


class CurrencyType(Enum):
    """Types of currency in the NovaLux economy."""
    CREDITS = "credits"  # Standard currency
    QUANTUM_BITS = "quantum_bits"  # Premium currency
    FACTION_INFLUENCE = "faction_influence"  # Faction-specific currency
    REPUTATION = "reputation"  # Social currency


class ItemRarity(Enum):
    """Rarity levels for items in the NovaLux economy."""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5
    MYTHIC = 6


class ItemType(Enum):
    """Types of items in the NovaLux economy."""
    COSMETIC = "cosmetic"  # Visual customizations
    FUNCTIONAL = "functional"  # Items with gameplay effects
    CONSUMABLE = "consumable"  # One-time use items
    COLLECTIBLE = "collectible"  # Rare items for collection
    BLUEPRINT = "blueprint"  # Crafting recipes
    TOKEN = "token"  # Special access tokens


class MarketCategory(Enum):
    """Categories in the NovaLux marketplace."""
    GENERAL = "general"  # General items
    FACTION = "faction"  # Faction-specific items
    BLACK_MARKET = "black_market"  # Rare and exclusive items
    LIMITED = "limited"  # Time-limited offers
    PLAYER = "player"  # Player-to-player marketplace


@dataclass
class Currency:
    """Represents a currency in the NovaLux economy."""
    type: CurrencyType
    name: str
    symbol: str
    description: str
    exchange_rate: float = 1.0  # Exchange rate to credits (base currency)
    is_tradable: bool = True
    is_earnable: bool = True
    daily_limit: Optional[int] = None
    faction: Optional[str] = None


@dataclass
class ItemAttribute:
    """Represents an attribute of an item."""
    name: str
    value: Union[str, int, float, bool]
    description: str = ""
    is_hidden: bool = False


@dataclass
class Item:
    """Represents an item in the NovaLux economy."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: ItemType = ItemType.COSMETIC
    rarity: ItemRarity = ItemRarity.COMMON
    base_value: float = 0.0
    currency_type: CurrencyType = CurrencyType.CREDITS
    is_tradable: bool = True
    is_consumable: bool = False
    durability: Optional[int] = None
    cooldown: Optional[int] = None
    level_requirement: int = 0
    faction_requirement: Optional[str] = None
    attributes: List[ItemAttribute] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    creation_timestamp: int = field(default_factory=lambda: int(time.time()))
    
    def calculate_value(self, market_conditions: Dict[str, Any]) -> float:
        """
        Calculate the current value of the item based on market conditions.
        
        Args:
            market_conditions: Dictionary containing market factors
            
        Returns:
            Current value of the item
        """
        # Start with base value
        value = self.base_value
        
        # Apply rarity multiplier
        rarity_multipliers = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.5,
            ItemRarity.RARE: 3.0,
            ItemRarity.EPIC: 7.0,
            ItemRarity.LEGENDARY: 15.0,
            ItemRarity.MYTHIC: 40.0
        }
        value *= rarity_multipliers.get(self.rarity, 1.0)
        
        # Apply supply/demand factor
        supply_demand_factor = market_conditions.get('supply_demand_factor', 1.0)
        value *= supply_demand_factor
        
        # Apply faction influence if applicable
        if self.faction_requirement:
            faction_influence = market_conditions.get('faction_influence', {}).get(self.faction_requirement, 1.0)
            value *= faction_influence
        
        # Apply global economy factor
        global_economy_factor = market_conditions.get('global_economy_factor', 1.0)
        value *= global_economy_factor
        
        # Apply player skill factor if applicable
        if 'skill' in self.tags:
            player_skill_factor = market_conditions.get('player_skill_factor', 1.0)
            value *= player_skill_factor
        
        # Apply time-based factors for collectibles
        if self.type == ItemType.COLLECTIBLE:
            age_in_days = (int(time.time()) - self.creation_timestamp) / (60 * 60 * 24)
            age_factor = min(1.0 + (age_in_days / 365), 2.0)  # Max 2x value after 1 year
            value *= age_factor
        
        return round(value, 2)


@dataclass
class Inventory:
    """Represents a player's inventory."""
    player_id: str
    items: Dict[str, int] = field(default_factory=dict)  # item_id -> quantity
    currencies: Dict[CurrencyType, float] = field(default_factory=dict)
    max_slots: int = 100
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Add an item to the inventory.
        
        Args:
            item_id: ID of the item to add
            quantity: Quantity to add
            
        Returns:
            True if successful, False if inventory is full
        """
        current_items = sum(self.items.values())
        if current_items + quantity > self.max_slots:
            return False
        
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
        
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove an item from the inventory.
        
        Args:
            item_id: ID of the item to remove
            quantity: Quantity to remove
            
        Returns:
            True if successful, False if not enough items
        """
        if item_id not in self.items or self.items[item_id] < quantity:
            return False
        
        self.items[item_id] -= quantity
        
        if self.items[item_id] == 0:
            del self.items[item_id]
        
        return True
    
    def add_currency(self, currency_type: CurrencyType, amount: float) -> None:
        """
        Add currency to the inventory.
        
        Args:
            currency_type: Type of currency to add
            amount: Amount to add
        """
        if currency_type in self.currencies:
            self.currencies[currency_type] += amount
        else:
            self.currencies[currency_type] = amount
    
    def remove_currency(self, currency_type: CurrencyType, amount: float) -> bool:
        """
        Remove currency from the inventory.
        
        Args:
            currency_type: Type of currency to remove
            amount: Amount to remove
            
        Returns:
            True if successful, False if not enough currency
        """
        if currency_type not in self.currencies or self.currencies[currency_type] < amount:
            return False
        
        self.currencies[currency_type] -= amount
        return True
    
    def get_total_value(self, item_catalog: Dict[str, Item], market_conditions: Dict[str, Any]) -> Dict[CurrencyType, float]:
        """
        Calculate the total value of the inventory.
        
        Args:
            item_catalog: Dictionary of all items (item_id -> Item)
            market_conditions: Current market conditions
            
        Returns:
            Dictionary of currency types to total values
        """
        total_values = {currency_type: amount for currency_type, amount in self.currencies.items()}
        
        for item_id, quantity in self.items.items():
            if item_id in item_catalog:
                item = item_catalog[item_id]
                value = item.calculate_value(market_conditions) * quantity
                
                if item.currency_type in total_values:
                    total_values[item.currency_type] += value
                else:
                    total_values[item.currency_type] = value
        
        return total_values


@dataclass
class Transaction:
    """Represents a transaction in the NovaLux economy."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = field(default_factory=lambda: int(time.time()))
    seller_id: Optional[str] = None  # None for system seller
    buyer_id: str = ""
    item_id: Optional[str] = None
    item_quantity: int = 0
    currency_type: CurrencyType = CurrencyType.CREDITS
    amount: float = 0.0
    transaction_fee: float = 0.0
    market_category: MarketCategory = MarketCategory.GENERAL
    is_completed: bool = False
    is_refunded: bool = False
    notes: str = ""


class EconomySystem:
    """
    Core class for the NovaLux virtual economy system.
    
    This class manages the overall economy, including currencies, items,
    market conditions, and transactions.
    """
    
    def __init__(self):
        """Initialize the economy system."""
        self.currencies: Dict[CurrencyType, Currency] = {}
        self.items: Dict[str, Item] = {}
        self.inventories: Dict[str, Inventory] = {}
        self.transactions: List[Transaction] = []
        self.market_conditions: Dict[str, Any] = {
            'global_economy_factor': 1.0,
            'supply_demand_factor': 1.0,
            'faction_influence': {
                'Architects': 1.0,
                'Guardians': 1.0,
                'Seekers': 1.0,
                'Shadows': 1.0
            },
            'player_skill_factor': 1.0,
            'market_volatility': 0.1
        }
        
        # Initialize default currencies
        self._initialize_currencies()
    
    def _initialize_currencies(self) -> None:
        """Initialize the default currencies in the economy."""
        self.currencies[CurrencyType.CREDITS] = Currency(
            type=CurrencyType.CREDITS,
            name="Credits",
            symbol="₵",
            description="Standard currency used throughout NovaLux.",
            exchange_rate=1.0,
            is_tradable=True,
            is_earnable=True
        )
        
        self.currencies[CurrencyType.QUANTUM_BITS] = Currency(
            type=CurrencyType.QUANTUM_BITS,
            name="Quantum Bits",
            symbol="Qb",
            description="Premium currency for exclusive items and features.",
            exchange_rate=100.0,  # 1 Qb = 100 Credits
            is_tradable=False,
            is_earnable=True,
            daily_limit=10
        )
        
        self.currencies[CurrencyType.FACTION_INFLUENCE] = Currency(
            type=CurrencyType.FACTION_INFLUENCE,
            name="Faction Influence",
            symbol="FI",
            description="Currency representing influence with factions.",
            exchange_rate=50.0,
            is_tradable=False,
            is_earnable=True
        )
        
        self.currencies[CurrencyType.REPUTATION] = Currency(
            type=CurrencyType.REPUTATION,
            name="Reputation",
            symbol="Rep",
            description="Social currency earned through positive interactions.",
            exchange_rate=20.0,
            is_tradable=False,
            is_earnable=True
        )
    
    def create_item(self, item_data: Dict[str, Any]) -> Item:
        """
        Create a new item in the economy.
        
        Args:
            item_data: Dictionary containing item properties
            
        Returns:
            Created Item object
        """
        item = Item(
            name=item_data.get('name', ''),
            description=item_data.get('description', ''),
            type=item_data.get('type', ItemType.COSMETIC),
            rarity=item_data.get('rarity', ItemRarity.COMMON),
            base_value=item_data.get('base_value', 0.0),
            currency_type=item_data.get('currency_type', CurrencyType.CREDITS),
            is_tradable=item_data.get('is_tradable', True),
            is_consumable=item_data.get('is_consumable', False),
            durability=item_data.get('durability'),
            cooldown=item_data.get('cooldown'),
            level_requirement=item_data.get('level_requirement', 0),
            faction_requirement=item_data.get('faction_requirement'),
            attributes=item_data.get('attributes', []),
            tags=item_data.get('tags', [])
        )
        
        self.items[item.id] = item
        return item
    
    def create_inventory(self, player_id: str, max_slots: int = 100) -> Inventory:
        """
        Create a new inventory for a player.
        
        Args:
            player_id: ID of the player
            max_slots: Maximum number of item slots
            
        Returns:
            Created Inventory object
        """
        inventory = Inventory(player_id=player_id, max_slots=max_slots)
        
        # Initialize with starting currencies
        inventory.add_currency(CurrencyType.CREDITS, 1000.0)
        inventory.add_currency(CurrencyType.QUANTUM_BITS, 10.0)
        
        self.inventories[player_id] = inventory
        return inventory
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Transaction]:
        """
        Process a transaction in the economy.
        
        Args:
            transaction_data: Dictionary containing transaction details
            
        Returns:
            Completed Transaction object or None if transaction failed
        """
        # Create transaction object
        transaction = Transaction(
            seller_id=transaction_data.get('seller_id'),
            buyer_id=transaction_data.get('buyer_id'),
            item_id=transaction_data.get('item_id'),
            item_quantity=transaction_data.get('item_quantity', 1),
            currency_type=transaction_data.get('currency_type', CurrencyType.CREDITS),
            amount=transaction_data.get('amount', 0.0),
            market_category=transaction_data.get('market_category', MarketCategory.GENERAL),
            notes=transaction_data.get('notes', '')
        )
        
        # Calculate transaction fee
        fee_rate = 0.05  # 5% fee
        if transaction.market_category == MarketCategory.BLACK_MARKET:
            fee_rate = 0.10  # 10% fee for black market
        
        transaction.transaction_fee = round(transaction.amount * fee_rate, 2)
        
        # Verify buyer has enough currency
        buyer_inventory = self.inventories.get(transaction.buyer_id)
        if not buyer_inventory:
            return None
        
        total_cost = transaction.amount + transaction.transaction_fee
        if not buyer_inventory.remove_currency(transaction.currency_type, total_cost):
            return None
        
        # If this is an item transaction
        if transaction.item_id and transaction.item_quantity > 0:
            # If seller is a player, remove item from seller inventory and add currency
            if transaction.seller_id and transaction.seller_id in self.inventories:
                seller_inventory = self.inventories[transaction.seller_id]
                
                if not seller_inventory.remove_item(transaction.item_id, transaction.item_quantity):
                    # Refund buyer if seller doesn't have the item
                    buyer_inventory.add_currency(transaction.currency_type, total_cost)
                    return None
                
                # Add payment to seller (minus fee)
                seller_inventory.add_currency(transaction.currency_type, transaction.amount - transaction.transaction_fee)
            
            # Add item to buyer inventory
            if not buyer_inventory.add_item(transaction.item_id, transaction.item_quantity):
                # Refund buyer if inventory is full
                buyer_inventory.add_currency(transaction.currency_type, total_cost)
                
                # Return item to seller if applicable
                if transaction.seller_id and transaction.seller_id in self.inventories:
                    seller_inventory = self.inventories[transaction.seller_id]
                    seller_inventory.add_item(transaction.item_id, transaction.item_quantity)
                    seller_inventory.remove_currency(transaction.currency_type, transaction.amount - transaction.transaction_fee)
                
                return None
        
        # Mark transaction as completed
        transaction.is_completed = True
        
        # Add to transaction history
        self.transactions.append(transaction)
        
        # Update market conditions based on transaction
        self._update_market_conditions(transaction)
        
        return transaction
    
    def _update_market_conditions(self, transaction: Transaction) -> None:
        """
        Update market conditions based on a completed transaction.
        
        Args:
            transaction: Completed transaction
        """
        if not transaction.is_completed:
            return
        
        # Update supply/demand for the item
        if transaction.item_id:
            # Simple algorithm: transactions increase price slightly
            # More sophisticated algorithms would track volume over time
            item = self.items.get(transaction.item_id)
            if item:
                # Adjust supply/demand factor based on rarity
                rarity_impact = {
                    ItemRarity.COMMON: 0.001,
                    ItemRarity.UNCOMMON: 0.002,
                    ItemRarity.RARE: 0.005,
                    ItemRarity.EPIC: 0.01,
                    ItemRarity.LEGENDARY: 0.02,
                    ItemRarity.MYTHIC: 0.05
                }
                
                impact = rarity_impact.get(item.rarity, 0.001) * transaction.item_quantity
                
                # Apply randomness to simulate market fluctuations
                volatility = self.market_conditions['market_volatility']
                random_factor = 1.0 + random.uniform(-volatility, volatility)
                impact *= random_factor
                
                # Update supply/demand factor
                self.market_conditions['supply_demand_factor'] *= (1.0 + impact)
                
                # Cap at reasonable limits
                self.market_conditions['supply_demand_factor'] = max(0.5, min(2.0, self.market_conditions['supply_demand_factor']))
        
        # Update faction influence if applicable
        if transaction.item_id and transaction.item_quantity > 0:
            item = self.items.get(transaction.item_id)
            if item and item.faction_requirement:
                faction = item.faction_requirement
                if faction in self.market_conditions['faction_influence']:
                    # Increase influence of the faction whose items are being bought
                    self.market_conditions['faction_influence'][faction] *= 1.001
                    
                    # Cap at reasonable limits
                    self.market_conditions['faction_influence'][faction] = min(1.5, self.market_conditions['faction_influence'][faction])
    
    def update_economy(self) -> None:
        """
        Update the overall economy state.
        
        This method should be called periodically to simulate natural
        economic fluctuations and balance the economy.
        """
        # Apply random fluctuations to global economy factor
        volatility = self.market_conditions['market_volatility']
        random_factor = 1.0 + random.uniform(-volatility, volatility)
        self.market_conditions['global_economy_factor'] *= random_factor
        
        # Cap at reasonable limits
        self.market_conditions['global_economy_factor'] = max(0.8, min(1.2, self.market_conditions['global_economy_factor']))
        
        # Gradually normalize supply/demand factor
        current = self.market_conditions['supply_demand_factor']
        self.market_conditions['supply_demand_factor'] = current * 0.99 + 1.0 * 0.01
        
        # Gradually normalize faction influences
        for faction in self.market_conditions['faction_influence']:
            current = self.market_conditions['faction_influence'][faction]
            self.market_conditions['faction_influence'][faction] = current * 0.99 + 1.0 * 0.01
    
    def get_market_listings(self, category: Optional[MarketCategory] = None, 
                           faction: Optional[str] = None,
                           item_type: Optional[ItemType] = None,
                           min_price: Optional[float] = None,
                           max_price: Optional[float] = None,
                           sort_by: str = "price_asc") -> List[Dict[str, Any]]:
        """
        Get current market listings based on filters.
        
        Args:
            category: Filter by market category
            faction: Filter by faction requirement
            item_type: Filter by item type
            min_price: Minimum price
            max_price: Maximum price
            sort_by: Sorting method (price_asc, price_desc, rarity_asc, rarity_desc)
            
        Returns:
            List of market listings
        """
        listings = []
        
        for item_id, item in self.items.items():
            # Skip items that don't match filters
            if category and item_id not in self._get_category_items(category):
                continue
            
            if faction and item.faction_requirement != faction:
                continue
            
            if item_type and item.type != item_type:
                continue
            
            # Calculate current price
            price = item.calculate_value(self.market_conditions)
            
            if min_price is not None and price < min_price:
                continue
            
            if max_price is not None and price > max_price:
                continue
            
            # Add to listings
            listings.append({
                'item_id': item_id,
                'name': item.name,
                'description': item.description,
                'type': item.type.value,
                'rarity': item.rarity.value,
                'price': price,
                'currency_type': item.currency_type.value,
                'faction_requirement': item.faction_requirement
            })
        
        # Sort listings
        if sort_by == "price_asc":
            listings.sort(key=lambda x: x['price'])
        elif sort_by == "price_desc":
            listings.sort(key=lambda x: x['price'], reverse=True)
        elif sort_by == "rarity_asc":
            listings.sort(key=lambda x: x['rarity'])
        elif sort_by == "rarity_desc":
            listings.sort(key=lambda x: x['rarity'], reverse=True)
        
        return listings
    
    def _get_category_items(self, category: MarketCategory) -> List[str]:
        """
        Get item IDs for a specific market category.
        
        Args:
            category: Market category
            
        Returns:
            List of item IDs in the category
        """
        # In a real implementation, this would be a database query
        # For this prototype, we'll use a simple mapping
        
        category_items = {
            MarketCategory.GENERAL: [item_id for item_id, item in self.items.items() 
                                    if not item.faction_requirement and item.rarity.value <= 3],
            
            MarketCategory.FACTION: [item_id for item_id, item in self.items.items() 
                                    if item.faction_requirement],
            
            MarketCategory.BLACK_MARKET: [item_id for item_id, item in self.items.items() 
                                         if item.rarity.value >= 4],
            
            MarketCategory.LIMITED: [],  # Would be populated with time-limited items
            
            MarketCategory.PLAYER: []  # Would be populated with player-listed items
        }
        
        return category_items.get(category, [])
    
    def get_player_economic_status(self, player_id: str) -> Dict[str, Any]:
        """
        Get comprehensive economic status for a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Dictionary containing player's economic status
        """
        if player_id not in self.inventories:
            return {'error': 'Player not found'}
        
        inventory = self.inventories[player_id]
        
        # Calculate total value
        total_value = inventory.get_total_value(self.items, self.market_conditions)
        
        # Get recent transactions
        recent_transactions = [t for t in self.transactions 
                              if (t.buyer_id == player_id or t.seller_id == player_id)
                              and t.is_completed][-10:]  # Last 10 transactions
        
        # Format transactions for output
        formatted_transactions = []
        for t in recent_transactions:
            transaction_data = {
                'id': t.id,
                'timestamp': t.timestamp,
                'role': 'buyer' if t.buyer_id == player_id else 'seller',
                'item_id': t.item_id,
                'item_quantity': t.item_quantity,
                'currency_type': t.currency_type.value,
                'amount': t.amount,
                'transaction_fee': t.transaction_fee
            }
            
            if t.item_id in self.items:
                transaction_data['item_name'] = self.items[t.item_id].name
            
            formatted_transactions.append(transaction_data)
        
        return {
            'player_id': player_id,
            'currencies': {currency_type.value: amount for currency_type, amount in inventory.currencies.items()},
            'item_count': len(inventory.items),
            'total_value': {currency_type.value: value for currency_type, value in total_value.items()},
            'recent_transactions': formatted_transactions
        }
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the economy to a file.
        
        Args:
            filepath: Path to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to serializable format
            state = {
                'currencies': {currency_type.value: {
                    'name': currency.name,
                    'symbol': currency.symbol,
                    'description': currency.description,
                    'exchange_rate': currency.exchange_rate,
                    'is_tradable': currency.is_tradable,
                    'is_earnable': currency.is_earnable,
                    'daily_limit': currency.daily_limit,
                    'faction': currency.faction
                } for currency_type, currency in self.currencies.items()},
                
                'items': {item_id: {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'type': item.type.value,
                    'rarity': item.rarity.value,
                    'base_value': item.base_value,
                    'currency_type': item.currency_type.value,
                    'is_tradable': item.is_tradable,
                    'is_consumable': item.is_consumable,
                    'durability': item.durability,
                    'cooldown': item.cooldown,
                    'level_requirement': item.level_requirement,
                    'faction_requirement': item.faction_requirement,
                    'attributes': [{
                        'name': attr.name,
                        'value': attr.value,
                        'description': attr.description,
                        'is_hidden': attr.is_hidden
                    } for attr in item.attributes],
                    'tags': item.tags,
                    'creation_timestamp': item.creation_timestamp
                } for item_id, item in self.items.items()},
                
                'inventories': {player_id: {
                    'player_id': inventory.player_id,
                    'items': inventory.items,
                    'currencies': {currency_type.value: amount for currency_type, amount in inventory.currencies.items()},
                    'max_slots': inventory.max_slots
                } for player_id, inventory in self.inventories.items()},
                
                'market_conditions': self.market_conditions,
                
                'transactions': [{
                    'id': t.id,
                    'timestamp': t.timestamp,
                    'seller_id': t.seller_id,
                    'buyer_id': t.buyer_id,
                    'item_id': t.item_id,
                    'item_quantity': t.item_quantity,
                    'currency_type': t.currency_type.value,
                    'amount': t.amount,
                    'transaction_fee': t.transaction_fee,
                    'market_category': t.market_category.value,
                    'is_completed': t.is_completed,
                    'is_refunded': t.is_refunded,
                    'notes': t.notes
                } for t in self.transactions]
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving economy state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the state of the economy from a file.
        
        Args:
            filepath: Path to load the state from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Load currencies
            self.currencies = {}
            for currency_type_str, currency_data in state.get('currencies', {}).items():
                currency_type = CurrencyType(currency_type_str)
                self.currencies[currency_type] = Currency(
                    type=currency_type,
                    name=currency_data['name'],
                    symbol=currency_data['symbol'],
                    description=currency_data['description'],
                    exchange_rate=currency_data['exchange_rate'],
                    is_tradable=currency_data['is_tradable'],
                    is_earnable=currency_data['is_earnable'],
                    daily_limit=currency_data['daily_limit'],
                    faction=currency_data['faction']
                )
            
            # Load items
            self.items = {}
            for item_id, item_data in state.get('items', {}).items():
                attributes = []
                for attr_data in item_data.get('attributes', []):
                    attributes.append(ItemAttribute(
                        name=attr_data['name'],
                        value=attr_data['value'],
                        description=attr_data['description'],
                        is_hidden=attr_data['is_hidden']
                    ))
                
                self.items[item_id] = Item(
                    id=item_data['id'],
                    name=item_data['name'],
                    description=item_data['description'],
                    type=ItemType(item_data['type']),
                    rarity=ItemRarity(item_data['rarity']),
                    base_value=item_data['base_value'],
                    currency_type=CurrencyType(item_data['currency_type']),
                    is_tradable=item_data['is_tradable'],
                    is_consumable=item_data['is_consumable'],
                    durability=item_data['durability'],
                    cooldown=item_data['cooldown'],
                    level_requirement=item_data['level_requirement'],
                    faction_requirement=item_data['faction_requirement'],
                    attributes=attributes,
                    tags=item_data['tags'],
                    creation_timestamp=item_data['creation_timestamp']
                )
            
            # Load inventories
            self.inventories = {}
            for player_id, inventory_data in state.get('inventories', {}).items():
                inventory = Inventory(
                    player_id=inventory_data['player_id'],
                    max_slots=inventory_data['max_slots']
                )
                
                inventory.items = inventory_data['items']
                
                for currency_type_str, amount in inventory_data.get('currencies', {}).items():
                    inventory.currencies[CurrencyType(currency_type_str)] = amount
                
                self.inventories[player_id] = inventory
            
            # Load market conditions
            self.market_conditions = state.get('market_conditions', {})
            
            # Load transactions
            self.transactions = []
            for transaction_data in state.get('transactions', []):
                self.transactions.append(Transaction(
                    id=transaction_data['id'],
                    timestamp=transaction_data['timestamp'],
                    seller_id=transaction_data['seller_id'],
                    buyer_id=transaction_data['buyer_id'],
                    item_id=transaction_data['item_id'],
                    item_quantity=transaction_data['item_quantity'],
                    currency_type=CurrencyType(transaction_data['currency_type']),
                    amount=transaction_data['amount'],
                    transaction_fee=transaction_data['transaction_fee'],
                    market_category=MarketCategory(transaction_data['market_category']),
                    is_completed=transaction_data['is_completed'],
                    is_refunded=transaction_data['is_refunded'],
                    notes=transaction_data['notes']
                ))
            
            return True
        
        except Exception as e:
            print(f"Error loading economy state: {e}")
            return False
