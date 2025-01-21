from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from taggit.managers import TaggableManager

class CommonUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    real_name = models.CharField(max_length=255, default='Joe')
    date_joined_pma = models.DateTimeField(default=timezone.now)
    interests = models.TextField(blank=True)

    def __str__(self):
        return self.email

class Project(models.Model):
    SKILL_LEVEL_CHOICES = [
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
        (5, 'Pro'),
    ]

    SPORT_CHOICES = [
        ('soccer', 'Soccer'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('volleyball', 'Volleyball'),
        ('football', 'Football'),
        ('baseball', 'Baseball'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        null=True,  # Temporarily allow nulls
        blank=True
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ProjectMembership')
    
    skill_level = models.PositiveSmallIntegerField(
        choices=SKILL_LEVEL_CHOICES,
        null=True,
        blank=True,
        help_text="Optional: Indicate the required skill level for the event."
    )
    zip_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Optional: Enter a broad zip code for the event location."
    )
    venue = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional: Specify the venue for the event."
    )

    sport_type = models.CharField(
        max_length=20, 
        choices=SPORT_CHOICES,
        null=True,
        blank=True,
        default=None
    )

    def __str__(self):
        return self.title

class ProjectMembership(models.Model):
    STATUS_CHOICES = (
        ('member', 'Member'),
        ('requested', 'Requested'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='requested')

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f'{self.user.username} - {self.project.title}'

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, default="Untitled File")
    description = models.TextField(blank=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.author.username} on {self.posted_at}'