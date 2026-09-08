# POST : only name is required to create a countrry, but thats  fine, cause, unlike playersm there can't be duplicate counties
# UPDATE : use the same appraoch to avoid counting the country we are changing, only allowed to change : country
# DELETE : if a country gets deleted, players should be set to NULL but shouldn't the clubs be CASCADED? or set to None?