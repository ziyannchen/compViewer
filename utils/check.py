
INT32 = dict(min=-2**31, max=2**32-1)

def checkOverflow(number, type='int32'):
    if type == 'int32':
        if number < INT32['min'] or number > INT32['max']:
            return False
        return True
    else:
        raise NotImplementedError(f'unsupported type {type}')