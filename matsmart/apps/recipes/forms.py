from django.forms import Form, ModelForm, formset_factory, modelformset_factory
from django.forms import CharField, TextInput, Textarea, ModelChoiceField
from .models import Recipe, Ingredient, Comment
from apps.search.models import Category

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "image", "description", "method"]
        labels = {
            'name': "Tittel",
            'image': "Bilde",
            'description': "Beskrivelse",
            'method': "Fremgangsmåte"
        }
        widgets = {
            'name': TextInput(attrs={'cols':50, 'rows':1}),
            'description': Textarea(attrs={'cols':50, 'rows':4}),
            'method': Textarea(attrs={'cols':50, 'rows':4}),
        }

class IngredientForm(ModelForm):
    amount = CharField(required=False, label="Mengde")

    class Meta:
        model = Ingredient
        fields = ["name"]
        labels = { 'name': "Ingrediens" }
        widgets = {
            'name': TextInput(attrs={'cols':30, 'rows':1}),
            'amount': TextInput(attrs={'cols':20, 'rows':1}),
        }

IngredientFormSet = modelformset_factory(
    Ingredient,                 # use Ingredient model
    form=IngredientForm,        # use IngredientForm
    extra=0,                    # number of fields on top of the queryset,
    min_num=1,                  # require minimum 1 ingredient
    validate_min=True,          # prevent validation if 0 ingredients
    can_delete=True,
)

class CategoryForm(Form):
    name = ModelChoiceField(queryset = Category.objects.all(), required = False, label="Kategori")

CategoryFormSet = formset_factory(
            form=CategoryForm,        # use CategoryForm
            extra=2,                  # number of fields on top of the queryset
)

class NewCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        labels = { 'content': "" }
        widgets = {"content": Textarea(attrs={"class": "form-control w-full dark:bg-black"}),}
