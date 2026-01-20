from django.contrib import admin
from.models import UserProfile, UserLoginHistory,Shelter,Pet,PetLogHistory, AdoptionApplication
from .models import PetCareTip
from django.contrib import admin
from django.shortcuts import render
from django.contrib import messages
from django.utils.html import format_html


def assign_shelter_action(modeladmin, request, queryset):
	"""Admin action that shows a form to pick a Shelter and assigns it to selected profiles."""
	if 'apply' in request.POST:
		shelter_id = request.POST.get('shelter')
		if not shelter_id:
			messages.error(request, 'No shelter selected.')
			return None
		try:
			shelter = Shelter.objects.get(pk=int(shelter_id))
		except (Shelter.DoesNotExist, ValueError):
			messages.error(request, 'Selected shelter does not exist.')
			return None

		count = queryset.update(shelter=shelter)
		messages.success(request, f"Assigned shelter '{shelter}' to {count} users.")
		return None

	context = {
		'profiles': queryset,
		'shelters': Shelter.objects.all(),
		'action': 'assign_shelter_action',
		'opts': modeladmin.model._meta,
	}
	return render(request, 'admin/assign_shelter.html', context)


assign_shelter_action.short_description = 'Assign shelter to selected users'


class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'name', 'role', 'shelter')
	list_editable = ('role', 'shelter')
	list_display_links = ('user',)
	actions = [assign_shelter_action]


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserLoginHistory)
 

class ShelterAdmin(admin.ModelAdmin):
	list_display = ('shelter_name', 'city', 'email', 'logo_tag')
	readonly_fields = ('logo_tag',)

	def logo_tag(self, obj):
		if obj.logo:
			return format_html('<img src="{}" style="height:40px;border-radius:4px;"/>', obj.logo.url)
		return '(no logo)'

	logo_tag.short_description = 'Logo'

	def thumb_tag(self, obj):
		if obj.logo_thumb:
			return format_html('<img src="{}" style="height:24px;border-radius:4px;"/>', obj.logo_thumb.url)
		return ''

	thumb_tag.short_description = 'Thumb'

admin.site.register(Shelter, ShelterAdmin)
admin.site.register(Pet)
admin.site.register(PetLogHistory)
admin.site.register(AdoptionApplication)
admin.site.register(PetCareTip)




