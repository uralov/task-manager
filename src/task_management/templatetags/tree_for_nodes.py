from django import template

register = template.Library()


@register.filter
def tree_for_nodes(value):
    nodes = value
    def qwe():
        pass

    return
