from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Project, ProjectFile, ProjectMembership, ProjectMessage
from .forms import ProjectForm, ProjectFileForm, ProjectMessageForm
from django.utils import timezone

def home(request):
    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def landing_page(request):
    upcoming_events = Project.objects.filter(
        event_date__gte=timezone.now()
    ).order_by('event_date')[:6]
    
    return render(request, 'landing_page.html', {
        'upcoming_events': upcoming_events
    })

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def create_project(request):
    if request.user.is_admin:
        messages.error(request, "Admins cannot create projects.")
        return redirect('project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # Add the owner as a member
            ProjectMembership.objects.create(user=request.user, project=project, status='member')
            messages.success(request, "Event created successfully!")
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_admin:
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('project_list')
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list')
    return render(request, 'delete_project.html', {'project': project})



@login_required
def request_join_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.user.is_admin:
        messages.error(request, "Admins cannot join projects.")
        return redirect('project_list')

    if request.user == project.owner:
        messages.info(request, "You are the owner of this project.")
        return redirect('project_detail', pk=pk)

    membership, created = ProjectMembership.objects.get_or_create(user=request.user, project=project)
    if not created:
        if membership.status == 'member':
            messages.info(request, "You are already a member of this project.")
        elif membership.status == 'requested':
            messages.info(request, "Your join request is already pending approval.")
    else:
        membership.status = 'requested'
        membership.save()
        messages.success(request, "Your request to join has been submitted and is pending approval.")

    return redirect('project_list')


@login_required
def manage_requests(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner:
        return redirect('project_detail', pk=pk)
    join_requests = ProjectMembership.objects.filter(project=project, status='requested')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        membership = get_object_or_404(ProjectMembership, project=project, user_id=user_id)
        if action == 'approve':
            membership.status = 'member'
            membership.save()
        elif action == 'reject':
            membership.delete()
        return redirect('manage_requests', pk=pk)
    return render(request, 'manage_requests.html', {'project': project, 'join_requests': join_requests})

@login_required
def leave_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
    if membership:
        membership.delete()
    return redirect('project_list')

def project_list(request):
    projects = Project.objects.all().order_by('-event_date')
    
    # Get filter parameters
    zip_code = request.GET.get('zip_code')
    sport_type = request.GET.get('sport_type')
    skill_level = request.GET.get('skill_level')
    
    # Apply filters
    if zip_code:
        projects = projects.filter(zip_code=zip_code)
    if sport_type:
        projects = projects.filter(sport_type=sport_type)
    if skill_level:
        projects = projects.filter(skill_level=skill_level)

    if request.user.is_authenticated:
        for project in projects:
            project.user_status = ProjectMembership.objects.filter(
                project=project,
                user=request.user
            ).first()

    context = {
        'projects': projects,
        'anonymous': not request.user.is_authenticated,
        'sport_choices': Project.SPORT_CHOICES,
        'skill_choices': Project.SKILL_LEVEL_CHOICES,
        'zip_code': zip_code,
        'sport_type': sport_type,
        'skill_level': skill_level
    }
    
    return render(request, 'project_list.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
    is_member = membership and membership.status == 'member'
    membership_pending = membership and membership.status == 'requested'

    members = project.members.all()

    if request.method == 'POST' and 'kick_member' in request.POST:
        user_id = request.POST.get('user_id')
        member_to_kick = get_object_or_404(ProjectMembership, project=project, user_id=user_id)

        if member_to_kick.user == request.user:
            messages.error(request, "You cannot kick yourself from the project.")
            return redirect('project_detail', pk=pk)

        if request.user.is_admin or request.user == project.owner:
            # check if the user being kicked is the project owner
            if member_to_kick.user == project.owner:
                # if there are other members, assign a random new owner
                other_members = members.exclude(id=user_id)
                if other_members.exists():
                    new_owner = other_members.order_by('?').first()  # select a random member
                    project.owner = new_owner
                    project.save()
                    messages.info(request, f"{member_to_kick.user.username} has been removed. {new_owner.username} is now the new host.")
                else:
                    # if no other members, delete the project
                    project.delete()
                    messages.success(request, "The last member was removed, so the project has been deleted.")
                    return redirect('project_list')
            else:
                messages.info(request, f"{member_to_kick.user.username} has been removed.")
            member_to_kick.delete()
            return redirect('project_detail', pk=pk)

    if is_member or request.user.is_admin or request.user == project.owner:
        files = project.files.all()
        project_messages = project.messages.all()
    else:
        files = []
        project_messages = []
        members = []  # Clear members list for non-members

    return render(request, 'project_detail.html', {
        'project': project,
        'files': files,
        'messages': project_messages,
        'is_member': is_member,
        'membership_pending': membership_pending,
        'members': members,
    })

@login_required
def upload_file(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    membership = ProjectMembership.objects.filter(
        project=project, 
        user=request.user,
        status='member'
    ).exists()
    
    if not membership and not request.user.is_admin and request.user != project.owner:
        messages.error(request, "You must be an approved member or the project owner to upload files.")
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)

        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.uploaded_by = request.user
            project_file.save()
            
            form.save_m2m()
            
            tags = form.cleaned_data.get('tags')
            if tags:
                # Split tags and add them to the file
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                project_file.tags.set(tag_list)
            
            messages.success(request, "File uploaded successfully!")
            return redirect('project_detail', pk=pk)
        else:
            messages.error(request, "There was an error uploading your file. Please try again.")         
    else:
        form = ProjectFileForm()

    return render(request, 'upload_file.html', {'form': form, 'project': project})


@login_required
def post_message(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    membership = ProjectMembership.objects.filter(
        project=project, 
        user=request.user,
        status='member'
    ).exists()
    
    if not membership and not request.user.is_admin and request.user != project.owner:
        messages.error(request, "You must be an approved member to post messages.")
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.project = project
            message.author = request.user
            message.save()
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectMessageForm()
    return render(request, 'post_message.html', {'form': form, 'project': project})

@login_required
def delete_file(request, pk, file_id):
    project = get_object_or_404(Project, pk=pk)
    project_file = get_object_or_404(ProjectFile, pk=file_id)

    # Check if the user is allowed to delete the file
    if request.user != project_file.uploaded_by and not request.user.is_admin:
        messages.error(request, "You do not have permission to delete this file.")
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        project_file.file.delete()  # Deletes from storage
        project_file.delete()
        messages.success(request, "File deleted successfully.")
        return redirect('project_detail', pk=pk)

    return render(request, 'delete_file.html', {'project': project, 'file': project_file})


def file_metadata(request, file_id):
    try:
        file = get_object_or_404(ProjectFile, id=file_id)
        metadata = {
            'title': file.title,
            'timestamp': file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'description': file.description or "No description available.",
            'tags': [tag.name for tag in file.tags.all()],
        }
        return JsonResponse({'metadata': metadata})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def file_contents(request, file_id):
    try:
        project_file = ProjectFile.objects.get(id=file_id)
        if request.user not in project_file.project.members.all() and request.user != project_file.project.owner:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        content_type = getattr(project_file.file, 'content_type', None)
        if not content_type:
            import mimetypes
            content_type, _ = mimetypes.guess_type(project_file.file.name)
            content_type = content_type or 'application/octet-stream'

        # Handle PDF files
        if content_type == 'application/pdf':
            return JsonResponse({
                'type': 'pdf',
                'url': project_file.file.url  # Assuming you're using S3 or similar storage
            })

        # Handle text files
        if content_type.startswith('text/') or content_type in ['application/json', 'application/xml']:
            with default_storage.open(project_file.file.name, 'rb') as file:
                try:
                    text_content = file.read().decode('utf-8')
                    return JsonResponse({
                        'type': 'text',
                        'content': text_content
                    })
                except UnicodeDecodeError:
                    return JsonResponse({'error': 'File is not readable as text'}, status=400)

        # Handle images
        if content_type.startswith('image/'):
            with default_storage.open(project_file.file.name, 'rb') as file:
                import base64
                image_b64 = base64.b64encode(file.read()).decode('utf-8')
                return JsonResponse({
                    'type': 'image',
                    'content': f"data:{content_type};base64,{image_b64}"
                })

        return JsonResponse({
            'error': f'Unsupported file type: {content_type}'
        }, status=400)

    except ProjectFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)