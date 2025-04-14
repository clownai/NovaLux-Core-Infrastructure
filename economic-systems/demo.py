"""
Demo Script for NovaLux Economic and Social Systems

This script demonstrates the functionality of the integrated economic and social
systems by simulating player interactions, market transactions, and social dynamics.

The demo creates a small virtual economy with players, items, currencies, and factions,
then simulates various interactions to show how the systems work together.
"""

import sys
import os
import time
import random
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from src.integration import EconomicSocialSystem
from src.core.economy import CurrencyType, ItemRarity, ItemType, MarketCategory
from src.social.social import SocialActionType, FactionAlignment


def create_demo_items(system: EconomicSocialSystem, count: int = 20) -> List[str]:
    """Create demo items for the economy."""
    item_ids = []
    
    # Item templates
    item_templates = [
        {
            'name': 'Neural Interface',
            'description': 'Standard neural interface for connecting to the NovaLux network.',
            'type': ItemType.FUNCTIONAL,
            'rarity': ItemRarity.COMMON,
            'base_value': 100.0,
            'tags': ['tech', 'interface']
        },
        {
            'name': 'Quantum Processor',
            'description': 'High-performance quantum processor for advanced computations.',
            'type': ItemType.FUNCTIONAL,
            'rarity': ItemRarity.RARE,
            'base_value': 500.0,
            'tags': ['tech', 'processor']
        },
        {
            'name': 'Holographic Display',
            'description': 'Customizable holographic display for your virtual space.',
            'type': ItemType.COSMETIC,
            'rarity': ItemRarity.UNCOMMON,
            'base_value': 200.0,
            'tags': ['cosmetic', 'display']
        },
        {
            'name': 'Memory Shard',
            'description': 'Fragment of digital memory containing valuable data.',
            'type': ItemType.COLLECTIBLE,
            'rarity': ItemRarity.EPIC,
            'base_value': 1000.0,
            'tags': ['collectible', 'memory']
        },
        {
            'name': 'Energy Cell',
            'description': 'Standard energy cell for powering various devices.',
            'type': ItemType.CONSUMABLE,
            'rarity': ItemRarity.COMMON,
            'base_value': 50.0,
            'tags': ['consumable', 'energy']
        }
    ]
    
    # Faction-specific items
    faction_items = {
        'Architects': {
            'name': 'Architect\'s Blueprint',
            'description': 'Advanced blueprint used by the Architects faction.',
            'type': ItemType.BLUEPRINT,
            'rarity': ItemRarity.RARE,
            'base_value': 800.0,
            'faction_requirement': 'Architects',
            'tags': ['blueprint', 'architects']
        },
        'Guardians': {
            'name': 'Guardian\'s Shield',
            'description': 'Protective shield used by the Guardians faction.',
            'type': ItemType.FUNCTIONAL,
            'rarity': ItemRarity.RARE,
            'base_value': 750.0,
            'faction_requirement': 'Guardians',
            'tags': ['shield', 'guardians']
        },
        'Seekers': {
            'name': 'Seeker\'s Compass',
            'description': 'Navigation tool used by the Seekers faction.',
            'type': ItemType.FUNCTIONAL,
            'rarity': ItemRarity.RARE,
            'base_value': 700.0,
            'faction_requirement': 'Seekers',
            'tags': ['navigation', 'seekers']
        },
        'Shadows': {
            'name': 'Shadow\'s Cloak',
            'description': 'Stealth device used by the Shadows faction.',
            'type': ItemType.FUNCTIONAL,
            'rarity': ItemRarity.RARE,
            'base_value': 850.0,
            'faction_requirement': 'Shadows',
            'tags': ['stealth', 'shadows']
        }
    }
    
    # Create regular items
    for i in range(count):
        # Select a template
        template = random.choice(item_templates)
        
        # Create variations
        item_data = template.copy()
        item_data['name'] = f"{template['name']} {chr(65 + i % 26)}-{i+1}"
        
        # Randomize value slightly
        value_variation = random.uniform(0.8, 1.2)
        item_data['base_value'] = template['base_value'] * value_variation
        
        # Create the item
        item = system.economy.create_item(item_data)
        item_ids.append(item.id)
    
    # Create faction items
    for faction_name, item_template in faction_items.items():
        item = system.economy.create_item(item_template)
        item_ids.append(item.id)
    
    return item_ids


def create_demo_players(system: EconomicSocialSystem, count: int = 10) -> List[str]:
    """Create demo players for the simulation."""
    player_ids = []
    
    for i in range(count):
        player_id = f"player_{i+1}"
        display_name = f"Player {i+1}"
        
        # Create player
        system.create_player(player_id, display_name)
        player_ids.append(player_id)
        
        # Add some items to inventory
        inventory = system.economy.inventories[player_id]
        
        # Add 3-5 random items
        item_count = random.randint(3, 5)
        for _ in range(item_count):
            item_id = random.choice(list(system.economy.items.keys()))
            inventory.add_item(item_id)
    
    return player_ids


def setup_faction_relationships(system: EconomicSocialSystem, player_ids: List[str]) -> None:
    """Set up faction relationships for players."""
    # Get faction IDs
    factions = {}
    for faction_id, faction in system.social.factions.items():
        factions[faction.name] = faction_id
    
    # Assign players to factions
    faction_names = list(factions.keys())
    
    for player_id in player_ids:
        # Choose a primary faction
        primary_faction = random.choice(faction_names)
        faction_id = factions[primary_faction]
        
        # Create faction relationship
        alignment = random.choice([
            FactionAlignment.FRIENDLY,
            FactionAlignment.TRUSTED,
            FactionAlignment.EXALTED
        ])
        
        influence = random.uniform(20.0, 80.0)
        reputation = random.uniform(20.0, 80.0)
        
        relationship = system.social.record_social_action(
            action_type=SocialActionType.FACTION_SUPPORT,
            initiator_id=player_id,
            faction_id=faction_id,
            data={'value': influence}
        )
        
        # Update player's social profile
        profile = system.social.get_social_profile(player_id)
        if profile:
            profile.primary_faction_id = faction_id
        
        # Create relationships with other factions
        for other_faction in faction_names:
            if other_faction != primary_faction:
                other_faction_id = factions[other_faction]
                
                # 50% chance of having a relationship with other factions
                if random.random() < 0.5:
                    # Determine alignment based on faction relationships
                    primary_faction_obj = system.social.get_faction(faction_id)
                    relationship_value = primary_faction_obj.faction_relationships.get(other_faction, 0.0)
                    
                    if relationship_value > 0:
                        alignment = random.choice([
                            FactionAlignment.NEUTRAL,
                            FactionAlignment.FRIENDLY
                        ])
                    else:
                        alignment = random.choice([
                            FactionAlignment.NEUTRAL,
                            FactionAlignment.SUSPICIOUS,
                            FactionAlignment.UNFRIENDLY
                        ])
                    
                    influence = random.uniform(10.0, 40.0)
                    
                    system.social.record_social_action(
                        action_type=SocialActionType.FACTION_SUPPORT if alignment.value > 0 else SocialActionType.FACTION_OPPOSE,
                        initiator_id=player_id,
                        faction_id=other_faction_id,
                        data={'value': influence}
                    )


def setup_social_relationships(system: EconomicSocialSystem, player_ids: List[str]) -> None:
    """Set up social relationships between players."""
    for i in range(len(player_ids)):
        for j in range(i + 1, len(player_ids)):
            player1_id = player_ids[i]
            player2_id = player_ids[j]
            
            # 30% chance of being friends
            if random.random() < 0.3:
                # Player 1 sends friend request
                system.social.record_social_action(
                    action_type=SocialActionType.FRIEND_REQUEST,
                    initiator_id=player1_id,
                    target_id=player2_id
                )
                
                # Player 2 accepts
                system.social.record_social_action(
                    action_type=SocialActionType.FRIEND_ACCEPT,
                    initiator_id=player2_id,
                    target_id=player1_id
                )
                
                # Add some interactions
                interaction_count = random.randint(1, 5)
                for _ in range(interaction_count):
                    # Random interaction type
                    action_type = random.choice([
                        SocialActionType.MESSAGE,
                        SocialActionType.GIFT,
                        SocialActionType.TEAM_INVITE
                    ])
                    
                    # Random direction
                    if random.random() < 0.5:
                        initiator_id, target_id = player1_id, player2_id
                    else:
                        initiator_id, target_id = player2_id, player1_id
                    
                    system.social.record_social_action(
                        action_type=action_type,
                        initiator_id=initiator_id,
                        target_id=target_id,
                        is_public=random.random() < 0.5
                    )


def simulate_market_activity(system: EconomicSocialSystem, player_ids: List[str], days: int = 7) -> None:
    """Simulate market activity over a period of time."""
    print(f"Simulating market activity over {days} days...")
    
    # Simulate each day
    for day in range(1, days + 1):
        print(f"Day {day}:")
        
        # Create some listings
        listing_count = random.randint(3, 8)
        for _ in range(listing_count):
            seller_id = random.choice(player_ids)
            
            # Find an item the seller has
            seller_inventory = system.economy.inventories[seller_id]
            if not seller_inventory.items:
                continue
            
            item_id = random.choice(list(seller_inventory.items.keys()))
            
            # Get item details
            item = system.economy.items.get(item_id)
            if not item:
                continue
            
            # Calculate price
            base_price = item.calculate_value(system.economy.market_conditions)
            price_variation = random.uniform(0.8, 1.5)
            price = base_price * price_variation
            
            # Create listing
            listing_data = {
                'item_id': item_id,
                'quantity': 1,
                'price': price,
                'currency_type': CurrencyType.CREDITS,
                'market_category': MarketCategory.GENERAL,
                'is_featured': random.random() < 0.2
            }
            
            result = system.process_market_transaction('sell', seller_id, listing_data)
            
            if result['success']:
                print(f"  {system.social.get_social_profile(seller_id).display_name} listed {item.name} for {price:.2f} credits")
        
        # Create some auctions
        auction_count = random.randint(1, 3)
        for _ in range(auction_count):
            seller_id = random.choice(player_ids)
            
            # Find an item the seller has
            seller_inventory = system.economy.inventories[seller_id]
            if not seller_inventory.items:
                continue
            
            item_id = random.choice(list(seller_inventory.items.keys()))
            
            # Get item details
            item = system.economy.items.get(item_id)
            if not item:
                continue
            
            # Calculate starting bid
            base_price = item.calculate_value(system.economy.market_conditions)
            price_variation = random.uniform(0.6, 0.9)  # Start lower to attract bids
            starting_bid = base_price * price_variation
            
            # Create auction
            auction_data = {
                'item_id': item_id,
                'quantity': 1,
                'starting_bid': starting_bid,
                'currency_type': CurrencyType.CREDITS,
                'market_category': MarketCategory.GENERAL,
                'is_featured': random.random() < 0.3,
                'duration_days': random.randint(1, 3)
            }
            
            result = system.process_market_transaction('create_auction', seller_id, auction_data)
            
            if result['success']:
                print(f"  {system.social.get_social_profile(seller_id).display_name} started auction for {item.name} at {starting_bid:.2f} credits")
        
        # Process purchases
        for player_id in player_ids:
            # 30% chance of making a purchase
            if random.random() < 0.3:
                # Find active listings
                active_listings = []
                for listing_id, listing in system.market.listings.items():
                    if listing.is_active and listing.seller_id != player_id:
                        active_listings.append(listing_id)
                
                if not active_listings:
                    continue
                
                # Choose a random listing
                listing_id = random.choice(active_listings)
                listing = system.market.listings[listing_id]
                
                # Check if player can afford it
                player_inventory = system.economy.inventories[player_id]
                if CurrencyType.CREDITS not in player_inventory.currencies or player_inventory.currencies[CurrencyType.CREDITS] < listing.price:
                    continue
                
                # Make purchase
                result = system.process_market_transaction('buy', player_id, {'listing_id': listing_id})
                
                if result['success']:
                    item = system.economy.items.get(listing.item_id)
                    if item:
                        print(f"  {system.social.get_social_profile(player_id).display_name} purchased {item.name} for {listing.price:.2f} credits")
        
        # Process bids
        for player_id in player_ids:
            # 20% chance of placing a bid
            if random.random() < 0.2:
                # Find active auctions
                active_auctions = []
                for auction_id, auction in system.market.auctions.items():
                    if auction.is_active and auction.seller_id != player_id and auction.current_bidder_id != player_id:
                        active_auctions.append(auction_id)
                
                if not active_auctions:
                    continue
                
                # Choose a random auction
                auction_id = random.choice(active_auctions)
                auction = system.market.auctions[auction_id]
                
                # Calculate bid amount
                min_bid = auction.current_bid + auction.min_bid_increment
                max_bid = min_bid * random.uniform(1.05, 1.3)
                
                # Check if player can afford it
                player_inventory = system.economy.inventories[player_id]
                if CurrencyType.CREDITS not in player_inventory.currencies or player_inventory.currencies[CurrencyType.CREDITS] < min_bid:
                    continue
                
                # Place bid
                bid_amount = min(max_bid, player_inventory.currencies[CurrencyType.CREDITS] * 0.8)  # Don't spend more than 80% of available credits
                
                result = system.process_market_transaction('bid', player_id, {
                    'auction_id': auction_id,
                    'bid_amount': bid_amount
                })
                
                if result['success']:
                    item = system.economy.items.get(auction.item_id)
                    if item:
                        print(f"  {system.social.get_social_profile(player_id).display_name} bid {bid_amount:.2f} credits on {item.name}")
        
        # Finalize expired auctions
        for auction_id, auction in list(system.market.auctions.items()):
            if auction.is_active and auction.expiration_timestamp < time.time():
                transaction = system.market.finalize_auction(auction_id)
                
                if transaction:
                    item = system.economy.items.get(auction.item_id)
                    if item:
                        seller_name = system.social.get_social_profile(auction.seller_id).display_name
                        buyer_name = system.social.get_social_profile(auction.current_bidder_id).display_name
                        print(f"  Auction completed: {seller_name} sold {item.name} to {buyer_name} for {auction.current_bid:.2f} credits")
        
        # Update systems
        system.update_systems()
        print()


def simulate_social_activity(system: EconomicSocialSystem, player_ids: List[str], days: int = 7) -> None:
    """Simulate social activity over a period of time."""
    print(f"Simulating social activity over {days} days...")
    
    # Simulate each day
    for day in range(1, days + 1):
        print(f"Day {day}:")
        
        # Process social actions
        action_count = random.randint(5, 15)
        for _ in range(action_count):
            # Choose random player
            player_id = random.choice(player_ids)
            
            # Choose action type
            action_type = random.choice([
                SocialActionType.MESSAGE,
                SocialActionType.GIFT,
                SocialActionType.TEAM_INVITE,
                SocialActionType.FACTION_SUPPORT,
                SocialActionType.REPUTATION_BOOST
            ])
            
            # Process based on action type
            if action_type in [SocialActionType.MESSAGE, SocialActionType.GIFT, SocialActionType.TEAM_INVITE]:
                # Need a target player
                other_players = [p for p in player_ids if p != player_id]
                if not other_players:
                    continue
                
                target_id = random.choice(other_players)
                
                # Check if they're friends
                relationship = system.social.get_relationship(player_id, target_id)
                is_friend = relationship and relationship.status.value == "friends"
                
                # For gifts, need to have an item
                if action_type == SocialActionType.GIFT:
                    player_inventory = system.economy.inventories[player_id]
                    if not player_inventory.items:
                        continue
                    
                    item_id = random.choice(list(player_inventory.items.keys()))
                    item = system.economy.items.get(item_id)
                    
                    if not item:
                        continue
                    
                    data = {
                        'item_id': item_id,
                        'item_name': item.name,
                        'quantity': 1,
                        'value': item.calculate_value(system.economy.market_conditions)
                    }
                else:
                    data = {'message': f"Automated message on day {day}"}
                
                result = system.process_social_action(
                    action_type=action_type,
                    initiator_id=player_id,
                    target_id=target_id,
                    data=data,
                    is_public=random.random() < 0.7
                )
                
                initiator_name = system.social.get_social_profile(player_id).display_name
                target_name = system.social.get_social_profile(target_id).display_name
                
                if action_type == SocialActionType.MESSAGE:
                    print(f"  {initiator_name} sent a message to {target_name}")
                elif action_type == SocialActionType.GIFT:
                    print(f"  {initiator_name} gave {item.name} to {target_name}")
                elif action_type == SocialActionType.TEAM_INVITE:
                    print(f"  {initiator_name} invited {target_name} to join a team")
            
            elif action_type == SocialActionType.FACTION_SUPPORT:
                # Choose a faction
                faction_ids = list(system.social.factions.keys())
                if not faction_ids:
                    continue
                
                faction_id = random.choice(faction_ids)
                faction = system.social.get_faction(faction_id)
                
                if not faction:
                    continue
                
                # Support the faction
                value = random.uniform(10.0, 50.0)
                
                result = system.process_social_action(
                    action_type=action_type,
                    initiator_id=player_id,
                    faction_id=faction_id,
                    data={'value': value},
                    is_public=True
                )
                
                initiator_name = system.social.get_social_profile(player_id).display_name
                print(f"  {initiator_name} supported the {faction.name} faction")
            
            elif action_type == SocialActionType.REPUTATION_BOOST:
                # Choose a target player
                other_players = [p for p in player_ids if p != player_id]
                if not other_players:
                    continue
                
                target_id = random.choice(other_players)
                
                # Boost reputation
                result = system.process_social_action(
                    action_type=action_type,
                    initiator_id=player_id,
                    target_id=target_id,
                    is_public=True
                )
                
                initiator_name = system.social.get_social_profile(player_id).display_name
                target_name = system.social.get_social_profile(target_id).display_name
                print(f"  {initiator_name} boosted {target_name}'s reputation")
        
        # Update systems
        system.update_systems()
        print()


def print_system_status(system: EconomicSocialSystem, player_ids: List[str]) -> None:
    """Print the current status of the economic and social systems."""
    print("\n=== SYSTEM STATUS ===\n")
    
    # Print economy stats
    print("Economy Status:")
    print(f"  Items: {len(system.economy.items)}")
    print(f"  Players: {len(system.economy.inventories)}")
    print(f"  Transactions: {len(system.economy.transactions)}")
    print(f"  Market Conditions:")
    for key, value in system.economy.market_conditions.items():
        if isinstance(value, dict):
            print(f"    {key}:")
            for subkey, subvalue in value.items():
                print(f"      {subkey}: {subvalue:.2f}")
        else:
            print(f"    {key}: {value:.2f}")
    print()
    
    # Print market stats
    print("Market Status:")
    print(f"  Active Listings: {sum(1 for l in system.market.listings.values() if l.is_active)}")
    print(f"  Active Auctions: {sum(1 for a in system.market.auctions.values() if a.is_active)}")
    print()
    
    # Print faction stats
    print("Faction Status:")
    for faction_id, faction in system.social.factions.items():
        print(f"  {faction.name}:")
        print(f"    Power Level: {faction.power_level:.2f}")
        print(f"    Member Count: {faction.member_count}")
        print(f"    Territory Control: {sum(faction.territory_control.values()):.2f}")
        print(f"    Resources: {sum(faction.resources.values()):.2f}")
        print()
    
    # Print player stats for a sample player
    if player_ids:
        sample_player_id = player_ids[0]
        print(f"Sample Player ({sample_player_id}) Status:")
        
        # Get dashboard
        dashboard = system.get_player_dashboard(sample_player_id)
        
        print(f"  Display Name: {dashboard['social']['display_name']}")
        print(f"  Reputation: {dashboard['social']['reputation_score']:.2f}")
        print(f"  Influence: {dashboard['social']['influence_score']:.2f}")
        print(f"  Friend Count: {dashboard['social']['friend_count']}")
        
        print("  Currencies:")
        for currency_type, amount in dashboard['economic']['currencies'].items():
            print(f"    {currency_type}: {amount:.2f}")
        
        print("  Faction Affiliations:")
        for faction in dashboard['factions']:
            print(f"    {faction['name']} - {faction['alignment_name']} ({faction['influence']:.2f} influence)")
        
        print("  Recent Social Feed:")
        for item in dashboard['social_feed'][:3]:
            print(f"    {item['message']}")
        
        print()


def run_demo() -> None:
    """Run the demo simulation."""
    print("=== NovaLux Economic and Social Systems Demo ===\n")
    
    # Create system
    system = EconomicSocialSystem()
    print("System initialized.\n")
    
    # Create items
    print("Creating demo items...")
    item_ids = create_demo_items(system)
    print(f"Created {len(item_ids)} items.\n")
    
    # Create players
    print("Creating demo players...")
    player_ids = create_demo_players(system)
    print(f"Created {len(player_ids)} players.\n")
    
    # Setup faction relationships
    print("Setting up faction relationships...")
    setup_faction_relationships(system, player_ids)
    print("Faction relationships established.\n")
    
    # Setup social relationships
    print("Setting up social relationships...")
    setup_social_relationships(system, player_ids)
    print("Social relationships established.\n")
    
    # Simulate market activity
    simulate_market_activity(system, player_ids, days=3)
    
    # Simulate social activity
    simulate_social_activity(system, player_ids, days=3)
    
    # Print final status
    print_system_status(system, player_ids)
    
    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
