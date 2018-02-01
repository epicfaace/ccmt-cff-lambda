
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

FORMS_PREFIX = "forms::"

class User:
    def __init__(self, permissions):
        self.permissions = permissions
    def resource_exists(self, prefix, id):
        key = prefix + id
        if key in self.permissions:
            return key
        else:
            return False
    def get_form_list_keys(self):
        keys = []
        for key in self.permissions:
            if key.startswith(FORMS_PREFIX):
                keys.append({"id": remove_prefix(key, FORMS_PREFIX), "version": 1})
        return keys
    def can_view_responses(self, formId):
        resourceId = self.resource_exists(FORMS_PREFIX, formId)
        if resourceId and "ViewResponses" in self.permissions[resourceId]:
            return True
        else:
            raise Exception("User does not have access to view this form.")