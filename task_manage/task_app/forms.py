from django import forms
from django.contrib.auth.models import User
from .models import Task, UserProfile, TaskChat

class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.
    """
    class Meta:
        model = Task
        fields = [
            'assigned_to', 'deadline', 'ticket_type', 'priority',
            'department', 'subject', 'request_details', 'attach_file', 'status',
            'is_recurring', 'recurrence_type', 'recurrence_count', 'recurrence_duration'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        if user:
            user_profile = UserProfile.objects.get(user=user)

            if user_profile.category == 'Departmental Manager':
                self.fields['assigned_to'].queryset = User.objects.all()
            elif user_profile.category == 'Executive Management':
                self.fields['assigned_to'].queryset = User.objects.all()
            else:
                self.fields['assigned_to'].queryset = User.objects.all()

        if not self.fields['assigned_to'].queryset.exists():
            self.fields['assigned_to'].queryset = User.objects.none()

        # Conditionally show recurrence fields based on 'is_recurring'
        if not self.instance.is_recurring:
            # Hide recurrence fields if task is not recurring
            self.fields['recurrence_type'].widget.attrs['style'] = 'display: none;'
            self.fields['recurrence_count'].widget.attrs['style'] = 'display: none;'
            self.fields['recurrence_duration'].widget.attrs['style'] = 'display: none;'
        else:
            # Show recurrence fields if task is recurring
            self.fields['recurrence_type'].widget.attrs['style'] = 'display: block;'
            self.fields['recurrence_count'].widget.attrs['style'] = 'display: block;'
            self.fields['recurrence_duration'].widget.attrs['style'] = 'display: block;'


class TaskStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['comments_by_assignee', 'revised_completion_date']
        widgets = {
            'revised_completion_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskStatusUpdateForm, self).__init__(*args, **kwargs)
        self.fields['comments_by_assignee'].required = False
        self.fields['revised_completion_date'].required = False


class TaskChatForm(forms.ModelForm):
    """
    Form for sending chat messages for a task
    """
    class Meta:
        model = TaskChat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Type your message...',
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        # Allow passing task and sender optionally during initialization
        self.task = kwargs.pop('task', None)
        self.sender = kwargs.pop('sender', None)
        super(TaskChatForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Override save method to set task and sender
        """
        instance = super(TaskChatForm, self).save(commit=False)
        
        if self.task:
            instance.task = self.task
        if self.sender:
            instance.sender = self.sender
        
        if commit:
            instance.save()
        return instance

    def clean_message(self):
        """
        Validate message content
        """
        message = self.cleaned_data.get('message')
        if not message or len(message.strip()) == 0:
            raise forms.ValidationError("Message cannot be empty.")
        return message