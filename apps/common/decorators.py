from functools import wraps


def auto_generate_code(prefix, suffix:int=10001, code_field:str=''):
    def decorator(save_method):
        @wraps(save_method)
        def wrapper(self, *args, **kwargs):
            if not self.pk:  # Check if the instance is being created
                model = self.__class__
                last_instance = model.objects.order_by('id').last()
                if not code_field:
                    model_field = f'{model.__name__.lower()}_code'
                else:
                    model_field = code_field
                if not last_instance:
                    new_code = f'{prefix}{suffix}'
                else:
                    last_code = getattr(last_instance, model_field)
                    if not last_code:
                        new_code = f'{prefix}{suffix + model.objects.count()}'
                    else:
                        last_code_int = int(last_code.split(prefix)[-1])
                        new_code_int = last_code_int + 1
                        new_code = f'{prefix}{new_code_int}'
                setattr(self, model_field, new_code)
            return save_method(self, *args, **kwargs)
        return wrapper
    return decorator