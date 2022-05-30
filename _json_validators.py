import abc


class JsonValidator(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def meet_condition(cls, json_data):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def validate(cls, json_data):
        raise NotImplementedError


class JsonValidatorOs(JsonValidator):
    @classmethod
    def meet_condition(cls, json_data):
        return json_data.get('command_type') == 'os'

    @classmethod
    def validate(cls, json_data):
        if not json_data.get('command_name'):
            raise ValueError('Command name is empty')
        return True


class JsonValidatorCompute(JsonValidator):
    @classmethod
    def meet_condition(cls, json_data):
        return json_data.get('command_type') == 'compute'

    @classmethod
    def validate(cls, json_data):
        if not json_data.get('expression'):
            raise ValueError('Expression is empty')
        return True