from django.contrib import admin
from .models import Image, Game, DeepModel, Dataset
import os
from django.contrib import messages

# Register your models

admin.site.register(Image)
admin.site.register(Game)


class DatasetAdmin(admin.ModelAdmin):
    model = Dataset
    fields = ['dataset', 'name', 'description']
    list_display = ['name', 'description', 'performance', 'valid']


class DeepModelAdmin(admin.ModelAdmin):
    model = DeepModel
    fields = ['upload', 'name', 'dataset', 'result']
    list_display = ['name', 'dataset', 'result', 'current']
    actions = ['set_as_current', 'remove_as_current']

    @admin.action(description="Make selected model the current one")
    def set_as_current(self, request, queryset):
        # checking that only one queryset have been selected
        if queryset.count() != 1:
            self.message_user(request, "You cannot have more than one current model running", level=messages.ERROR)
            return
        deepmodel = DeepModel.objects.filter(current=True)
        if deepmodel.exists():
            # get current deep model if it exists
            current_deepmodel = DeepModel.objects.get(current=True)
            # update current deep model and save
            current_deepmodel.current = False
            current_deepmodel.save()
        # update the selected queryset
        queryset.update(current=True)
        self.message_user(request, "Model successfully changed", level=messages.SUCCESS)

    @admin.action(description="Remove as current")
    def remove_as_current(self, request, queryset):
        # checking that only one queryset have been selected
        if queryset.count() != 1:
            self.message_user(request, "You cannot select more than one model", level=messages.ERROR)
            return
        queryset.update(current=False)
        self.message_user(request, "Model successfully changed to not current ", level=messages.SUCCESS)

    @admin.action(description="Delete selected deep models")
    def delete_queryset(self, request, queryset):
        # checking that only one queryset have been selected
        if queryset.count() > 1:
            self.message_user(request, "You cannot delete more than one model at a time", level=messages.ERROR)
            return
        # if model's current value is True, then make delete impossible.
        for q in queryset:
            if q.current:
                self.message_user(request, "You cannot delete a model that is currently marked as active.",
                                  level=messages.ERROR)
                return
            # if model's current value is False, then delete and also delete the corresponding dataset
            else:
                deep_model = DeepModel.objects.get(name=q.name)
                DeepModel.delete(deep_model)
                path = "./media/uploaded_models/"

                # make sure correct file is removed from directory
                filename = str(q.upload)[::-1]
                name = ''
                for char in filename:
                    if char == '/':
                        break
                    else:
                        name += char
                name = name[::-1]
                filepath = path + name
                os.remove(filepath)
                self.message_user(request, "Model " + name + "successfully deleted", level=messages.SUCCESS)
                return


admin.site.register(DeepModel, DeepModelAdmin)
admin.site.register(Dataset, DatasetAdmin)

# %%
