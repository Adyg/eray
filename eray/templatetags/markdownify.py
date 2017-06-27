import mistune

from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError
from django.utils.safestring import mark_safe


register = Library()

class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):

        return '\n<pre class="prettyprint"><code>%s</code></pre>\n' % \
                mistune.escape(code)

@register.filter
def markdownify(content):
    renderer = HighlightRenderer()
    markdown = mistune.Markdown(renderer=renderer)

    return mark_safe(markdown(content))

markdownify.is_safe = True

