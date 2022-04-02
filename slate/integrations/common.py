import uuid


def b_id() -> str:
    return str(uuid.uuid4())


DUMMY_INDICATORS = {'dummy': {'values': [{'time': 0, 'value': 0}],
                              'display_name': 'dummy',
                              'type': 'dummy'}}

DUMMY_METRICS = {'dummy': {'value': 0,
                           'display_name': 'dummy',
                           'type': 'dummy'}}
