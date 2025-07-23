def format_db_input(func):
    def wrapper( *args, **kwargs):
        for i, input_data in enumerate(args):
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    if isinstance(value, bool):
                        args[i][key] = int(value)
        return func(*args, **kwargs)
    return wrapper
