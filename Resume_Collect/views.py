from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.forms.models import model_to_dict
import json
from .decorators import *
from .models import *
from .forms import *
from .utils import *


def Landing(request):
    return render(request, 'Resume_Collect/Landing.html')


@unauthenticated_user
def Register(request):
    form = RegisterUserForm()
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('Collection')
            return redirect('Collection')

    context = {'form': form}
    return render(request, 'Resume_Collect/Register.html', context)


@unauthenticated_user
def Access(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('Collection')
            else:
                messages.error(request, 'Incorrect username or password')

    context = {'form': form}
    return render(request, 'Resume_Collect/Access.html', context)


@login_required(login_url='Access')
@login_required(login_url='Register')
def Collection(request):
    active_user = request.user
    if 'opening' not in request.POST:
        openingform = OpeningForm(request.POST or None)
    if 'candidate' not in request.POST:
        candidateform = CandidateForm(
            request.POST or None, request.FILES or None, user=active_user)
    if 'search' not in request.POST:
        searchform = SearchForm(request.POST or None, user=active_user)
    if 'share' not in request.POST:
        emailform = EmailForm(request.POST or None)
    query = None
    education = None
    if request.method == 'POST':
        if 'opening' in request.POST:
            openingform = OpeningForm(request.POST)
            if openingform.is_valid():
                name = openingform.cleaned_data['name']
                if Opening.objects.filter(name=name, user=active_user).exists():
                    openingform.add_error(
                        'name', 'Job Opening already exists.')
                else:
                    opening = openingform.save(commit=False)
                    opening.user = active_user
                    request.session['opening_id'] = str(opening.id)
                    request.session['opening_name'] = str(opening.name)
                    candidateform = CandidateForm(
                        initial={'opening': opening.id}, files=None)
                    searchform = SearchForm(initial={'opening': opening.id})
                    openingform = OpeningForm(initial={'name': None})
                    opening.save()
                    candidateform = CandidateForm(
                        initial={'opening': opening.id}, user=active_user, files=None)
                    searchform = SearchForm(
                        initial={'opening': opening.id}, user=active_user)
                    openingform = OpeningForm(initial={'name': None})
                    query = None

        if 'candidate' in request.POST:
            candidateform = CandidateForm(
                request.POST, request.FILES, user=active_user)
            if candidateform.is_valid():
                opening = candidateform.cleaned_data.get('opening')
                request.session['opening_id'] = str(opening.id)
                request.session['opening_name'] = str(opening.name)
                for f in request.FILES.getlist('resumes'):
                    text = read_pdf(f)
                    text = remove_null_bytes(text)
                    candidate = extract_candidate(text)
                    Candidate.objects.create(
                        opening=opening,
                        resume=f,
                        name=candidate['name'],
                        phone=candidate['phone'],
                        email=candidate['email'],
                        education=candidate['education'],
                        experience=candidate['experience'],
                        text_list=candidate['text_list'],
                        user=active_user
                    )
                try:
                    current_opening_id = request.session['opening_id']
                except KeyError as error:
                    current_opening_id = None
                query = None
                education = None
                candidateform = CandidateForm(
                initial={'opening': current_opening_id}, user=active_user, files=None)
                searchform = SearchForm(initial={
                                    'opening': current_opening_id, 'query': query, 'education': education}, user=active_user)

        if 'search' in request.POST:
            searchform = SearchForm(request.POST, user=active_user)
            if searchform.is_valid():
                query = searchform.cleaned_data.get('query')
                request.session['query'] = query
                opening = searchform.cleaned_data.get('opening')
                education = searchform.cleaned_data.get('education')
                request.session['education'] = education
                if opening:
                    request.session['opening_id'] = str(opening.id)
                    request.session['opening_name'] = str(opening.name)
                    candidateform = CandidateForm(
                        initial={'opening': opening.id}, user=active_user, files=None)
                    searchform = SearchForm(initial={
                                            'opening': opening.id, 'query': query, 'education': education}, user=active_user)
                else:
                    request.session['opening_id'] = None
                    request.session['opening_name'] = 'All Candidates'
                    searchform = SearchForm(
                        initial={'query': query, 'education': education}, user=active_user)


        if 'delete_candidate' in request.POST:
            candidate_id = request.POST.get('delete_candidate')
            candidate = get_object_or_404(Candidate, id=candidate_id)
            try:
                current_opening_id = request.session['opening_id']
            except KeyError as error:
                current_opening_id = None
            request.session['opening_name'] = str(candidate.opening.name)
            candidate.resume.delete()
            candidate.delete()
            query = request.session.get('query', '')
            education = request.session.get('education', '')
            candidateform = CandidateForm(
                initial={'opening': current_opening_id}, user=active_user, files=None)
            searchform = SearchForm(initial={
                                    'opening': current_opening_id, 'query': query, 'education': education}, user=active_user)


        if 'delete_opening' in request.POST:
            opening_id = request.session.get('opening_id')
            if opening_id:
                opening = get_object_or_404(Opening, id=opening_id)
                opening.delete()
                request.session['opening_id'] = None
                request.session['opening_name'] = None
                query = None

        
        if 'share' in request.POST:
            emailform = EmailForm(request.POST)
            if emailform.is_valid():
                receiver_email = emailform.cleaned_data.get('email')
                name_opening = request.session.get('opening_name')
                if name_opening == 'All Candidates':
                    title = f'All Candidates'
                    message = f'Attached to this email are the resumes of selected candidates for your consideration. (Sent by {request.user.email})'
                else:
                    title = f'{name_opening} candidates'
                    message = f'Attached to this email are the resumes of selected candidates that have applied to the following position: {name_opening}. (Sent by {request.user.email})'
                email = EmailMessage(
                    title,
                    message,
                    'settings.EMAIL_HOST_USER',
                    [receiver_email]
                )
                session_candidate_ids = json.loads(
                    request.session.get('session_candidates'))
                candidates_to_email = Candidate.objects.filter(
                    id__in=session_candidate_ids)
                for each in candidates_to_email:
                    attach_url_to_email(email, each.resume.url)
                email.send()
                try:
                    current_opening_id = request.session['opening_id']
                except KeyError as error:
                    current_opening_id = None
                query = request.session.get('query', '')
                education = request.session.get('education', '')
                candidateform = CandidateForm(
                initial={'opening': current_opening_id}, user=active_user, files=None)
                searchform = SearchForm(initial={
                                    'opening': current_opening_id, 'query': query, 'education': education}, user=active_user)

    opening_id = request.session.get('opening_id')
    opening_name = request.session.get('opening_name')

    if opening_id:
        candidates = Candidate.objects.filter(opening__id=opening_id)
    else:
        opening_name = 'All Candidates'
        candidates = Candidate.objects.filter(user=active_user)
        if len(candidates) == 0:
            opening_name = None

    if query:
        keywords = [word.strip() for word in query.split('&')]
        for keyword in keywords:
            candidates = candidates.filter(text_list__icontains=keyword)
        request.session['query'] = query
    else:
        query = None

    if education:
        candidates = candidates.filter(education__icontains=education)

    opening = Opening.objects.filter(id=opening_id)
    candidates = candidates.order_by('name')

    session_candidate_list = []
    for candidate in candidates:
        session_candidate_list.append(str(candidate.id))

    if request.method == 'GET':
        candidateform = CandidateForm(
            initial={'opening': opening_id}, user=active_user, files=None)
        searchform = SearchForm(
            initial={'opening': opening_id}, user=active_user)


    request.session['session_candidates'] = json.dumps(session_candidate_list)
    total_candidates = candidates.count()
    context = {
        'candidates': candidates,
        'opening': opening,
        'total_candidates': total_candidates,
        'openingform': openingform,
        'candidateform': candidateform,
        'opening_name': opening_name,
        'searchform': searchform,
        'emailform': emailform,
        'query': query
    }

    return render(request, 'Resume_Collect/Collection.html', context)


def Exit(request):
    logout(request)
    return redirect('Access')
