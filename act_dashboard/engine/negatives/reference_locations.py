"""UK postcode regex + major-cities reference set for Pass 1 Rule 4.

A token is "location-shaped" if either:
 - it matches the UK outcode regex (sw4, nw3, ec1, sw1a, etc.), OR
 - it appears (lowercase) in UK_MAJOR_CITIES below.

UK_MAJOR_CITIES is a pragmatic seed — ~200 entries covering:
 - All 32 London boroughs + City of London
 - UK cities with population >~50k
 - Major commuter towns and historically-recognisable places

Not exhaustive. First-week user feedback will add misses. Keep lowercase.
"""
import re

UK_POSTCODE_OUTCODE_RE = re.compile(r"^[a-z]{1,2}\d[a-z\d]?$")


# 32 London boroughs + City of London (all lowercase, matches how they'd appear
# in a search term after normalize()).
_LONDON_BOROUGHS = {
    'barking', 'barnet', 'bexley', 'brent', 'bromley', 'camden',
    'croydon', 'ealing', 'enfield', 'greenwich', 'hackney', 'hammersmith',
    'haringey', 'harrow', 'havering', 'hillingdon', 'hounslow', 'islington',
    'kensington', 'kingston', 'lambeth', 'lewisham', 'merton', 'newham',
    'redbridge', 'richmond', 'southwark', 'sutton', 'tower hamlets',
    'waltham forest', 'wandsworth', 'westminster', 'city of london',
    # Common compound forms that appear in search terms
    'dagenham', 'barking and dagenham', 'hammersmith and fulham', 'fulham',
    'kensington and chelsea', 'chelsea', 'royal borough of kingston',
    'kingston upon thames', 'richmond upon thames',
}

# UK cities >~50k population — major urban centres across England, Scotland,
# Wales, and Northern Ireland.
_UK_CITIES = {
    # England — major conurbations
    'london', 'manchester', 'birmingham', 'leeds', 'liverpool', 'sheffield',
    'bristol', 'newcastle', 'newcastle upon tyne', 'nottingham', 'leicester',
    'coventry', 'bradford', 'stoke', 'stoke-on-trent', 'stoke on trent',
    'wolverhampton', 'sunderland', 'plymouth', 'southampton', 'portsmouth',
    'derby', 'brighton', 'brighton and hove', 'hove', 'hull',
    'kingston upon hull', 'preston', 'oxford', 'cambridge', 'york',
    'norwich', 'swindon', 'northampton', 'milton keynes', 'luton',
    'bournemouth', 'poole', 'reading', 'blackpool', 'blackburn',
    'middlesbrough', 'huddersfield', 'bolton', 'stockport', 'rotherham',
    'doncaster', 'wigan', 'salford', 'oldham', 'warrington', 'chester',
    'gloucester', 'exeter', 'bath', 'lincoln', 'worcester', 'peterborough',
    'cheltenham', 'carlisle', 'chelmsford', 'basildon', 'colchester',
    'ipswich', 'southend', 'southend-on-sea', 'maidstone', 'dartford',
    'canterbury', 'medway', 'rochester', 'gillingham', 'chatham',
    'tunbridge wells', 'eastbourne', 'hastings', 'worthing', 'crawley',
    'basingstoke', 'aldershot', 'farnborough', 'guildford', 'woking',
    'reigate', 'redhill', 'epsom', 'watford', 'st albans', 'hemel hempstead',
    'welwyn garden city', 'stevenage', 'high wycombe', 'slough', 'windsor',
    'maidenhead', 'bracknell', 'wokingham', 'havant', 'fareham', 'gosport',
    'winchester', 'newbury', 'andover', 'salisbury', 'yeovil', 'taunton',
    'weston-super-mare', 'weston super mare', 'torquay', 'paignton',
    'truro', 'penzance', 'falmouth', 'scarborough', 'darlington', 'durham',
    'gateshead', 'hartlepool', 'stockton', 'stockton-on-tees',
    'redcar', 'halifax', 'wakefield', 'harrogate', 'burnley', 'rochdale',
    'bury', 'st helens', 'birkenhead', 'wallasey', 'southport', 'runcorn',
    'widnes', 'crewe', 'macclesfield', 'warwick', 'leamington',
    'leamington spa', 'rugby', 'solihull', 'dudley', 'walsall', 'sandwell',
    'west bromwich', 'telford', 'shrewsbury', 'hereford', 'redditch',
    'bromsgrove', 'kidderminster', 'tamworth', 'burton-on-trent',
    'burton upon trent', 'stafford', 'kings lynn', "king's lynn",
    'great yarmouth', 'lowestoft', 'bury st edmunds',
    # Scotland
    'edinburgh', 'glasgow', 'aberdeen', 'dundee', 'stirling', 'perth',
    'inverness', 'falkirk', 'dunfermline', 'kirkcaldy', 'paisley',
    'east kilbride', 'livingston',
    # Wales
    'cardiff', 'swansea', 'newport', 'wrexham', 'bangor', 'st asaph',
    'st davids', "st david's",
    # Northern Ireland
    'belfast', 'derry', 'londonderry', 'lisburn', 'newtownabbey', 'bangor',
    'craigavon', 'ballymena',
}

UK_MAJOR_CITIES: set[str] = _LONDON_BOROUGHS | _UK_CITIES


def is_location_shaped(token: str) -> bool:
    """True if `token` looks like a UK location (postcode outcode or known city/town)."""
    if not token:
        return False
    t = token.strip().lower()
    if UK_POSTCODE_OUTCODE_RE.match(t):
        return True
    return t in UK_MAJOR_CITIES
