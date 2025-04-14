"""
Currency System for NovaLux Phase 2

This module defines the currency system components, including:
- Currency types and properties
- Currency exchange mechanisms
- Currency earning and spending mechanisms
- Currency balancing and inflation control
- Currency analytics and reporting

The currency system integrates with the core economy system to provide
a comprehensive framework for managing different types of currencies
in the NovaLux virtual economy.
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
    CurrencyType, Currency, EconomySystem
)


class CurrencyAction(Enum):
    """Types of currency actions in the NovaLux economy."""
    EARN = "earn"
    SPEND = "spend"
    CONVERT = "convert"
    GIFT = "gift"
    REWARD = "reward"
    REFUND = "refund"


@dataclass
class CurrencyTransaction:
    """Represents a currency transaction in the NovaLux economy."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str = ""
    currency_type: CurrencyType = CurrencyType.CREDITS
    amount: float = 0.0
    action: CurrencyAction = CurrencyAction.EARN
    source: str = ""  # e.g., "game_win", "daily_bonus", "purchase"
    timestamp: int = field(default_factory=lambda: int(time.time()))
    related_player_id: Optional[str] = None  # For gifts, trades, etc.
    notes: str = ""


class CurrencySystem:
    """
    Currency system for the NovaLux virtual economy.
    
    This class manages currency transactions, exchange rates, earning rates,
    and currency balancing mechanisms.
    """
    
    def __init__(self, economy_system: EconomySystem):
        """
        Initialize the currency system.
        
        Args:
            economy_system: Reference to the core economy system
        """
        self.economy = economy_system
        self.currency_transactions: List[CurrencyTransaction] = []
        
        # Currency earning rates (per action)
        self.earning_rates = {
            'game_win': {
                CurrencyType.CREDITS: 50.0,
                CurrencyType.QUANTUM_BITS: 0.5
            },
            'daily_login': {
                CurrencyType.CREDITS: 100.0,
                CurrencyType.QUANTUM_BITS: 1.0
            },
            'quest_completion': {
                CurrencyType.CREDITS: 200.0,
                CurrencyType.FACTION_INFLUENCE: 10.0
            },
            'social_interaction': {
                CurrencyType.REPUTATION: 5.0
            },
            'tournament_win': {
                CurrencyType.CREDITS: 500.0,
                CurrencyType.QUANTUM_BITS: 5.0,
                CurrencyType.REPUTATION: 20.0
            }
        }
        
        # Daily limits for currency earning
        self.daily_limits = {
            CurrencyType.CREDITS: 5000.0,
            CurrencyType.QUANTUM_BITS: 10.0,
            CurrencyType.FACTION_INFLUENCE: 100.0,
            CurrencyType.REPUTATION: 50.0
        }
        
        # Currency conversion fees
        self.conversion_fees = {
            CurrencyType.CREDITS: 0.05,  # 5% fee
            CurrencyType.QUANTUM_BITS: 0.10,  # 10% fee
            CurrencyType.FACTION_INFLUENCE: 0.15,  # 15% fee
            CurrencyType.REPUTATION: 0.20   # 20% fee
        }
        
        # Player daily earnings tracking
        self.player_daily_earnings = {}  # player_id -> {currency_type -> amount}
        
        # Last reset timestamp for daily limits
        self.last_daily_reset = int(time.time())
    
    def earn_currency(self, player_id: str, currency_type: CurrencyType, 
                     amount: float, source: str, notes: str = "") -> Optional[CurrencyTransaction]:
        """
        Award currency to a player.
        
        Args:
            player_id: ID of the player
            currency_type: Type of currency to award
            amount: Amount to award
            source: Source of the currency (e.g., "game_win")
            notes: Additional notes
            
        Returns:
            CurrencyTransaction object or None if the transaction failed
        """
        if player_id not in self.economy.inventories:
            return None
        
        # Check if currency exists
        if currency_type not in self.economy.currencies:
            return None
        
        # Check if currency is earnable
        currency = self.economy.currencies[currency_type]
        if not currency.is_earnable:
            return None
        
        # Check daily limit
        if not self._check_daily_limit(player_id, currency_type, amount):
            return None
        
        # Add currency to player's inventory
        inventory = self.economy.inventories[player_id]
        inventory.add_currency(currency_type, amount)
        
        # Create transaction record
        transaction = CurrencyTransaction(
            player_id=player_id,
            currency_type=currency_type,
            amount=amount,
            action=CurrencyAction.EARN,
            source=source,
            notes=notes
        )
        
        # Add to transaction history
        self.currency_transactions.append(transaction)
        
        # Update daily earnings
        self._update_daily_earnings(player_id, currency_type, amount)
        
        return transaction
    
    def spend_currency(self, player_id: str, currency_type: CurrencyType,
                      amount: float, source: str, notes: str = "") -> Optional[CurrencyTransaction]:
        """
        Deduct currency from a player.
        
        Args:
            player_id: ID of the player
            currency_type: Type of currency to deduct
            amount: Amount to deduct
            source: Source of the deduction (e.g., "item_purchase")
            notes: Additional notes
            
        Returns:
            CurrencyTransaction object or None if the transaction failed
        """
        if player_id not in self.economy.inventories:
            return None
        
        # Check if player has enough currency
        inventory = self.economy.inventories[player_id]
        if not inventory.remove_currency(currency_type, amount):
            return None
        
        # Create transaction record
        transaction = CurrencyTransaction(
            player_id=player_id,
            currency_type=currency_type,
            amount=amount,
            action=CurrencyAction.SPEND,
            source=source,
            notes=notes
        )
        
        # Add to transaction history
        self.currency_transactions.append(transaction)
        
        return transaction
    
    def convert_currency(self, player_id: str, from_currency: CurrencyType,
                        to_currency: CurrencyType, amount: float) -> Optional[Tuple[CurrencyTransaction, CurrencyTransaction]]:
        """
        Convert currency from one type to another.
        
        Args:
            player_id: ID of the player
            from_currency: Currency type to convert from
            to_currency: Currency type to convert to
            amount: Amount to convert
            
        Returns:
            Tuple of (spend_transaction, earn_transaction) or None if conversion failed
        """
        if player_id not in self.economy.inventories:
            return None
        
        # Check if currencies exist
        if from_currency not in self.economy.currencies or to_currency not in self.economy.currencies:
            return None
        
        # Check if currencies are tradable
        from_currency_obj = self.economy.currencies[from_currency]
        to_currency_obj = self.economy.currencies[to_currency]
        
        if not from_currency_obj.is_tradable or not to_currency_obj.is_tradable:
            return None
        
        # Calculate conversion rate
        from_rate = from_currency_obj.exchange_rate
        to_rate = to_currency_obj.exchange_rate
        
        conversion_rate = from_rate / to_rate
        
        # Apply conversion fee
        fee_rate = self.conversion_fees.get(from_currency, 0.05)
        fee_amount = amount * fee_rate
        
        # Calculate converted amount
        converted_amount = (amount - fee_amount) * conversion_rate
        
        # Spend source currency
        spend_transaction = self.spend_currency(
            player_id=player_id,
            currency_type=from_currency,
            amount=amount,
            source="currency_conversion",
            notes=f"Converted to {to_currency.value}"
        )
        
        if not spend_transaction:
            return None
        
        # Earn target currency
        earn_transaction = self.earn_currency(
            player_id=player_id,
            currency_type=to_currency,
            amount=converted_amount,
            source="currency_conversion",
            notes=f"Converted from {from_currency.value}"
        )
        
        if not earn_transaction:
            # Refund source currency if target currency couldn't be added
            inventory = self.economy.inventories[player_id]
            inventory.add_currency(from_currency, amount)
            return None
        
        return (spend_transaction, earn_transaction)
    
    def gift_currency(self, sender_id: str, receiver_id: str, currency_type: CurrencyType,
                     amount: float, notes: str = "") -> Optional[Tuple[CurrencyTransaction, CurrencyTransaction]]:
        """
        Gift currency from one player to another.
        
        Args:
            sender_id: ID of the sender
            receiver_id: ID of the receiver
            currency_type: Type of currency to gift
            amount: Amount to gift
            notes: Additional notes
            
        Returns:
            Tuple of (spend_transaction, earn_transaction) or None if gifting failed
        """
        if sender_id not in self.economy.inventories or receiver_id not in self.economy.inventories:
            return None
        
        # Check if currency exists and is tradable
        if currency_type not in self.economy.currencies:
            return None
        
        currency = self.economy.currencies[currency_type]
        if not currency.is_tradable:
            return None
        
        # Spend currency from sender
        spend_transaction = self.spend_currency(
            player_id=sender_id,
            currency_type=currency_type,
            amount=amount,
            source="gift",
            notes=f"Gift to {receiver_id}: {notes}"
        )
        
        if not spend_transaction:
            return None
        
        # Add currency to receiver
        earn_transaction = self.earn_currency(
            player_id=receiver_id,
            currency_type=currency_type,
            amount=amount,
            source="gift",
            notes=f"Gift from {sender_id}: {notes}"
        )
        
        if not earn_transaction:
            # Refund sender if receiver couldn't receive the gift
            inventory = self.economy.inventories[sender_id]
            inventory.add_currency(currency_type, amount)
            return None
        
        # Update related player IDs
        spend_transaction.related_player_id = receiver_id
        earn_transaction.related_player_id = sender_id
        
        return (spend_transaction, earn_transaction)
    
    def get_player_currency_history(self, player_id: str, 
                                   currency_type: Optional[CurrencyType] = None,
                                   action: Optional[CurrencyAction] = None,
                                   start_time: Optional[int] = None,
                                   end_time: Optional[int] = None,
                                   limit: int = 100) -> List[CurrencyTransaction]:
        """
        Get currency transaction history for a player.
        
        Args:
            player_id: ID of the player
            currency_type: Filter by currency type (optional)
            action: Filter by action type (optional)
            start_time: Filter by start time (optional)
            end_time: Filter by end time (optional)
            limit: Maximum number of transactions to return
            
        Returns:
            List of CurrencyTransaction objects
        """
        # Filter transactions
        filtered_transactions = []
        
        for transaction in self.currency_transactions:
            if transaction.player_id != player_id and transaction.related_player_id != player_id:
                continue
            
            if currency_type and transaction.currency_type != currency_type:
                continue
            
            if action and transaction.action != action:
                continue
            
            if start_time and transaction.timestamp < start_time:
                continue
            
            if end_time and transaction.timestamp > end_time:
                continue
            
            filtered_transactions.append(transaction)
        
        # Sort by timestamp (newest first)
        filtered_transactions.sort(key=lambda t: t.timestamp, reverse=True)
        
        # Apply limit
        return filtered_transactions[:limit]
    
    def get_currency_analytics(self, currency_type: Optional[CurrencyType] = None) -> Dict[str, Any]:
        """
        Get analytics data for currency usage.
        
        Args:
            currency_type: Filter by currency type (optional)
            
        Returns:
            Dictionary containing currency analytics
        """
        # Filter transactions by currency type
        if currency_type:
            transactions = [t for t in self.currency_transactions if t.currency_type == currency_type]
        else:
            transactions = self.currency_transactions
        
        # Calculate total earned and spent
        total_earned = {}
        total_spent = {}
        
        for transaction in transactions:
            currency = transaction.currency_type
            
            if transaction.action == CurrencyAction.EARN or transaction.action == CurrencyAction.REWARD:
                if currency in total_earned:
                    total_earned[currency] += transaction.amount
                else:
                    total_earned[currency] = transaction.amount
            
            elif transaction.action == CurrencyAction.SPEND:
                if currency in total_spent:
                    total_spent[currency] += transaction.amount
                else:
                    total_spent[currency] = transaction.amount
        
        # Calculate net flow (earned - spent)
        net_flow = {}
        for currency in set(list(total_earned.keys()) + list(total_spent.keys())):
            earned = total_earned.get(currency, 0.0)
            spent = total_spent.get(currency, 0.0)
            net_flow[currency] = earned - spent
        
        # Calculate earning sources
        earning_sources = {}
        for transaction in transactions:
            if transaction.action != CurrencyAction.EARN and transaction.action != CurrencyAction.REWARD:
                continue
            
            currency = transaction.currency_type
            source = transaction.source
            
            if currency not in earning_sources:
                earning_sources[currency] = {}
            
            if source in earning_sources[currency]:
                earning_sources[currency][source] += transaction.amount
            else:
                earning_sources[currency][source] = transaction.amount
        
        # Calculate spending sources
        spending_sources = {}
        for transaction in transactions:
            if transaction.action != CurrencyAction.SPEND:
                continue
            
            currency = transaction.currency_type
            source = transaction.source
            
            if currency not in spending_sources:
                spending_sources[currency] = {}
            
            if source in spending_sources[currency]:
                spending_sources[currency][source] += transaction.amount
            else:
                spending_sources[currency][source] = transaction.amount
        
        # Format results
        results = {
            'total_transactions': len(transactions),
            'total_earned': {currency.value: amount for currency, amount in total_earned.items()},
            'total_spent': {currency.value: amount for currency, amount in total_spent.items()},
            'net_flow': {currency.value: amount for currency, amount in net_flow.items()},
            'earning_sources': {currency.value: sources for currency, sources in earning_sources.items()},
            'spending_sources': {currency.value: sources for currency, sources in spending_sources.items()}
        }
        
        return results
    
    def _check_daily_limit(self, player_id: str, currency_type: CurrencyType, amount: float) -> bool:
        """
        Check if a currency earning would exceed the daily limit.
        
        Args:
            player_id: ID of the player
            currency_type: Type of currency
            amount: Amount to earn
            
        Returns:
            True if within limit, False if exceeding limit
        """
        # Reset daily earnings if needed
        self._reset_daily_earnings_if_needed()
        
        # Check if currency has a daily limit
        currency = self.economy.currencies[currency_type]
        if currency.daily_limit is None:
            return True
        
        # Check player's daily earnings
        if player_id not in self.player_daily_earnings:
            self.player_daily_earnings[player_id] = {}
        
        if currency_type not in self.player_daily_earnings[player_id]:
            self.player_daily_earnings[player_id][currency_type] = 0.0
        
        current_earnings = self.player_daily_earnings[player_id][currency_type]
        
        # Check if adding the amount would exceed the limit
        if current_earnings + amount > currency.daily_limit:
            return False
        
        return True
    
    def _update_daily_earnings(self, player_id: str, currency_type: CurrencyType, amount: float) -> None:
        """
        Update a player's daily earnings for a currency.
        
        Args:
            player_id: ID of the player
            currency_type: Type of currency
            amount: Amount earned
        """
        if player_id not in self.player_daily_earnings:
            self.player_daily_earnings[player_id] = {}
        
        if currency_type not in self.player_daily_earnings[player_id]:
            self.player_daily_earnings[player_id][currency_type] = 0.0
        
        self.player_daily_earnings[player_id][currency_type] += amount
    
    def _reset_daily_earnings_if_needed(self) -> None:
        """Reset daily earnings if a day has passed since the last reset."""
        current_time = int(time.time())
        seconds_in_day = 24 * 60 * 60
        
        if current_time - self.last_daily_reset >= seconds_in_day:
            self.player_daily_earnings = {}
            self.last_daily_reset = current_time
    
    def update_currency_system(self) -> None:
        """
        Update the currency system.
        
        This method should be called periodically to reset daily limits,
        adjust exchange rates, and apply other currency balancing mechanisms.
        """
        # Reset daily earnings if needed
        self._reset_daily_earnings_if_needed()
        
        # Adjust exchange rates based on economy state
        self._adjust_exchange_rates()
    
    def _adjust_exchange_rates(self) -> None:
        """Adjust currency exchange rates based on economy state."""
        # This would be a more sophisticated algorithm in a real implementation
        # For this prototype, we'll use a simple approach
        
        # Calculate total currency in circulation
        total_circulation = {}
        
        for inventory in self.economy.inventories.values():
            for currency_type, amount in inventory.currencies.items():
                if currency_type in total_circulation:
                    total_circulation[currency_type] += amount
                else:
                    total_circulation[currency_type] = amount
        
        # Adjust exchange rates based on circulation
        for currency_type, currency in self.economy.currencies.items():
            if currency_type == CurrencyType.CREDITS:
                # Credits are the base currency, exchange rate stays at 1.0
                continue
            
            if currency_type not in total_circulation:
                continue
            
            circulation = total_circulation[currency_type]
            
            # Calculate target circulation based on number of players
            num_players = len(self.economy.inventories)
            target_circulation = num_players * currency.daily_limit * 7 if currency.daily_limit else num_players * 100
            
            if target_circulation == 0:
                continue
            
            # Calculate circulation ratio
            circulation_ratio = circulation / target_circulation
            
            # Adjust exchange rate
            # If circulation is high, increase exchange rate (currency is worth less)
            # If circulation is low, decrease exchange rate (currency is worth more)
            adjustment_factor = math.sqrt(circulation_ratio)
            
            # Apply adjustment with dampening
            current_rate = currency.exchange_rate
            new_rate = current_rate * (0.95 + 0.1 * adjustment_factor)
            
            # Cap at reasonable limits
            min_rate = 10.0 if currency_type == CurrencyType.QUANTUM_BITS else 5.0
            max_rate = 200.0 if currency_type == CurrencyType.QUANTUM_BITS else 100.0
            
            currency.exchange_rate = max(min_rate, min(max_rate, new_rate))
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the currency system to a file.
        
        Args:
            filepath: Path to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to serializable format
            state = {
                'currency_transactions': [{
                    'id': t.id,
                    'player_id': t.player_id,
                    'currency_type': t.currency_type.value,
                    'amount': t.amount,
                    'action': t.action.value,
                    'source': t.source,
                    'timestamp': t.timestamp,
                    'related_player_id': t.related_player_id,
                    'notes': t.notes
                } for t in self.currency_transactions],
                
                'earning_rates': {
                    source: {currency_type.value: amount for currency_type, amount in rates.items()}
                    for source, rates in self.earning_rates.items()
                },
                
                'daily_limits': {
                    currency_type.value: amount for currency_type, amount in self.daily_limits.items()
                },
                
                'conversion_fees': {
                    currency_type.value: fee for currency_type, fee in self.conversion_fees.items()
                },
                
                'player_daily_earnings': {
                    player_id: {currency_type.value: amount for currency_type, amount in earnings.items()}
                    for player_id, earnings in self.player_daily_earnings.items()
                },
                
                'last_daily_reset': self.last_daily_reset
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving currency state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the state of the currency system from a file.
        
        Args:
            filepath: Path to load the state from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Load currency transactions
            self.currency_transactions = []
            for transaction_data in state.get('currency_transactions', []):
                self.currency_transactions.append(CurrencyTransaction(
                    id=transaction_data['id'],
                    player_id=transaction_data['player_id'],
                    currency_type=CurrencyType(transaction_data['currency_type']),
                    amount=transaction_data['amount'],
                    action=CurrencyAction(transaction_data['action']),
                    source=transaction_data['source'],
                    timestamp=transaction_data['timestamp'],
                    related_player_id=transaction_data['related_player_id'],
                    notes=transaction_data['notes']
                ))
            
            # Load earning rates
            self.earning_rates = {}
            for source, rates in state.get('earning_rates', {}).items():
                self.earning_rates[source] = {CurrencyType(currency_type): amount for currency_type, amount in rates.items()}
            
            # Load daily limits
            self.daily_limits = {}
            for currency_type, amount in state.get('daily_limits', {}).items():
                self.daily_limits[CurrencyType(currency_type)] = amount
            
            # Load conversion fees
            self.conversion_fees = {}
            for currency_type, fee in state.get('conversion_fees', {}).items():
                self.conversion_fees[CurrencyType(currency_type)] = fee
            
            # Load player daily earnings
            self.player_daily_earnings = {}
            for player_id, earnings in state.get('player_daily_earnings', {}).items():
                self.player_daily_earnings[player_id] = {CurrencyType(currency_type): amount for currency_type, amount in earnings.items()}
            
            # Load last daily reset
            self.last_daily_reset = state.get('last_daily_reset', int(time.time()))
            
            return True
        
        except Exception as e:
            print(f"Error loading currency state: {e}")
            return False
