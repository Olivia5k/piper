REQUIREMENT_SCHEMA = {
    'description': 'A set of requirement definitions',
    'type': ['object', 'null'],
    'addtionalProperties': {
        'required': ['reason', 'class', 'key', 'equals'],
        'properties': {
            'reason': {
                'description':
                    'Human-readable motivation for this requirement.',
                'type': 'string',
            },
            'class': {
                'description': 'Dynamic class to load.',
                'type': 'string',
            },
            'key': {
                'description': 'The key for lookup.',
                'type': 'string',
            },
            'equals': {
                'description': 'The value to compare the lookup with.',
                'type': 'string',
            },
        },
    }
}
