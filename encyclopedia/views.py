import markdown2
import random
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry_content = util.get_entry(title)

    if entry_content is not None:
        html_content = markdown2.markdown(entry_content)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": "Page not found",
            "content": "The requested page could not be found."
        })


def search(request):
    query = request.GET.get('q')
    entries = util.list_entries()

    exact_match = next((entry for entry in entries if entry.lower() == query.lower()), None)

    if exact_match:
        entry_content = util.get_entry(exact_match)
        html_content = markdown2.markdown(entry_content)
        return render(request, "encyclopedia/entry.html", {
            "title": exact_match,
            "content": html_content
        })
    else: #subtring matches
        substring_matches = [entry for entry in entries if query.lower() in entry.lower()]
        if substring_matches:
            return render(request, "encyclopedia/search_results.html", {
                "query": query,
                "results": substring_matches
            })
        else:
            # no exact matches or substrings
            return render(request, "encyclopedia/error.html", {
                "title": "Search not found",
                "content": "Please, search again"
            })

class NewPageForm(forms.Form):
    title = forms.CharField(
        label="Write the title",
        max_length=100,
        widget=forms.TextInput(attrs={'style': 'display: block;'})
    )
    content = forms.CharField(
        label="Write the content",
        widget=forms.Textarea(attrs={'style': 'max-height: 50vh; max-width: 80%; display: block;'})
    )

def add(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            entries = util.list_entries()

            if title.lower() in [entry.lower() for entry in entries]:
                return render(request, "encyclopedia/error.html", {
                    "title": "Duplicate Entry",
                    "content": "An entry with the same title already exists. Please choose a different title."
                })
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
        else:
            return render(request, "encyclopedia/add.html", {"form": form})
    
    return render(request, "encyclopedia/add.html", {"form": NewPageForm()})

def random_entry(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    entry_content = util.get_entry(random_entry)
    html_content = markdown2.markdown(entry_content)
    return render(request, "encyclopedia/entry.html", {
        "title": random_entry,
        "content": html_content
    })

class EditPageForm(forms.Form):
    content = forms.CharField(
        label="Edit the content",
        widget=forms.Textarea(attrs={'style': 'max-height: 50vh; max-width: 80%; display: block;'})
    )

def edit(request, title):
    entry_content = util.get_entry(title)

    if entry_content is not None:
        if request.method == "POST":
            form = EditPageForm(request.POST)
            if form.is_valid():
                new_content = form.cleaned_data['content']
                util.save_entry(title, new_content)
                return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
        else:
            form = EditPageForm(initial={'content': entry_content})

        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": form
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": "Page not found",
            "content": "The requested page could not be found."
        })