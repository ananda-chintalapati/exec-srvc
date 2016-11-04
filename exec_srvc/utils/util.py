
def get_component_action(component, action):
    if component.lower() == 'rally':
        if action.lower() == 'full':
            return 'Rally_Complete'