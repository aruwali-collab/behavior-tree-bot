import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    ships_to_send = weakest_planet.num_ships + 1
    
    if strongest_planet.num_ships <= ships_to_send:
        return False
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
    return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_to_send)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if strongest_planet is None or weakest_planet is None:
        return False
    
    ships_to_send = weakest_planet.num_ships + 1
    
    if ships_to_send >= strongest_planet.num_ships:
        return False
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
    return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_to_send)
    
def reinforce_weakest_friendly_planet(state):
    
    
    

    
    if len(state.my_planets()) < 2:
        return False

   
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

   
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)
    

    if strongest_planet.ID == weakest_planet.ID:
        return False
    
    if weakest_planet.num_ships >= strongest_planet.num_ships // 2:
        return False
    
    ships_to_send = strongest_planet.num_ships // 3
    
    if ships_to_send <= 0:
        return False
       
    return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships // 2)  
    

def attack_if_strong(state):
    
    
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)
    
    if strongest_planet is None or weakest_planet is None:
        return False
    
    distance = state.distance(strongest_planet.ID, weakest_planet.ID)
    
    ships_to_send = weakest_planet.num_ships + distance * weakest_planet.growth_rate + 1
    
    if strongest_planet.num_ships <= ships_to_send:
        return False
    
    return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_to_send)


def defend_threatened_planets(state):
    issued_order = False
    
    for target in state.my_planets():
        enemy_incoming = sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == target.ID)
        
        friendly_incoming = sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == target.ID)
        
        projected_strength = (target.num_ships + friendly_incoming - enemy_incoming)
        
        if projected_strength >= 1:
            continue
        
        ships_needed = 1 - projected_strength
        
        donors = sorted(
            [
                planet for planet in state.my_planets()
                if planet.ID != target.ID 
            ],
            key=lambda p: p.num_ships,
            reverse=True
            
        )
        
        for donor in donors:
            available = donor.num_ships - 5
            if available <= 0:
                continue
            
            ships_to_send = min(available, ships_needed)
            if ships_to_send > 0:
                if issue_order(state, donor.ID, target.ID, ships_to_send):
                    issued_order = True
                    ships_needed -= ships_to_send
                
            if ships_needed <= 0:
                break
    return issued_order


def expand_and_attack (state):
    issued_order = False
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)    
    
    already_targeted = {fleet.destination_planet for fleet in state.my_fleets()}
    
    available_targets = [ planet for planet in state.not_my_planets() if planet.ID not in already_targeted]
    
    for source in my_planets:
        best_target = None
        best_required = None
        best_score = None
        
        for target in available_targets:
            distance = state.distance(source.ID, target.ID)
            
            if target.owner == 0:
                required_ships = target.num_ships + 1
            else:
                required_ships = (target.num_ships + distance * target.growth_rate + 1)
            
            if source.num_ships <= required_ships + 5:
                continue
            
            score = (target.growth_rate * 5 - required_ships - distance)
            
            if best_score is None or score > best_score:
                best_score = score
                best_target = target
                best_required = required_ships
            
        if best_target is not None:
            if issue_order(state, source.ID, best_target.ID, best_required):
                issued_order = True
                available_targets.remove(best_target)
                    
    return issued_order