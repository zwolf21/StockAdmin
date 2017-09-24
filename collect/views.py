from pprint import pprint

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView, TemplateView, ListView, DetailView, DeleteView

# from .core import Collect
from .forms import *
from .models import Collect


class CollectCreateView(FormView):
    template_name = 'collect/collect_form.html'
    form_class = CollectFormTest
    success_url = '.'

    def form_valid(self, form):
        c = Collect()
        obj = c.create_collect(**form.cleaned_data)
        c.set_context(obj, test=False)
        c.save(obj)
        return super(CollectCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CollectCreateView, self).get_context_data(**kwargs)
        c = Collect()
        form_data = c.get_form(self.request, auto_on_staturday=True, translate=False)
        if form_data:
            context['form'] = CollectCreateForm(form_data)
        context['object_list'] = c.get_list()        
        return context

def collect_detail(request, slug):
    c = Collect()
    object = c.get_object(slug)
    object_list = c.get_list()
    return render(request, 'collect/collect_detail.html', {'object': object, 'object_list':object_list})

def collect_delete(request, slug):
    # if request.method == "POST":
    c = Collect()
    c.delete(slug)
    return redirect('collect:create')

def clear_collect(request):
    c = Collect()
    c.clear_list()
    return redirect('collect:create')


class CollectListView(ListView):
    
    def get_queryset(self):
        collect = Collect()
        return collect.get_queryset()


class CollectDetailView(DetailView):
    template_name = 'collect/collect_detail.html'

    def get_object(self):
        collect = Collect()
        return collect.get(self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        collect = Collect()
        context = super(CollectDetailView, self).get_context_data(**kwargs)
        context['object_list'] = collect.get_queryset()
        return context

class CollectFormView(FormView):
    template_name = 'collect/collect_form.html'
    success_url = '.'

    def get_form_class(self):
        return get_form_class(test=False, **self.kwargs)

    def form_valid(self, form):
        collect = Collect()
        collect.save(test=False, **form.cleaned_data)
        return super(CollectFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kind = self.kwargs.get('kind')
        collect = Collect()
        context = super(CollectFormView, self).get_context_data(**kwargs)
        context['object_list'] = collect.get_queryset()
        Form = self.get_form_class() 
        form = Form(initial = collect.get_form_initial(kind=kind, types=['ST']))
        context['form'] = form
        # context['form'] = CollectFormTest(initial = collect.get_form_initial(kind=kind, types=['ST']))
        return context



class StaticFormView(FormView):
    template_name = 'collect/static_form.html'
    success_url = '.'
 
    def get_form_class(self):
        return get_form_class(app='static', **self.kwargs)

    def form_valid(self, form):
        collect = Collect()
        collect.save_static(**form.cleaned_data)
        return super(StaticFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(StaticFormView, self).get_context_data(**kwargs)
        collect = Collect()
        Form = self.get_form_class()
        context['form'] = Form(initial=collect.get_static(**self.kwargs))
        return context

class CollectDeleteView(DeleteView):
    # success_url = reverse_lazy('collect:create', args=('LABEl', ))

    def get_success_url(self):
        return reverse_lazy('collect:create', args=('LABEL',))

    def get_object(self):
        collect = Collect()
        return collect.get(self.kwargs.get('slug'))

    def delete(self, request, *args, **kwargs):
        collect = Collect()
        obj = self.get_object()
        collect.delete(obj.slug)
        return super(CollectDeleteView, self).delete(request, *args, **kwargs)


def clear(request):
    if request.method == "POST":
        collect = Collect()
        collect.clear()
    return HttpResponseRedirect(reverse('collect:create', args=('LABEL', )))











