from django.forms.widgets import Input
from django.template import loader
from django.utils.safestring import mark_safe

# 自定义widgets在手机号后加上发送验证码和相应js代码


class EmojiInput(Input):
    input_type = 'text'
    template_name = "widgets/moji.html"

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)

